import asyncio
import json
import numpy as np
import pandas as pd
import websockets

df = pd.read_csv("dataset.csv")
df = df.replace({np.nan: None})


async def stream_sensor_data(websocket):
    client_addr = websocket.remote_address
    print(f"Client connected: {client_addr}")
    try:
        for idx, row in df.iterrows():
            payload = row.to_dict()
            await websocket.send(json.dumps(payload))
            print(f"server: sent stream payload [{payload['Time']}]: {payload}")
            await asyncio.sleep(1)

        await websocket.send(json.dumps({"status": "EOF"}))
        print("Server finished streaming all rows.")

    except websockets.exceptions.ConnectionClosed:
        print(f"Client {client_addr} disconnected prematurely.")


async def main():
    async with websockets.serve(stream_sensor_data, "localhost", 1234):
        print("WebSocket server running on ws://localhost:1234")
        await asyncio.Future()  # Keep server alive


if __name__ == "__main__":
    asyncio.run(main())