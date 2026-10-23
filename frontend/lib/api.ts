/**
 * GreenLedger - API Client
 * Manages dual connectivity: Local Windows Telemetry Agent (http://127.0.0.1:8765)
 * and Cloud / Local FastAPI Backend (http://127.0.0.1:8000).
 */

import { TelemetryData, PredictionResult, OptimizationOpportunity, BeforeAfterResult, UserCreditState, GridState, AIGovernorStatus } from "../types";

export const AGENT_BASE_URL = process.env.NEXT_PUBLIC_LOCAL_AGENT_URL || "http://127.0.0.1:8765";
export const BACKEND_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

/**
 * Checks if the local Windows agent daemon is running.
 */
export async function checkAgentHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${AGENT_BASE_URL}/health`, { 
      method: "GET",
      signal: AbortSignal.timeout(1200) 
    });
    return res.ok;
  } catch {
    return false;
  }
}

/**
 * Fetches latest telemetry from the local Windows agent only.
 */
export async function fetchTelemetry(): Promise<TelemetryData> {
  try {
    const res = await fetch(`${AGENT_BASE_URL}/telemetry`, {
      signal: AbortSignal.timeout(6000)
    });
    if (res.ok) {
      const data = await res.json();
      return { ...data, is_live: true, mode_label: "Live Windows device telemetry" };
    }
  } catch {
    // Report the unavailable state to the page without inventing measurements.
  }
  throw new Error("Live Windows telemetry unavailable: start the local agent.");
}

/**
 * Calls XGBoost ML Inference Engine for honest power estimation.
 */
export async function predictPower(telemetry: TelemetryData): Promise<PredictionResult> {
  try {
    const res = await fetch(`${BACKEND_BASE_URL}/api/ml/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(telemetry),
      signal: AbortSignal.timeout(6000)
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (e) {
    console.warn("ML predict network error, using physics baseline:", e);
  }

  throw new Error("Power estimate unavailable: backend ML service is unreachable.");
}

/**
 * Fetches optimization opportunities for current system state.
 */
export async function fetchRecommendations(telemetry: TelemetryData, isAgentLive: boolean): Promise<OptimizationOpportunity[]> {
  try {
    const res = await fetch(`${BACKEND_BASE_URL}/api/optimization/recommendations`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(telemetry),
      signal: AbortSignal.timeout(6000)
    });
    if (res.ok) {
      return await res.json();
    }
  } catch {}

  if (isAgentLive) {
    try {
      const res = await fetch(`${AGENT_BASE_URL}/optimization/recommendations`, {
        signal: AbortSignal.timeout(5000)
      });
      if (res.ok) {
        return await res.json();
      }
    } catch {
      // Fallback
    }
  }

  throw new Error("Optimization recommendations unavailable: agent and backend are unreachable.");
}

/**
 * Executes safe optimization action.
 */
export async function executeOptimizationAction(actionId: string, params?: any, isAgentLive: boolean = false): Promise<boolean> {
  if (isAgentLive) {
    try {
      const res = await fetch(`${AGENT_BASE_URL}/optimization/execute`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action_id: actionId, params })
      });
      return res.ok;
    } catch {
      return false;
    }
  }
  return false;
}

/**
 * Evaluates before/after optimization impact and calculates green credit rewards.
 */
export async function evaluateOptimizationDelta(
  actionId: string,
  before: TelemetryData,
  after: TelemetryData,
  userId: string = "default_user"
): Promise<BeforeAfterResult> {
  try {
    const res = await fetch(`${BACKEND_BASE_URL}/api/optimization/evaluate-delta`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        action_id: actionId,
        before_telemetry: before,
        after_telemetry: after,
        user_id: userId
      })
    });
    if (res.ok) {
      return await res.json();
    }
  } catch {}

  throw new Error("Optimization result unavailable: backend verification service is unreachable.");
}

/**
 * Fetches user credit state, streak, and recent history.
 */
export async function fetchCreditState(userId: string = "default_user"): Promise<UserCreditState> {
  try {
    const res = await fetch(`${BACKEND_BASE_URL}/api/credits/state?user_id=${userId}`);
    if (res.ok) {
      return await res.json();
    }
  } catch {}

  throw new Error("Credit state unavailable: backend is unreachable.");
}

/**
 * Fetches real-time electricity grid carbon intensity and renewable status (Novelty 2).
 */
export async function fetchGridIntelligence(): Promise<GridState | null> {
  try {
    const res = await fetch(`${BACKEND_BASE_URL}/api/carbon/grid`);
    if (res.ok) {
      return await res.json();
    }
  } catch {}
  return null;
}

/**
 * Switches the active regional electricity grid zone.
 */
export async function switchGridZone(zone: string): Promise<GridState | null> {
  try {
    const res = await fetch(`${BACKEND_BASE_URL}/api/carbon/grid/select`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ zone })
    });
    if (res.ok) {
      const data = await res.json();
      return data.active_grid;
    }
  } catch {}
  return null;
}

/**
 * Fetches status of local AI / LLM Power Governor (Novelty 4).
 */
export async function fetchAIGovernorStatus(): Promise<AIGovernorStatus | null> {
  try {
    const res = await fetch(`${AGENT_BASE_URL}/ai/status`, {
      signal: AbortSignal.timeout(6000)
    });
    if (res.ok) {
      return await res.json();
    }
  } catch {}
  return null;
}

/**
 * Changes dynamic AI Energy Budget Mode (eco, balanced, turbo).
 */
export async function setAIGovernorMode(mode: 'eco' | 'balanced' | 'turbo'): Promise<boolean> {
  try {
    const res = await fetch(`${AGENT_BASE_URL}/ai/mode`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mode })
    });
    return res.ok;
  } catch {
    return false;
  }
}
