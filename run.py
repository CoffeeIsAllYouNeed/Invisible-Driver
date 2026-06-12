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
    reproducible_pipeline = Reproducible()
    reproducible_pipeline.set_seed(42)

    if OPTION == "a":
        print("Starting pipeline: Ingesting from Hardware (Serial Stream)...")
        ingestion = Ingestion(
            source_type="serial", port="COM6", baudrate=115200
        )
    elif OPTION == "b":
        print("Starting pipeline: Ingesting from File (data/data.csv)...")
        ingestion = Ingestion(source_type="file", filepath=DATA_CSV_PATH)
    else:
        raise ValueError(
            f"Unknown pipeline option: '{OPTION}'. Select 'a' or 'b'."
        )

    preprocess_layer = Preprocess()
    feature_layer = FeatureEngineer()
    prediction_layer = Predict()

    prediction_layer.load_prediction_engine(model_path=MODEL_PATH)

    print(f"\n--- Running Pipeline Inferences (Window: {TIME_WINDOW_SEC}s) ---")

    try:
        raw_stream = ingestion.stream_raw_data()

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
        ingestion.close()
        print("Pipeline streaming channels disconnected.")


if __name__ == "__main__":
    main()