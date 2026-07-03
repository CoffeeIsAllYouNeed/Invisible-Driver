import datetime
import os
import time

import pandas as pd

from src import (
    FeatureEngineer,
    Ingestion,
    Predict,
    Preprocess,
    Reproducible,
)

OPTION = "b"
MODEL_PATH = "model/model.pkl"
DATA_CSV_PATH = "data/data.csv"
TIME_WINDOW_SEC = 2.0


def main() -> None:
    print("Set seeds [BEGIN]")
    reproducible_pipeline = Reproducible()
    reproducible_pipeline.set_seed(42)
    print("Set seeds [END]")

    if OPTION == "a":
        print("Hardware Ingestion [BEGIN]")
        ingestion = Ingestion(
            option="hardware", port="COM6", baudrate=115200
        )
        print("Hardware Ingestion [END]")
    elif OPTION == "b":
        print("Simulation Ingestion [BEGIN]")
        ingestion = Ingestion(option="simulation", filepath=DATA_CSV_PATH)
        print("Simulation Ingestion [END]")
    else:
        raise ValueError(
            f"Unknown pipeline option: '{OPTION}'. Select 'a' or 'b'."
        )

    print("Preprocessing [BEGIN]")
    preprocess_layer = Preprocess()
    print("Preprocessing [END]")

    print("Feature Engineering [BEGIN]")
    feature_layer = FeatureEngineer()
    print("Feature Engineering [END]")

    print("Prediction [BEGIN]")
    prediction_layer = Predict()

    prediction_layer.load_prediction_engine(model_path=MODEL_PATH)
    print("Prediction [END]")

    print(f"\n--- Running Pipeline Inferences (Window: {TIME_WINDOW_SEC}s) ---")

    try:
        raw_stream = ingestion.run()

        while True:
            window_buffer = []
            window_start_time = time.time()

            while time.time() - window_start_time < TIME_WINDOW_SEC:
                try:
                    val = next(raw_stream)
                    current_ts = datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S.%f"
                    )
                    window_buffer.append(
                        {"timestamp": current_ts, "value": val}
                    )
                except StopIteration:
                    if not window_buffer:
                        print("Data stream complete. Exiting pipeline loop.")
                        return
                    break
                except Exception as stream_err:
                    print(f"Skipping corrupt streaming frame: {stream_err}")
                    continue

            if not window_buffer:
                time.sleep(0.1)
                continue

            try:
                input_df = pd.DataFrame(window_buffer)

                pivoted_df = preprocess_layer.preprocess(input_df)

                _, feature_df = feature_layer.preprocess(pivoted_df)

                predictions = prediction_layer.predict_batch(feature_df)

                timestamp_str = datetime.datetime.now().strftime("%H:%M:%S")
                print(f"[{timestamp_str}] Window Predictions: {predictions}")

            except Exception as pipeline_err:
                print(f"Pipeline calculation batch skipped: {pipeline_err}")

    except KeyboardInterrupt:
        print("\nPipeline execution stopped manually.")
    finally:
        print("Pipeline streaming channels disconnected.")


if __name__ == "__main__":
    main()