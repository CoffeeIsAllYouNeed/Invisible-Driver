import csv
import datetime
import serial
import time


class DataIngestion:
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
        except serial.SerialException as e:
            raise RuntimeError(
                f"Failed to connect to serial port {self.port}: {e}"
            )

    def collect_data_to_csv(self, output_path="data/signal.csv", max_duration_sec=300):
        if not self.ser or not self.ser.is_open:
            self.connect()

        try:
            # Errors set to replace to bad character.
            # The replaced characters can be dealt in preprocessing.
            with open(output_path, "a", newline="", errors="replace") as csvfile:
                csvwriter = csv.writer(csvfile)
                start_time = time.time()
                print("Data collection started.")

                # To prevent infinite loop: 
                # Data collection duration set as 300 seconds.
                while time.time() - start_time < max_duration_sec:
                    try:
                        # UTF-8 decoding might crash due to bad characters.
                        # Hence, we implemented Latin-1.
                        # It can decode all byte values.
                        data = self.ser.readline().decode("latin-1").strip()
                    except serial.SerialException as e:
                        raise RuntimeError(f"Error reading from serial port: {e}")

                    current_time = datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S.%f"
                    )
                    values = data.split(",")
                          
                    # Safety check for initial bad characters.
                    # Skipping error message as the logs might clutter.
                    if len(values) > 0 and values[0].isdigit():
                        csvwriter.writerow([current_time, values[0]])
        finally:
            self.close()

    def stream_raw_data(self):
        if not self.ser or not self.ser.is_open:
            self.connect()
        while True:
            try:
                raw_data = self.ser.readline().decode("latin-1").strip()
                if raw_data:
                    yield float(raw_data)
            except serial.SerialException as e:
                raise RuntimeError(f"Serial port disconnected during stream: {e}")
            except ValueError:
                continue
            except Exception as e:
                raise RuntimeError(f"Unexpected error during streaming: {e}")

    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()