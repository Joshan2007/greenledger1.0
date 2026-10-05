# 5-Minute Hackathon Demo Script for Judges

## Quick Pitch Outline (5 Minutes)

### Minute 1: The Hook & Landing Page
- **Say**: "Laptops consume significant electricity even when idle, yet operating systems provide no universal Watt meter. GreenLedger bridges Windows 11 hardware counters to machine-learning power inference and verified optimization."
- **Action**: Show landing page, highlight 3D Energy Core and the 6-step loop. Click **"Launch Dashboard"**.

### Minute 2: Real-Time Telemetry & AI Inference
- **Say**: "Here is the live dashboard. Notice the separation: this is **Estimated Power** computed via our trained XGBoost model ($R^2: 0.975$, MAE: $0.96\text{ W}$), alongside our **Carbon Footprint** in grams of $\text{CO}_2\text{e}$ per hour."
- **Action**: Point out the live telemetry cards (CPU, RAM, GPU, Disk, Network) and the ML explanation panel explaining why wattage is elevated.

### Minute 3: Safe Optimization Execution
- **Say**: "GreenLedger identifies non-destructive optimizations. Notice our strict safety rules: we never touch system services or delete files."
- **Action**: Click **"Tune System"** or **"Optimize"**. Confirm the safe action (e.g. Windows Power Saver Profile).
- **Show**: Watch the Before vs. After comparison card report the measured power and carbon delta without claiming a reduction when the trial does not verify one.

### Minute 4: Device-Specific Learning
- **Say**: "Every completed trial is measured locally. GreenLedger learns which actions genuinely save power on this specific laptop and updates recommendation confidence."
- **Action**: Show the recommendation confidence, local trial count, and measured before/after result.

### Minute 5: Safety, Evidence, and Novelty
- **Say**: "The optimizer is consent-based, reversible, device-adaptive, and honest about estimated versus measured power."
- **Action**: Show protected processes, rollback support, ML diagnostics, and the local optimization history.
- **Wrap up**: "This completes the loop from Windows telemetry to machine learning, safe action, measured verification, and device-specific improvement."
