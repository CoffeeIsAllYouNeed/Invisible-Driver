import datetime
import os
import time
import pandas as pd
import serial


# =====================================================================
# PIPELINE COMPONENTS
# =====================================================================

class MethodSelect:
    # At the game interface, user has two options: 
    # (a) Simulation (If user doesn't have hardware setup)
    # (b) Hardware (If user has hardware setup)

    def __init__(self, option: str):
        self.option = option.strip().lower()
        if self.option not in ["simulation", "hardware"]:
            raise ValueError("METHOD SELECTION ERROR: \n" 
            "CHOOSE 'simulation' OR 'hardware'.")
        
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
        return df


class ParquetDataHandle:

    def execute(self, filepath: str) -> pd.DataFrame:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"DATA FILE NOT FOUND: {filepath}")
        # CONTEXT:
        # In practical implementation,setup might produce upto 500 readings/second.
        # This will require more memory and time to process the data.
       
        # For fast-processing: Select pyarrow-engine.
        # For low memory usage: Converted all values to int32.
        
        df = pd.read_parquet(
            path=filepath,
            engine="pyarrow"
        )
        
        if "value" in df.columns:
            df["value"] = df["value"].astype("Int32")
            
        return df


class HardwareIngest:

    def process(self, ctx: dict) -> pd.DataFrame:
        port = ctx.get("port", "COM6")
        baudrate = ctx.get("baudrate", 115200)
        # DATA COLLECTION TIME LIMIT: 
        # Adjust as per requirements.
        # We have used 5 minutes (300 seconds) as default.
        max_duration_sec = ctx.get("max_duration_sec", 300)
        output_path = ctx.get("output_path", "../data/signal.parquet")

        connector = Connect(port, baudrate)
        ser_connection = connector.establish()

        try:
            collector = Collect(ser_connection)
            raw_lines = collector.gather(max_duration_sec)

            decoder = Decode()
            decoded_lines = decoder.process_batch(raw_lines)

            noise_handler = NoiseHandle()
            filtered_records = noise_handler.clean_batch(decoded_lines)

            storage_writer = Store()
            return storage_writer.save_and_convert(filtered_records, output_path)

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
            # BOOTLOADER INTIALIZATION TIME:
            
            # FOR MODERN ARDUINO:
            # Modern Arduino's bootloader normally finishes initializing in 1 to 2 seconds
            # 5-second delay is implemented as a safety margin.

            # FOR OLDER ARDUINO:
            # Older Arduino's bootloader might take around 4 to 8 seconds to initialize. 
            # Extend the sleep time to 10 seconds in that case. 
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


class Store:

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


class FetchBatch:

    def __init__(self, option: str, ctx: dict):
        self.option = option.strip().lower()
        self.ctx = ctx
        self.connector = None

    def stream_raw_data(self):
        if self.option == "simulation":
            filepath = self.ctx.get("filepath", "data/data.csv")
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"DATA FILE NOT FOUND: {filepath}")
            df = pd.read_csv(filepath, engine="c", low_memory=True)
            for _, row in df.iterrows():
                yield row["value"]
        elif self.option == "hardware":
            port = self.ctx.get("port", "COM6")
            baudrate = self.ctx.get("baudrate", 115200)
            self.connector = Connect(port, baudrate)
            ser_connection = self.connector.establish()
            decoder = Decode()
            noise_handler = NoiseHandle()
            while True:
                line_bytes = ser_connection.readline()
                if line_bytes:
                    decoded = decoder.process_batch([("now", line_bytes)])
                    cleaned = noise_handler.clean_batch(decoded)
                    if cleaned:
                        yield cleaned[0]["value"]

    def close(self) -> None:
        if self.connector:
            self.connector.close()


# =====================================================================
# MAIN PIPELINE CLASS
# =====================================================================

class Ingestion:

    def __init__(self, option: str, **kwargs):
        self.option = option
        self.ctx = kwargs
        self.batch_fetcher = FetchBatch(self.option, self.ctx)

    def run(self) -> pd.DataFrame:
        selector = MethodSelect(self.option)
        df = selector.route(self.ctx)
        print("INGESTION STEP [COMPLETED]")
        return df

    def stream_raw_data(self):
        return self.batch_fetcher.stream_raw_data()

    def close(self) -> None:
        self.batch_fetcher.close()