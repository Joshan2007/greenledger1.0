"""
GreenLedger - Windows System Safe Optimization Engine
Executes verified, reversible, user-approved optimizations adhering to strict safety guardrails.
NEVER kills system services, deletes user files, or modifies security settings.
"""

import subprocess
import logging
from typing import Dict, Any, List, Optional
import psutil

from config import POWER_SCHEMES, PROTECTED_PROCESSES, OPTIMIZABLE_PROCESS_CANDIDATES

logger = logging.getLogger("GreenLedger.Optimizer")


class WindowsOptimizer:
    def __init__(self):
        self._applied_actions: List[Dict[str, Any]] = []
        self._original_power_scheme: Optional[str] = None
        self._original_brightness: Optional[int] = None
        self._detect_initial_power_scheme()

    def _detect_initial_power_scheme(self):
        """Reads current active Windows power plan scheme GUID."""
        try:
            res = subprocess.run(["powercfg", "/getactivescheme"], capture_output=True, text=True)
            if res.returncode == 0:
                output = res.stdout.strip()
                for key, guid in POWER_SCHEMES.items():
                    if guid.lower() in output.lower():
                        self._original_power_scheme = guid
                        return
            self._original_power_scheme = POWER_SCHEMES["balanced"]
        except Exception as e:
            logger.warning(f"Could not query active power scheme: {e}")
            self._original_power_scheme = POWER_SCHEMES["balanced"]

    def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """
        Scans current live system state and returns a ranked list of safe,
        explainable optimization opportunities.
        """
        recommendations = []
        
        # 1. Check Windows Power Plan
        try:
            res = subprocess.run(["powercfg", "/getactivescheme"], capture_output=True, text=True)
            is_power_saver = POWER_SCHEMES["power_saver"].lower() in res.stdout.lower()
            if not is_power_saver:
                recommendations.append({
                    "id": "enable_power_saver",
                    "title": "Enable Windows Energy Saver Mode",
                    "category": "power_plan",
                    "priority": "high",
                    "estimated_power_reduction_pct": 4.0,
                    "estimated_watts_saved": 1.5,
                    "confidence": 0.62,
                    "rationale": "Power Saver is a reversible Windows setting that can reduce CPU boost behavior and background activity.",
                    "safety_level": "reversible",
                    "learned_from_trials": 0,
                    "reversible": True,
                    "description": "Switches the Windows energy scheme to Power Saver to reduce CPU clock throttling floor and background synchronization.",
                    "action_name": "Switch Power Plan"
                })
        except Exception:
            pass

        # 2. Display brightness when exposed by Windows WMI
        try:
            read_cmd = "(Get-CimInstance -Namespace root/WMI -ClassName WmiMonitorBrightness | Select-Object -First 1 CurrentBrightness).CurrentBrightness"
            res = subprocess.run(["powershell", "-NoProfile", "-Command", read_cmd], capture_output=True, text=True, timeout=1.2)
            if res.returncode == 0 and res.stdout.strip():
                brightness = int(float(res.stdout.strip().splitlines()[-1]))
                if brightness > 55:
                    recommendations.append({
                        "id": "reduce_display_brightness",
                        "title": "Reduce Display Brightness",
                        "category": "display",
                        "priority": "medium",
                        "estimated_power_reduction_pct": 3.0,
                        "estimated_watts_saved": round(min(4.5, max(0.8, (brightness - 45.0) * 0.055)), 2),
                        "confidence": 0.72,
                        "rationale": f"Brightness is currently {brightness}%; display power is a direct laptop energy load.",
                        "safety_level": "reversible",
                        "learned_from_trials": 0,
                        "reversible": True,
                        "description": "Lowers screen brightness by a small reversible step and verifies the impact afterward.",
                        "action_name": "Dim Display"
                    })
        except Exception:
            pass

        # 3. Inspect Running Processes for High-Resource Non-System Candidates
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                name = (p.info['name'] or "").lower()
                pid = p.info['pid']
                cpu_p = p.info.get('cpu_percent') or 0.0
                mem_p = p.info.get('memory_percent') or 0.0

                if name in PROTECTED_PROCESSES or name not in OPTIMIZABLE_PROCESS_CANDIDATES:
                    continue

                # Check if it is a notable resource consumer or background app
                if name in OPTIMIZABLE_PROCESS_CANDIDATES and (cpu_p > 8.0 or mem_p > 10.0):
                    recommendations.append({
                        "id": f"close_process_{pid}",
                        "title": f"Suspend High-Load Application: {p.info['name']}",
                        "category": "process_management",
                        "priority": "medium" if cpu_p < 15.0 else "high",
                        "pid": pid,
                        "process_name": p.info['name'],
                        "cpu_percent": round(cpu_p, 1),
                        "memory_percent": round(mem_p, 1),
                        "estimated_power_reduction_pct": round(min(20.0, max(2.0, cpu_p * 0.45)), 1),
                        "estimated_watts_saved": round(min(8.0, max(0.8, cpu_p * 0.22)), 2),
                        "confidence": 0.64,
                        "rationale": "This user-space process is consuming CPU and is on the safe optimization candidate list.",
                        "safety_level": "user_approved",
                        "learned_from_trials": 0,
                        "reversible": False,
                        "description": f"Application '{p.info['name']}' is consuming {cpu_p:.1f}% CPU and {mem_p:.1f}% RAM in background.",
                        "action_name": f"Close {p.info['name']}"
                    })
                    if len(recommendations) >= 5:
                        break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return recommendations

    def execute_action(self, action_id: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Safely executes an approved optimization action with strict validation.
        """
        logger.info(f"Executing approved action: {action_id}")
        
        # Action 1: Switch to Power Saver Plan
        if action_id == "enable_power_saver":
            guid = POWER_SCHEMES["power_saver"]
            cmd = ["powercfg", "/setactive", guid]
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0:
                self._applied_actions.append({
                    "action_id": action_id,
                    "type": "power_scheme",
                    "previous_value": self._original_power_scheme
                })
                return {"success": True, "message": "Windows Energy Saver profile successfully activated."}

            fallback_cmds = [
                ["powercfg", "/setdcvalueindex", "SCHEME_CURRENT", "SUB_ENERGYSAVER", "ESBATTTHRESHOLD", "100"],
                ["powercfg", "/setacvalueindex", "SCHEME_CURRENT", "SUB_ENERGYSAVER", "ESBATTTHRESHOLD", "100"],
                ["powercfg", "/setactive", "SCHEME_CURRENT"],
            ]
            fallback_errors = []
            for fallback in fallback_cmds:
                fb_res = subprocess.run(fallback, capture_output=True, text=True)
                if fb_res.returncode != 0:
                    fallback_errors.append(fb_res.stderr.strip() or f"exit {fb_res.returncode}")
            if not fallback_errors:
                self._applied_actions.append({
                    "action_id": action_id,
                    "type": "energy_saver_settings",
                    "previous_value": self._original_power_scheme
                })
                return {"success": True, "message": "Windows Energy Saver settings enabled on the current power scheme."}

            return {"success": False, "error": f"Power Saver plan unavailable and fallback failed: {'; '.join(fallback_errors)}"}

        # Action 2: Reduce display brightness by a small reversible step
        if action_id == "reduce_display_brightness":
            try:
                read_cmd = "(Get-CimInstance -Namespace root/WMI -ClassName WmiMonitorBrightness | Select-Object -First 1 CurrentBrightness).CurrentBrightness"
                current = subprocess.run(
                    ["powershell", "-NoProfile", "-Command", read_cmd],
                    capture_output=True,
                    text=True,
                    timeout=1.5
                )
                if current.returncode != 0 or not current.stdout.strip():
                    return {"success": False, "error": "Display brightness is not exposed by this Windows device."}

                current_brightness = int(float(current.stdout.strip().splitlines()[-1]))
                if self._original_brightness is None:
                    self._original_brightness = current_brightness
                target = max(35, current_brightness - 15)
                set_cmd = f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{target})"
                res = subprocess.run(
                    ["powershell", "-NoProfile", "-Command", set_cmd],
                    capture_output=True,
                    text=True,
                    timeout=1.5
                )
                if res.returncode == 0:
                    self._applied_actions.append({
                        "action_id": action_id,
                        "type": "display_brightness",
                        "previous_value": current_brightness,
                        "new_value": target
                    })
                    return {"success": True, "message": f"Display brightness reduced from {current_brightness}% to {target}%."}
                return {"success": False, "error": f"Brightness adjustment failed: {res.stderr}"}
            except Exception as e:
                return {"success": False, "error": str(e)}

        # Action 3: Graceful Close of Specific User Application
        if action_id.startswith("close_process_"):
            try:
                requested_pid = int(action_id.replace("close_process_", ""))
            except ValueError:
                return {"success": False, "error": "Invalid process optimization action ID."}
            if params and params.get("pid") is not None and int(params["pid"]) != requested_pid:
                return {"success": False, "error": "Process ID does not match the approved action."}
            pid = requested_pid
            try:
                proc = psutil.Process(pid)
                pname = proc.name().lower()
                
                # Strict security guardrail
                if pname in PROTECTED_PROCESSES or pid <= 4:
                    return {"success": False, "error": f"Security violation: Process '{pname}' (PID {pid}) is a protected system service."}

                # Graceful termination request (SIGTERM)
                proc.terminate()
                try:
                    proc.wait(timeout=2.0)
                except psutil.TimeoutExpired:
                    return {"success": False, "error": f"Process PID {pid} did not exit after graceful request; no force kill performed."}

                self._applied_actions.append({
                    "action_id": action_id,
                    "type": "process_terminate",
                    "name": pname,
                    "pid": pid
                })
                return {"success": True, "message": f"Application '{pname}' (PID {pid}) safely closed."}
            except psutil.NoSuchProcess:
                return {"success": True, "message": f"Process PID {pid} was already closed."}
            except psutil.AccessDenied:
                return {"success": False, "error": f"Access denied terminating process PID {pid}."}
            except Exception as e:
                return {"success": False, "error": str(e)}

        return {"success": False, "error": f"Unknown or unsupported action ID: '{action_id}'"}

    def undo_action(self, action_id: str) -> Dict[str, Any]:
        """
        Reverses an optimization action where technically possible.
        """
        logger.info(f"Reversing action: {action_id}")
        
        if action_id == "enable_power_saver":
            restore_guid = self._original_power_scheme or POWER_SCHEMES["balanced"]
            res = subprocess.run(["powercfg", "/setactive", restore_guid], capture_output=True, text=True)
            if res.returncode == 0:
                return {"success": True, "message": "Windows power scheme restored to previous setting."}
            return {"success": False, "error": f"Failed to restore power plan: {res.stderr}"}

        if action_id == "reduce_display_brightness":
            if self._original_brightness is None:
                return {"success": False, "error": "No previous brightness value is available to restore."}
            set_cmd = f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{self._original_brightness})"
            res = subprocess.run(["powershell", "-NoProfile", "-Command", set_cmd], capture_output=True, text=True, timeout=1.5)
            if res.returncode == 0:
                return {"success": True, "message": f"Display brightness restored to {self._original_brightness}%."}
            return {"success": False, "error": f"Failed to restore brightness: {res.stderr}"}
            
        return {"success": False, "error": f"Action '{action_id}' is not reversible or has no undo state."}


# Global singleton instance
optimizer_instance = WindowsOptimizer()
