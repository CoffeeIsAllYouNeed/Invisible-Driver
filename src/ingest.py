import datetime
import os
import time
from abc import ABC, abstractmethod
import pandas as pd
import serial


# =====================================================================
# DATA HANDLER LAYER
# =====================================================================

class DataHandler(ABC):

    @abstractmethod
    def read_data(self, filepath: str) -> pd.DataFrame:
        pass


class CSVDataHandler(DataHandler):

    def read_data(self, filepath: str) -> pd.DataFrame:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"DATA FILE NOT FOUND: {filepath}")
        # CONTEXT:
        # In practical implementation,setup might produce upto 500 readings/second.
        # This will require more memory and time to process the data.

        # For fast-processing: Select C-engine.
        # For low memory usage: Enable low memory and converted all values to int32.

        df = pd.read_csv(
            filepath_or_buffer=filepath,
            engine="c",
            low_memory=True,
            dtype={"value": "Int32"},
            parse_dates=["timestamp"]
        )
        if "value" not in df.columns and len(df.columns) > 0:
            df = df.rename(columns={df.columns[0]: "value"})
        return df


class ParquetDataHandler(DataHandler):

    def read_data(self, filepath: str) -> pd.DataFrame:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"DATA FILE NOT FOUND: {filepath}")
        
        df = pd.read_parquet(filepath)
        
        if "value" not in df.columns and len(df.columns) > 0:
            df = df.rename(columns={df.columns[0]: "value"})
            
        if "value" in df.columns:
            df["value"] = df["value"].astype("Int32")
            
        return df


class DataHandlerFactory:

    @staticmethod
    def get_handler(filepath: str) -> DataHandler:
        if filepath.endswith(".csv"):
            return CSVDataHandler()
        elif filepath.endswith(".parquet"):
            return ParquetDataHandler()
        else:
            raise ValueError(f"Unsupported file extension for path: {filepath}")


# =====================================================================
# PIPELINE COMPONENTS
# =====================================================================

class MethodSelect:

    def __init__(self, option: str):
        self.option = option.strip().lower()
        if self.option not in ["simulation", "hardware"]:
            raise ValueError("Selection method must be 'simulation' or 'hardware'")

    def route(self, ctx: dict) -> pd.DataFrame:
        if self.option == "simulation":
            return SimulationIngest().process(ctx)
        else:
            return HardwareIngest().process(ctx)


class SimulationIngest:

    def process(self, ctx: dict) -> pd.DataFrame:
        filepath = ctx.get("filepath", "../data/data.csv")
        return CsvDataHandle().execute(filepath)


class CsvDataHandle:

    def execute(self, filepath: str) -> pd.DataFrame:
        handler = DataHandlerFactory.get_handler(filepath)
        return handler.read_data(filepath)


class HardwareIngest:

    def process(self, ctx: dict) -> pd.DataFrame:
        port = ctx.get("port", "COM6")
        baudrate = ctx.get("baudrate", 115200)
        max_duration_sec = ctx.get("max_duration_sec", 300)
        output_path = ctx.get("output_path", "data/signal.parquet")

        connector = Connect(port, baudrate)
        ser_connection = connector.establish()

        try:
            collector = Collect(ser_connection)
            raw_lines = collector.gather(max_duration_sec)

            decoder = Decode()
            decoded_lines = decoder.process_batch(raw_lines)

            noise_handler = NoiseHandle()
            filtered_records = noise_handler.clean_batch(decoded_lines)

            parquet_writer = ParquetDataHandle()
            return parquet_writer.save_and_convert(filtered_records, output_path)

        finally:
            connector.close()


class Connect:

    def __init__(self, port: str, baudrate: int):
        self.port = port
        self.baudrate = baudrate
        self.ser = None

    def establish(self) -> serial.Serial:
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(5)
            return self.ser
        except serial.SerialException as e:
            raise RuntimeError(
                f"Connection failure [Serial Port] {self.port}: {e}"
            )

    def close(self) -> None:
        if self.ser and self.ser.is_open:
            self.ser.close()


class Collect:

    def __init__(self, ser_connection: serial.Serial):
        self.ser = ser_connection

    def gather(self, max_duration_sec: int) -> list:
        if not self.ser or not self.ser.is_open:
            raise RuntimeError("Serial connection must be open to collect data.")

        raw_lines = []
        start_time = time.time()
        print("Data collection [BEGIN]")

        while time.time() - start_time < max_duration_sec:
            try:
                line_bytes = self.ser.readline()
                if line_bytes:
                    current_time = datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S.%f"
                    )
                    raw_lines.append((current_time, line_bytes))
            except serial.SerialException as e:
                raise RuntimeError(
                    f"Serial interface disconnected during collection: {e}"
                )
        return raw_lines


class Decode:

    def process_batch(self, raw_lines: list) -> list:
        processed_records = []
        for timestamp, byte_data in raw_lines:
            # NOISE TESTING IN HARDWARE:

            # Method-1:
            # Set encoding="latin-1" and disable isdigit() check.
            # It will substitute the noise character with a corresponding latin-1 character.
            # Hence, you can track noise.

            # Method-2:
            # Use encoding="ascii", errors="replace".
            # It will substitute  (U+FFFD, the official REPLACEMENT CHARACTER) for decoding errors.
            # Hence, you can see the records with noise.

            # FOR PIPELINE:

            # Use encoding="latin-1", errors="ignore"
            # Latin-1 will decode corrupted byte into a Latin-1 character.
            # The corrupted character will be dropped by isdigit() check.

            decoded_str = byte_data.decode("latin-1", errors="ignore").strip()
            processed_records.append((timestamp, decoded_str))
        return processed_records


class NoiseHandle:

    def clean_batch(self, decoded_lines: list) -> list:
        cleaned_buffer = []
        for timestamp, text in decoded_lines:
            values = text.split(",")
            if len(values) > 0 and values[0]:
                val_to_check = values[0]
                if val_to_check.replace('.', '', 1).isdigit():
                    cleaned_buffer.append(
                        {"timestamp": timestamp, "value": val_to_check}
                    )
        return cleaned_buffer


class ParquetDataHandle:

    def save_and_convert(self, cleaned_records: list, output_path: str) -> pd.DataFrame:
        if not cleaned_records:
            return pd.DataFrame(columns=["timestamp", "value"])

        dir_name = os.path.dirname(output_path)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)

        try:
            df = pd.DataFrame(cleaned_records)
            df.to_parquet(
                output_path,
                engine="pyarrow",
                compression="snappy",
                index=False
            )
            return df
        except Exception as e:
            raise IOError(f"Failed to save data to parquet: {e}")


# =====================================================================
# MAIN PIPELINE CLASS
# =====================================================================

class Ingestion:

    def __init__(self, option: str, **kwargs):
        self.option = option
        self.ctx = kwargs

    def run(self) -> pd.DataFrame:
        selector = MethodSelect(self.option)
        df = selector.route(self.ctx)
        print("INGESTION PIPELINE [COMPLETED]")
        return df