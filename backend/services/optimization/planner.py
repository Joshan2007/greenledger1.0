"""
GreenLedger - Safety-constrained optimization planner.
Ranks approved laptop power actions by predicted watt reduction, confidence,
and local device learning from verified before/after trials.
"""

import hashlib
from copy import deepcopy
from typing import Any, Dict, List

from schemas.models import OptimizationRecommendation
from services.ml.inference import ml_engine
from services.optimization.trial_store import trial_store

OPTIMIZABLE_PROCESS_NAMES = {
    "chrome.exe", "msedge.exe", "firefox.exe", "brave.exe", "opera.exe",
    "spotify.exe", "discord.exe", "slack.exe", "teams.exe", "zoom.exe",
    "steam.exe", "epicgameslauncher.exe", "dropbox.exe", "onedrive.exe",
    "onedrive.sync.service.exe", "notion.exe", "figma.exe"
}


def device_fingerprint(telemetry: Dict[str, Any]) -> str:
    raw = "|".join(
        str(telemetry.get(key) or "")
        for key in ("gpu_name", "memory_total_gb", "cpu_logical_cores", "cpu_physical_cores")
    )
    if not raw.strip("|"):
        raw = "unknown-device"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _predict_watts(telemetry: Dict[str, Any]) -> float:
    prediction = ml_engine.predict_power(telemetry)
    return float(prediction["estimated_power_w"])


def _estimate_counterfactual(before: Dict[str, Any], changes: Dict[str, Any]) -> float:
    candidate = deepcopy(before)
    for key, value in changes.items():
        if callable(value):
            candidate[key] = value(candidate.get(key))
        else:
            candidate[key] = value
    return _predict_watts(candidate)


def _with_learning(
    recommendation: OptimizationRecommendation,
    telemetry: Dict[str, Any],
    predicted_watts_saved: float,
) -> OptimizationRecommendation:
    summary = trial_store.summarize_action(recommendation.id, device_fingerprint(telemetry))
    trial_count = int(summary["trial_count"])
    avg_watts = summary["avg_watts_saved"]

    blended_watts = predicted_watts_saved
    confidence = recommendation.confidence or 0.45
    rationale = recommendation.rationale or "Ranked from current telemetry and expected workload impact."

    if avg_watts is not None:
        # Weight local verified evidence more heavily as repeated trials accumulate.
        local_weight = min(0.65, 0.18 * trial_count)
        blended_watts = (predicted_watts_saved * (1.0 - local_weight)) + (float(avg_watts) * local_weight)
        confidence = min(0.92, confidence + min(0.28, 0.06 * trial_count))
        rationale = f"{rationale} Local history shows {avg_watts} W average verified savings."

    before_w = max(1.0, _predict_watts(telemetry))
    recommendation.estimated_watts_saved = round(max(0.0, blended_watts), 2)
    recommendation.estimated_power_reduction_pct = round(max(0.0, blended_watts) / before_w * 100.0, 2)
    recommendation.confidence = round(confidence, 2)
    recommendation.learned_from_trials = trial_count
    recommendation.rationale = rationale
    return recommendation


class OptimizationPlannerService:
    def plan(self, telemetry: Dict[str, Any]) -> List[OptimizationRecommendation]:
        before_w = _predict_watts(telemetry)
        recommendations: List[OptimizationRecommendation] = []

        active_scheme = str(telemetry.get("active_power_scheme") or "").lower()
        if "power saver" not in active_scheme and "a1841308" not in active_scheme:
            after_w = _estimate_counterfactual(telemetry, {
                "cpu_utilization": lambda v: max(0.0, float(v or 0.0) * 0.92),
                "cpu_frequency": lambda v: float(v) * 0.88 if v else v,
                "temperature": lambda v: max(25.0, float(v or 45.0) - 2.0),
            })
            recommendations.append(_with_learning(
                OptimizationRecommendation(
                    id="enable_power_saver",
                    title="Enable Windows Energy Saver Profile",
                    category="power_plan",
                    priority="high",
                    reversible=True,
                    description="Switches to the Windows Power Saver plan and verifies the actual watt reduction afterward.",
                    action_name="Switch Power Plan",
                    confidence=0.68,
                    safety_level="reversible",
                    rationale="CPU frequency and temperature indicate potential savings from lower boost behavior."
                ),
                telemetry,
                before_w - after_w,
            ))

        brightness = telemetry.get("display_brightness")
        if isinstance(brightness, (int, float)) and brightness > 55:
            estimated = min(4.5, max(0.8, (float(brightness) - 45.0) * 0.055))
            recommendations.append(_with_learning(
                OptimizationRecommendation(
                    id="reduce_display_brightness",
                    title="Reduce Display Brightness",
                    category="display",
                    priority="medium" if estimated < 2.5 else "high",
                    reversible=True,
                    description="Lowers screen brightness by a small reversible step; display power is often one of the largest laptop loads.",
                    action_name="Dim Display",
                    confidence=0.72,
                    safety_level="reversible",
                    rationale=f"Brightness is currently reported at {round(float(brightness), 1)}%."
                ),
                telemetry,
                estimated,
            ))

        top_procs = telemetry.get("top_cpu_processes") or []
        for proc in top_procs:
            name = str(proc.get("name") or "Application")
            lower_name = name.lower()
            proc_cpu = float(proc.get("cpu_percent") or 0.0)
            if lower_name not in OPTIMIZABLE_PROCESS_NAMES or proc_cpu < 8.0:
                continue
            after_w = _estimate_counterfactual(telemetry, {
                "cpu_utilization": lambda v, cpu=proc_cpu: max(0.0, float(v or 0.0) - min(cpu * 0.65, 18.0)),
                "memory_usage": lambda v: max(0.0, float(v or 0.0) - 1.5),
                "process_count": lambda v: max(1, int(v or 1) - 1),
            })
            recommendations.append(_with_learning(
                OptimizationRecommendation(
                    id=f"close_process_{proc.get('pid')}",
                    title=f"Close High-Load App: {name}",
                    category="process_management",
                    priority="high" if proc_cpu >= 18 else "medium",
                    reversible=False,
                    description=f"{name} is using {round(proc_cpu, 1)}% CPU. Closing it may reduce active CPU wakeups.",
                    action_name=f"Close {name}",
                    pid=proc.get("pid"),
                    process_name=name,
                    cpu_percent=proc_cpu,
                    memory_percent=proc.get("memory_percent", 0.0),
                    confidence=0.62,
                    safety_level="user_approved",
                    rationale="Process-level CPU use is the most direct safe optimization signal available."
                ),
                telemetry,
                before_w - after_w,
            ))

        recommendations.sort(
            key=lambda rec: (
                rec.estimated_watts_saved or 0.0,
                rec.confidence or 0.0,
            ),
            reverse=True,
        )
        return recommendations[:6]


optimization_planner = OptimizationPlannerService()
