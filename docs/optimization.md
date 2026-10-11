# Optimization Engine & System Safety Documentation

## Overview
The GreenLedger optimization engine translates hardware telemetry into ranked, non-destructive efficiency interventions.

---

## Safety Guardrails & Blacklist
GreenLedger enforces strict non-negotiable safety guardrails:
1. **Never Kills System Processes**: `explorer.exe`, `svchost.exe`, `dwm.exe`, `csrss.exe`, `lsass.exe`, and antivirus services (`msmpeng.exe`, `securityhealthservice.exe`) are blacklisted from termination.
2. **Reversible Actions**: Windows power scheme adjustments and EcoQoS process throttling record prior scheme GUIDs and process priority/affinity masks for instant rollback.
3. **No Arbitrary Shell Execution**: The agent exposes strictly enumerated action IDs; arbitrary terminal command strings sent from the web client are rejected.

---

## Available Optimization Actions

### 1. Windows Energy Saver Profile (`enable_power_saver`)
- **Action**: Activates Windows Power Saver scheme using `powercfg /setactive a1841308-3541-4fab-bc81-f71556f20b4a`.
- **Effect**: Curbs dynamic core voltage spikes, limits background telemetry, and reduces idle wattage by 10-15%.
- **Reversible**: Yes (`undo` restores original power plan).

### 2. Windows 11 EcoQoS & Hybrid E-Core Throttling (`eco_throttle_process_<pid>`) [Novelty]
- **Action**: Invokes native Win32 `SetProcessInformation(ProcessPowerThrottling)` API, demotes priority class to `BELOW_NORMAL_PRIORITY_CLASS`, and locks thread affinity to low-power Efficiency Cores (E-cores).
- **Effect**: Reduces active CPU core voltage and boost clock spikes without killing the application (zero user disruption; cloud sync and tabs remain active).
- **Safety**: Strictly constrained to user-space candidate applications.
- **Reversible**: Yes (`undo` restores standard priority and full CPU core affinity mask).

### 3. Graceful Process Suspension (`close_process_<pid>`) [Legacy Fallback]
- **Action**: Sends `SIGTERM` to high-draw user processes (e.g. background Chrome, Spotify, Discord, Slack).
- **Safety**: Only applies to non-system user-space applications.
- **Reversible**: Manual application relaunch.

### 4. Memory Working Set Trim (`trim_working_sets`)
- **Action**: Flushes Python caches and signals the Windows memory manager to release stale working set pages.
