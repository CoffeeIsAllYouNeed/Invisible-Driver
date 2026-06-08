import csv
import datetime
import os
import serial
import time


class DataConnect:

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

    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()


class DataCollect:

    def __init__(self, connection_manager: DataConnect):
        self.connection_manager = connection_manager

    def collect(self, output_path="data/signal.csv", max_duration_sec=300):
        if (
            not self.connection_manager.ser
            or not self.connection_manager.ser.is_open
        ):
            self.connection_manager.connect()

        dir_name = os.path.dirname(output_path)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)

        try:
            with open(
                output_path, "a", newline="", errors="replace"
            ) as csvfile:
                csvwriter = csv.writer(csvfile)
                if os.stat(output_path).st_size == 0:
                    csvwriter.writerow(["timestamp", "value"])

                start_time = time.time()
                print("Data collection started.")

                while time.time() - start_time < max_duration_sec:
                    try:
                        data = (
                            self.connection_manager.ser.readline()
                            .decode("latin-1")
                            .strip()
                        )
                    except serial.SerialException as e:
                        raise RuntimeError(
                            f"Error reading from serial port: {e}"
                        )

                    current_time = datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S.%f"
                    )
                    values = data.split(",")

                    if len(values) > 0 and values[0].isdigit():
                        csvwriter.writerow([current_time, values[0]])
        finally:
            self.connection_manager.close()


class DataStream:

    def __init__(self, connection_manager: DataConnect):
        self.connection_manager = connection_manager

    def stream(self):
        if (
            not self.connection_manager.ser
            or not self.connection_manager.ser.is_open
        ):
            self.connection_manager.connect()
        while True:
            try:
                raw_data = (
                    self.connection_manager.ser.readline()
                    .decode("latin-1")
                    .strip()
                )
                if raw_data:
                    yield float(raw_data)
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


class DataIngestion:

    def __init__(self, port="COM6", baudrate=115200):
        self.connection_manager = DataConnect(port, baudrate)
        self.collector = DataCollect(self.connection_manager)
        self.streamer = DataStream(self.connection_manager)

    def collect_data_to_csv(
        self, output_path="data/signal.csv", max_duration_sec=300
    ):
        self.collector.collect(output_path, max_duration_sec)

    def stream_raw_data(self):
        yield from self.streamer.stream()

    def close(self):
        self.connection_manager.close()