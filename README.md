# Real-Time Classroom Sensor Streaming & Analytics

A real-time data analytics pipeline developed for RTDA&DM (Assignment 2). This project simulates an IoT sensor data feed over WebSockets, processes and cleans the streaming data in real time, engineers environmental and efficiency features, and generates analytical summaries and visualizations.

---

## Architecture & Workflow

```text
[dataset.csv] ──> [server.py (WebSocket Server: 1234)]
                          │  (Streams row-by-row with 1s delay)
                          ▼
                  [main.py (Client / Consumer)]
                          │
         ┌────────────────┴────────────────┐
         ▼                                 ▼
[Real-Time Cleaning]              [Feature Engineering]
 • Linear Interpolation (Temp/CO2) • 3-period rolling averages
 • Forward Fill (Occupancy)        • Occupancy density & Energy/student
                                   • Comfort index flag
                          │
         ┌────────────────┴────────────────┐
         ▼                                 ▼
[cleaned_classroom_data.csv]      [classroom_analysis_plots.png]
 (Exported cleaned dataset)        (Dual-axis time series charts)
```

---

## File Structure

```text
src/
├── dataset.csv                   # Raw sensor observations (contains nulls/missing values)
├── server.py                     # WebSocket server simulating IoT stream (ws://localhost:1234)
├── main.py                       # Client pipeline: consumer, cleaner, feature engineering, visualizer
├── cleaned_classroom_data.csv    # Final processed dataset with engineered features
├── classroom_analysis_plots.png  # Generated analytical charts
└── README.md                     # Project documentation
```

---

## Pipeline Features

1. **WebSocket Telemetry Stream (`server.py`)**:
   - Reads [dataset.csv](file:///home/ami-ka/Projects/01_courses/RTDA&DM/assignment2/src/dataset.csv) and streams records as JSON payloads every 1 second.
   - Emits a completion sentinel `{"status": "EOF"}` when transmission ends.

2. **Real-Time Data Processing (`main.py`)**:
   - **Missing Value Imputation**: Linear interpolation for missing temperature (`Temp_C`) and carbon dioxide (`CO2_ppm`); forward-fill for missing `Occupancy`.
   - **Rolling Aggregations**: 3-step rolling means for `Temp_C`, `CO2_ppm`, and `Power_kW`.
   - **Feature Engineering**:
     - `occupancy_density`: Ratio of occupancy to classroom capacity (40).
     - `energy_per_student`: Power consumption per student (`Power_kW / Occupancy`).
     - `comfort_flag`: Boolean flag indicating ideal indoor climate (`CO2 <= 1000 ppm` and `20°C <= Temp <= 24°C`).

3. **Analytics & Output**:
   - Summarizes temperature statistics (mean, median, min, max) and CO2 levels.
   - Identifies peak power demand and calculates occupancy vs. power correlation.
   - Exports the processed dataset to [cleaned_classroom_data.csv](file:///home/ami-ka/Projects/01_courses/RTDA&DM/assignment2/src/cleaned_classroom_data.csv).
   - Generates two-panel time-series plots saved to [classroom_analysis_plots.png](file:///home/ami-ka/Projects/01_courses/RTDA&DM/assignment2/src/classroom_analysis_plots.png).

---

## Requirements

Managed with Python 3.14+ and `uv` (or `pip`):

- `websockets`
- `pandas`
- `numpy`
- `matplotlib`

---

## How to Run

Navigate to the `src` directory:

```bash
cd src
```

### 1. Start the WebSocket Server
Run the streaming server in your first terminal:

```bash
python server.py
```

*The server will start listening on `ws://localhost:1234`.*

### 2. Run the Consumer & Analytics Pipeline
In a separate terminal, launch the processing pipeline:

```bash
python main.py
```

*The consumer connects to the server, prints real-time updates as messages arrive, logs final summary statistics, and saves output data and plots upon stream completion.*
