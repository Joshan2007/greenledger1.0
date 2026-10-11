# Carbon Footprint Calculation & Conversion Methodology

## Conversion Formulas
GreenLedger converts predicted electrical wattage into standard units of carbon equivalent ($g\ CO_2e$):

$$\text{Energy (kWh)} = \left(\frac{\text{Power (Watts)}}{1000}\right) \times \text{Duration (Hours)}$$

$$\text{Emissions } (kg\ CO_2e) = \text{Energy (kWh)} \times \text{Carbon Intensity } \left(\frac{kg\ CO_2e}{kWh}\right)$$

$$\text{Emissions } (g\ CO_2e) = \text{Emissions } (kg\ CO_2e) \times 1000$$

---

## Novelty 2: Real-Time Dynamic Grid Carbon Shifting & Temporal Orchestration

Rather than relying purely on static national averages, GreenLedger incorporates a live **Dynamic Grid Carbon Intelligence Service**:

1. **Live Marginal Grid Feeds & Geo-Location**:
   - Auto-detects local regional electrical grid zone (e.g. India Southern Regional Grid `IN-SR`, California CAISO `US-CAISO`, UK National Grid ESO Live `GB-NATIONAL`, etc.).
   - Connects to real-time grid telemetry and diurnal renewable generation models.

2. **Diurnal Solar & Peaker Plant Curve Modeling**:
   - **Midday Solar Peak Window** (11:00 AM – 3:00 PM): High solar generation reduces local marginal intensity by up to 35%. GreenLedger flags this as the *"Clean Renewable Window"* for heavy batch tasks (model training, backup syncing).
   - **Evening Peaker Peak Alert** (6:00 PM – 10:00 PM): High demand activates fossil-fuel peaker plants, surging intensity by +22%. GreenLedger triggers a high-priority *"Grid Shield"* recommendation to defer compute and awards a **1.8x Green Credit Multiplier** for optimizations during dirty hours.

3. **Incentive Multiplier Formula**:
   $$\text{Verified Credits} = \text{Base Credits} \times \text{Grid Carbon Multiplier}$$

---

## Regional Grid Emission Baseline Factors

| Region | Base Factor ($kg\ CO_2e / kWh$) | Authority / Source | Live Support |
|---|---|---|---|
| **India (Southern Grid - SR)** | `0.680` | Central Electricity Authority (CEA) / SRPC | ✅ Diurnal Model |
| **India (National Grid)** | `0.710` | Central Electricity Authority (CEA) | ✅ Diurnal Model |
| **USA (California CAISO)** | `0.260` | California ISO Hourly Duck Curve | ✅ Diurnal Model |
| **USA (eGRID National)** | `0.385` | US EPA eGRID Average | ✅ Baseline |
| **United Kingdom** | `0.165` | National Grid ESO Live API | ✅ Live API Feed |
| **Germany** | `0.348` | Umweltbundesamt (UBA) / Agora | ✅ Diurnal Model |
| **Nordic Hydro/Nuclear** | `0.045` | Nordic Clean Energy Baseline | ✅ Always Clean |

---

## Environmental Equivalencies
- **Mature Tree Offset**: One mature tree absorbs approximately $21,770\ g\ CO_2$ per year ($59.64\ g\ CO_2/\text{day}$).
- **Passenger Vehicle Mileage**: An average passenger car emits approximately $120\ g\ CO_2/\text{km}$.
