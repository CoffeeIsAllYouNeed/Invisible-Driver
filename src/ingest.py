import datetime
import os
import time
from abc import ABC, abstractmethod
import pandas as pd
import serial


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
        df = pd.read_parquet(
            filepath,
            engine="c",
            low_memory=True,
            dtype={"value": "Int32"},
            parse_dates=["timestamp"]
        )
        if "value" not in df.columns and len(df.columns) > 0:
            df = df.rename(columns={df.columns[0]: "value"})
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


class SerialSource:

    def __init__(self, port="COM6", baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.ser = None

    def connect(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(5)
            return self.ser
        except serial.SerialException as e:
            raise RuntimeError(
                f"Connection failure [Serial Port] {self.port}: {e}"
            )

    def read_line(self) -> str:
        if self.ser and self.ser.is_open:
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

            return self.ser.readline().decode("latin-1", errors="ignore").strip()
       
        return ""

    def is_open(self) -> bool:
        return self.ser is not None and self.ser.is_open

    def close(self) -> None:
        if self.ser and self.ser.is_open:
            self.ser.close()


class FileSource:

    def __init__(self, filepath="../data/data.csv"):
        self.filepath = filepath
        self.generator = None
        self._is_connected = False

    def connect(self):
        handler = DataHandlerFactory.get_handler(self.filepath)
        df = handler.read_data(self.filepath)
           
        self.generator = (str(val) for val in df["value"].values)
        self._is_connected = True

    def read_line(self) -> str:
        try:
            if self.generator:
                return next(self.generator)
        except StopIteration:
            pass
        return ""

    def is_open(self) -> bool:
        return self._is_connected

    def close(self) -> None:
        self._is_connected = False
        self.generator = None


class DataCollect:

    def __init__(self, source: SerialSource):
        self.source = source

    def collect(self, output_path="data/signal.parquet", max_duration_sec=300):
        if not self.source.is_open():
            self.source.connect()

        dir_name = os.path.dirname(output_path)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)

        data_buffer = []

        try:
            start_time = time.time()
            print("Data collection [BEGIN]")

            while time.time() - start_time < max_duration_sec:
                try:
                    data = self.source.read_line()
                except serial.SerialException as e:
                    raise RuntimeError(
                        f"Connection failure [Serial Port] {self.port}: {e}"
                    )

                current_time = datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S.%f"
                )
                values = data.split(",")

                if len(values) > 0 and values[0].replace('.', '', 1).isdigit():
                    data_buffer.append({"timestamp": current_time, "value": values[0]})
           
            if data_buffer:
                df = pd.DataFrame(data_buffer)
                df.to_parquet(output_path, engine="pyarrow", compression="snappy", index=False)

        finally:
            self.source.close()


class RawValueYieldStream:

    def __init__(self, source: SerialSource):
        self.source = source

    def stream(self):
        if not self.source.is_open():
            self.source.connect()
           
        while True:
            try:
                raw_data = self.source.read_line()
               
                if raw_data:
                    actual_val = raw_data.split(",")[0]
                    yield float(actual_val)
                   
            except serial.SerialException as e:
                raise RuntimeError(
                    f"Serial port disconnected during stream: {e}"
                )
            except ValueError:
                continue
            except Exception as e:
                raise RuntimeError(f"Unexpected error during streaming: {e}")


class OptionStrategy(ABC):

    @abstractmethod
    def execute(self, ingestion_instance, source_type: str, **kwargs):
        pass


class SoftwareOptionStrategy(OptionStrategy):

    def execute(self, ingestion_instance, source_type: str, **kwargs):
        filepath = kwargs.get("filepath", "../data/data.csv")
        handler = DataHandlerFactory.get_handler(filepath)
        ingestion_instance.software_data = handler.read_data(filepath)


class HardwareOptionStrategy(OptionStrategy):

    def execute(self, ingestion_instance, source_type: str, **kwargs):
        if source_type.lower() == "serial":
            ingestion_instance.source = SerialSource(
                port=kwargs.get("port", "COM6"),
                baudrate=kwargs.get("baudrate", 115200)
            )
        elif source_type.lower() == "file":
            ingestion_instance.source = FileSource(
                filepath=kwargs.get("filepath", "../data/data.csv")
            )
        else:
            raise ValueError(f"INVALID source type: {source_type}")

        ingestion_instance.collector = DataCollect(ingestion_instance.source)
        ingestion_instance.streamer = RawValueYieldStream(ingestion_instance.source)


class OptionStrategyFactory:

    @staticmethod
    def get_strategy(option: str) -> OptionStrategy:
        if option.lower() == "software":
            return SoftwareOptionStrategy()
        elif option.lower() == "hardware":
            return HardwareOptionStrategy()
        else:
            raise ValueError("Option must be either 'software' or 'hardware'")


class Ingestion:

    def __init__(self, option: str, source_type: str = "serial", **kwargs):
        self.option = option.lower()
        self.source = None
        self.collector = None
        self.streamer = None
        self.software_data = None

        strategy = OptionStrategyFactory.get_strategy(self.option)
        strategy.execute(self, source_type, **kwargs)

    def collect_data_to_parquet(
        self, output_path="../data/signal.parquet", max_duration_sec=300
    ):
        if self.option == "software":
            return
        if self.collector is None:
            raise RuntimeError("Collector is not initialized for hardware option")
        self.collector.collect(output_path, max_duration_sec)

    def stream_raw_data(self):
        if self.option == "software":
            return
        if self.streamer is None:
            raise RuntimeError("Streamer is not initialized for hardware option")
        yield from self.streamer.stream()

    def close(self):
        if self.source:
            self.source.close()