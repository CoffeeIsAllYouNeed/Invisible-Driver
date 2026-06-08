import os
import sys
import threading
import time
import pandas as pd
import pyautogui

from src import (
    Ingestion,
    Preprocess,
    FeatureEngineer,
    Predict,
    Reproducible,
)


class DataFetch:

    def __init__(self, filepath: str, batch_duration_sec: int = 2):
        self.filepath = filepath
        self.batch_duration_sec = batch_duration_sec
        self.last_read_timestamp = None

    def fetch_latest_batch(self) -> pd.DataFrame:
        try:
            # Ensure the file doesn't require special permissions to access.
            # If so, it will return False.
            if not os.path.exists(self.filepath):
                return pd.DataFrame()
            
            # pyarrow to enable multithreading. 
            full_df = pd.read_parquet(self.filepath, engine="pyarrow")

            # Return empty df for type consistency.
            # Empty files are handled in preprocessing.
            if full_df.empty:
                return pd.DataFrame()

            full_df["timestamp"] = pd.to_datetime(full_df["timestamp"])

            # Quicksort has low time complexity and space complexity.
            # TIME COMPLEXITY: O(nlogn)
            # SPACE COMPLEXITY: O(logn)
            full_df = full_df.sort_values(by="timestamp", kind="quicksort").reset_index(drop=True)

            latest_time = full_df["timestamp"].iloc[-1]

            if self.last_read_timestamp is None:
                start_window = latest_time - pd.Timedelta(seconds=self.batch_duration_sec)
            else:
                start_window = self.last_read_timestamp

            batch = full_df[
                (full_df["timestamp"] >= start_window)
                & (full_df["timestamp"] <= latest_time)
            ]

            self.last_read_timestamp = latest_time
            return batch

        except Exception:
            return pd.DataFrame()


class KeyboardController:

    def trigger_action(self, duration: float = 2.0) -> None:
        # 'W' key is used for acceleration in the game.
        pyautogui.keyDown('w')
        time.sleep(duration)
        pyautogui.keyUp('w')


class Run:

    def __init__(self, port: str = "COM6", baudrate: int = 115200, 
                 storage_path: str = "data/signal.parquet", 
                 batch_duration_sec: int = 2):
        
        self.storage_path = storage_path
        self.batch_duration_sec = batch_duration_sec
        
        self.ingestion_system = Ingestion(port=port, baudrate=baudrate)
        self.preprocess_pipeline = Preprocess()
        self.feature_pipeline = FeatureEngineer()
        self.model_pipeline = Predict()
        
        self.fetcher = DataFetch(self.storage_path, self.batch_duration_sec)
        self.keyboard = KeyboardController()
        self.reproducibility_manager = Reproducible()
        
        self.ingestion_thread = None
        self.is_running = False

    def _process_workflow(self, raw_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        pivoted = self.preprocess_pipeline.preprocess(raw_df)
        _, features = self.feature_pipeline.preprocess(pivoted)
        return pivoted, features

    def _background_ingestion(self):
       
        try:
            self.ingestion_system.collect_data_to_parquet(
                output_path=self.storage_path, 
                max_duration_sec=300
            )
        except Exception:
            self.is_running = False

    def execute(self):
        self.reproducibility_manager.set_seed(42)

        if os.path.exists(self.storage_path):
            try:
                os.remove(self.storage_path)
            except Exception:
                pass

        self.is_running = True
        self.ingestion_thread = threading.Thread(target=self._background_ingestion, daemon=True)
        self.ingestion_thread.start()

        # Prevents a race condition by giving the background thread time to start.
        # Allows the hardware microcontroller 5 seconds to reset and initialize.
        # Allows 1 second for initial sensor data to be written to disk.
        # Prevents the training step from crashing on a missing or empty file.
        time.sleep(6) 

        try:
            raw_train_df = pd.read_parquet(self.storage_path)
            pivoted, features = self._process_workflow(raw_train_df)
            self.model_pipeline.fit_and_save_pipeline(pivoted, features)
            self.model_pipeline.load_prediction_engine()
        except Exception:
            self.ingestion_system.close()
            sys.exit(1)

        try:
            while self.is_running:
                time.sleep(self.batch_duration_sec)
                
                batch = self.fetcher.fetch_latest_batch()
                if batch.empty or len(batch) < 10:
                    continue

                try:
                    pivoted_batch, batch_features = self._process_workflow(batch)
                    predictions = self.model_pipeline.predict_batch(batch_features)

                    if any(pred == "beta, gamma" for pred in predictions):
                        self.keyboard.trigger_action()

                except Exception:
                    continue
        except KeyboardInterrupt:
            pass
        finally:
            self.ingestion_system.close()


if __name__ == "__main__":
    runner = Run()
    runner.execute()