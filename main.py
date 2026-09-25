import asyncio
import json
import matplotlib.pyplot as plt
import pandas as pd
import websockets

buffer = []


async def consume_and_process():
    uri = "ws://localhost:1234"
    print(f"Connecting to {uri}...")
    df_stream = None
    try:
        async with websockets.connect(uri) as websocket:
            async for message in websocket:
                data = json.loads(message)

                # Check for stream completion sentinel
                if data.get("status") == "EOF":
                    print("\nReceived EOF signal from server. Finalizing pipeline...")
                    break

                buffer.append(data)

                df_stream = pd.DataFrame(buffer)

                df_stream["Temp_C"] = df_stream["Temp_C"].interpolate(method="linear")
                df_stream["CO2_ppm"] = df_stream["CO2_ppm"].interpolate(method="linear")
                df_stream["Occupancy"] = df_stream["Occupancy"].ffill()

                df_stream["Temp_roll3"] = df_stream["Temp_C"].rolling(3).mean()
                df_stream["CO2_roll3"] = df_stream["CO2_ppm"].rolling(3).mean()
                df_stream["Power_roll3"] = df_stream["Power_kW"].rolling(3).mean()

                # Feature engineering
                df_stream["occupancy_density"] = df_stream["Occupancy"] / 40.0
                df_stream["energy_per_student"] = df_stream["Power_kW"] / df_stream["Occupancy"]
                df_stream["comfort_flag"] = (
                    (df_stream["CO2_ppm"] <= 1000) & 
                    (df_stream["Temp_C"].between(20.0, 24.0))
                )

                latest = df_stream.iloc[-1]
                co2_avg = f"{latest['CO2_roll3']:.1f}" if pd.notna(latest['CO2_roll3']) else "N/A"
                print(
                    f"[{latest['Time']}] Clean Temp: {latest['Temp_C']:.1f}°C | "
                    f"3-min CO2 Avg: {co2_avg} ppm | "
                    f"Comfort: {latest['comfort_flag']}"
                )

    except (websockets.exceptions.ConnectionClosedOK, websockets.exceptions.ConnectionClosed):
        print("Socket connection closed.")

    if df_stream is None or df_stream.empty:
        print("No data received. Exiting.")
        return

    df = df_stream

    df.to_csv("cleaned_classroom_data.csv", index=False)
    print("\n✓ Cleaned dataset saved to 'cleaned_classroom_data.csv'")

    print("\n=== Statistical Analysis ===")
    print(
        f"Temp -> Mean: {df['Temp_C'].mean():.2f}°C, Median: {df['Temp_C'].median():.2f}°C, "
        f"Min: {df['Temp_C'].min():.2f}°C, Max: {df['Temp_C'].max():.2f}°C"
    )
    print(f"CO2  -> Mean: {df['CO2_ppm'].mean():.2f} ppm, Max: {df['CO2_ppm'].max():.2f} ppm")

    peak_power_row = df.loc[df["Power_kW"].idxmax()]
    print(f"Peak Power: {peak_power_row['Power_kW']} kW at {peak_power_row['Time']}")

    corr = df["Occupancy"].corr(df["Power_kW"])
    print(f"Occupancy vs Power Correlation: {corr:.4f}")

    fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    ax1_twin = axes[0].twinx()
    axes[0].plot(df["Time"], df["CO2_roll3"], color="tab:red", marker="o", label="CO2 3-min Avg (ppm)")
    ax1_twin.plot(df["Time"], df["Temp_roll3"], color="tab:orange", marker="s", linestyle="--", label="Temp 3-min Avg (°C)")
    axes[0].set_ylabel("CO2 (ppm)", color="tab:red")
    ax1_twin.set_ylabel("Temp (°C)", color="tab:orange")
    axes[0].set_title("3-Minute Rolling CO2 and Temperature Stream")
    axes[0].grid(True, linestyle=":", alpha=0.6)

    axes[1].plot(df["Time"], df["Occupancy"], color="tab:blue", marker="o", label="Occupancy")
    ax2_twin = axes[1].twinx()
    ax2_twin.plot(df["Time"], df["Power_kW"], color="tab:green", marker="^", linestyle="-.", label="Power (kW)")
    axes[1].set_xlabel("Time")
    axes[1].set_ylabel("Occupancy", color="tab:blue")
    ax2_twin.set_ylabel("Power (kW)", color="tab:green")
    axes[1].set_title("Occupancy vs. Power Consumption")
    axes[1].grid(True, linestyle=":", alpha=0.6)

    plt.tight_layout()
    plt.savefig("classroom_analysis_plots.png")
    print("✓ Saved plots to 'classroom_analysis_plots.png'")
    plt.show()


if __name__ == "__main__":
    asyncio.run(consume_and_process())