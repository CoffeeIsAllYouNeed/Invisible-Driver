import asyncio
import datetime
import json
import os
import random

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import pandas as pd

from src.feature_engineer import FeatureEngineer
from src.ingest import Ingestion
from src.prediction import Predict
from src.preprocess import Preprocess

app = FastAPI()

SERIAL_PORT = "COM6"
SIMULATOR_FILE = "data/data.csv"
MODEL_PATH = "model/model.pkl"
TIME_WINDOW_SEC = 2.0


@app.get("/")
async def get_dashboard():
    with open("templates/ui.html", "r", encoding="utf-8") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)


@app.websocket("/pipeline_stream")
async def pipeline_websocket(websocket: WebSocket):
    await websocket.accept()

    ingestion_system = None
    stream_task = None

    async def core_data_emitter(mode: str):
        nonlocal ingestion_system
        try:
            target_source = mode
            target_path = "data/signal.parquet"

            if mode == "file":
                if os.path.exists(SIMULATOR_FILE):
                    raw_df = pd.read_csv(SIMULATOR_FILE)
                    clean_df = pd.DataFrame()
                    if "value" in raw_df.columns:
                        clean_df["value"] = raw_df["value"]
                    else:
                        clean_df["value"] = raw_df.iloc[:, 1]

                    clean_df.to_parquet(
                        target_path, engine="pyarrow", index=False
                    )
                else:
                    print(f"Simulator target missing at: {SIMULATOR_FILE}")
                    return

            ingestion_system = Ingestion(
                source_type=target_source,
                port=SERIAL_PORT,
                filepath=target_path,
            )
            preprocess_layer = Preprocess()
            feature_layer = FeatureEngineer()
            prediction_layer = Predict()

            prediction_layer.load_prediction_engine(model_path=MODEL_PATH)

            raw_stream = ingestion_system.stream_raw_data()
            print(
                f"Pipeline active via mode: {mode}. Beginning inference loops."
            )

            while True:
                window_buffer = []
                window_start_time = asyncio.get_event_loop().time()

                while (
                    asyncio.get_event_loop().time() - window_start_time
                ) < TIME_WINDOW_SEC:
                    try:
                        raw_val = next(raw_stream)
                        current_ts = datetime.datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S.%f"
                        )
                        window_buffer.append(
                            {"timestamp": current_ts, "value": float(raw_val)}
                        )
                    except StopIteration:
                        if not window_buffer:
                            print("Data stream file finished.")
                            return
                        break
                    await asyncio.sleep(0.002)

                if not window_buffer:
                    continue

                try:
                    input_df = pd.DataFrame(window_buffer)

                    pivoted_df = preprocess_layer.preprocess(input_df)

                    _, feature_df = feature_layer.preprocess(pivoted_df)

                    predictions = prediction_layer.predict_batch(feature_df)

                    if predictions:
                        final_prediction = predictions[0]

                        if random.random() < 0.30:
                            cognitive_state = "RELAXED"
                            action_signal = "NONE"
                            print(
                                "🎲 RANDOMIZER: Intermittent Relaxed interval forced!"
                            )
                        else:
                            if final_prediction == "Attentive State":
                                cognitive_state = "ATTENTIVE"
                                action_signal = "ACCELERATE"
                            else:
                                cognitive_state = "RELAXED"
                                action_signal = "NONE"

                        payload = {
                            "signal": window_buffer[-1]["value"],
                            "state": cognitive_state,
                            "action": action_signal,
                        }

                        await websocket.send_text(json.dumps(payload))
                        print(
                            f"Live Pipeline Broadcast: {cognitive_state} -> "
                            f"Action Sent: {action_signal}"
                        )

                except Exception as batch_err:
                    print(
                        f"Pipeline inference skipped for this window: {batch_err}"
                    )

        except Exception as e:
            print(f"Data stream exception handled: {e}")
        finally:
            if ingestion_system:
                ingestion_system.close()

    try:
        while True:
            message_text = await websocket.receive_text()
            data = json.loads(message_text)
            command = data.get("command")

            if command == "START" and not stream_task:
                mode = data.get("mode", "serial")
                stream_task = asyncio.create_task(core_data_emitter(mode))

            elif command == "STOP" and stream_task:
                stream_task.cancel()
                stream_task = None
                if ingestion_system:
                    ingestion_system.close()
                print("Pipeline loop halted.")

    except WebSocketDisconnect:
        print("User connection dropped.")
    finally:
        if stream_task:
            stream_task.cancel()
        if ingestion_system:
            ingestion_system.close()