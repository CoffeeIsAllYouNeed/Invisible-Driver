import datetime
import os
import time
import pandas as pd
import serial
from abc import ABC, abstractmethod


class DataSource(ABC):

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def read_line(self) -> str:
        pass

    @abstractmethod
    def is_open(self) -> bool:
        pass

    @abstractmethod
    def close(self) -> None:
        pass


class SerialSource(DataSource):

    def __init__(self, port="COM6", baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.ser = None

    def connect(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            # Bootloader requires 1-2 seconds.
            # For a safer approach, set the sleep time to 5 seconds.
            time.sleep(5)
            return self.ser
        except serial.SerialException as e:
            raise RuntimeError(
                f"Failed to connect to serial port {self.port}: {e}"
            )

    def read_line(self) -> str:
        if self.ser and self.ser.is_open:
            return self.ser.readline().decode("latin-1", errors="ignore").strip()
        return ""

    def is_open(self) -> bool:
        return self.ser is not None and self.ser.is_open

    def close(self) -> None:
        if self.ser and self.ser.is_open:
            self.ser.close()


class FileSource(DataSource):

    def __init__(self, filepath="data/signal.parquet"):
        self.filepath = filepath
        self.generator = None
        self._is_connected = False

    def connect(self):
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"Mock data file not found at: {self.filepath}")
        df = pd.read_parquet(self.filepath)
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


class SourceProvider:

    @staticmethod
    def create_source(source_type: str, **kwargs) -> DataSource:
        if source_type.lower() == "serial":
            return SerialSource(
                port=kwargs.get("port", "COM6"),
                baudrate=kwargs.get("baudrate", 115200)
            )
        elif source_type.lower() == "file":
            return FileSource(
                filepath=kwargs.get("filepath", "data/signal.parquet")
            )
        else:
            raise ValueError(f"Unknown source type: {source_type}")


class DataConnect:

    def __init__(self, source_type: str = "serial", **kwargs):
        self.source = SourceProvider.create_source(source_type, **kwargs)

    def connect(self):
        return self.source.connect()

    def close(self):
        self.source.close()


class DataCollect:

    def __init__(self, connection_manager: DataConnect):
        self.connection_manager = connection_manager

    def collect(self, output_path="data/signal.parquet", max_duration_sec=300):
        if not self.connection_manager.source.is_open():
            self.connection_manager.connect()

        dir_name = os.path.dirname(output_path)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)

        data_buffer = []

        try:
            start_time = time.time()
            print("Data collection started.")

            while time.time() - start_time < max_duration_sec:
                try:
                    data = self.connection_manager.source.read_line()
                except serial.SerialException as e:
                    raise RuntimeError(
                        f"Error reading from serial port: {e}"
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
            self.connection_manager.close()


class RawValueYieldStream:

    def __init__(self, connection_manager: DataConnect):
        self.connection_manager = connection_manager

    def stream(self):
        if not self.connection_manager.source.is_open():
            self.connection_manager.connect()
            
        while True:
            try:
                raw_data = self.connection_manager.source.read_line()
                
                if raw_data:
                    actual_val = raw_data.split(",")[0]
                    yield float(actual_val)
                    
            except serial.SerialException as e:
                raise RuntimeError(
                    f"Serial port disconnected during stream: {e}"
                )
            # Bad values will be dealt in preprocessing step.
            # Hence, we can ignore ValueError.
            except ValueError:
                continue
            except Exception as e:
                raise RuntimeError(f"Unexpected error during streaming: {e}")


class Ingestion:

    def __init__(self, source_type: str = "serial", **kwargs):
        self.connection_manager = DataConnect(source_type, **kwargs)
        self.collector = DataCollect(self.connection_manager)
        self.streamer = RawValueYieldStream(self.connection_manager)

    def collect_data_to_parquet(
        self, output_path="data/signal.parquet", max_duration_sec=300
    ):
        self.collector.collect(output_path, max_duration_sec)

    def stream_raw_data(self):
        yield from self.streamer.stream()

    def close(self):
        self.connection_manager.close()