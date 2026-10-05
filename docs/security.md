# Security & Telemetry Boundary Policy

## Core Tenets
1. **No Sensitive Telemetry Upload**: We do not capture personal files, keyboard inputs, browser histories, passwords, or document metadata.
2. **Strict Whitelists**: The agent only interacts with whitelisted Windows performance counters and well-defined user applications.
3. **Protected OS Services**: Windows critical binaries (`explorer.exe`, `svchost.exe`, `dwm.exe`, antivirus) cannot be terminated or targeted by optimization routines.
4. **Local Trial Storage**: Optimization evidence remains in a local SQLite database and is excluded from source control.
5. **CORS Security**: Cross-Origin Resource Sharing is scoped and parameterized.
