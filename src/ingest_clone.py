import os
import pandas as pd
import serial.tools.list_ports
import time
import datetime
import csv

class GetSelectedMode: 

    def __init__(self, mode: str) -> None: 
        self.mode = mode.lower()
     
    def get(self) -> str: 
        return self.mode
    

class SelectMethod: 

    def __init__(self, mode: str) -> None: 
        self.mode = mode.lower()

    def select(self) -> None:
    # GAME INTERFACE HAS TWO OPTIONS: 
    # (a) Simulation (If user doesn't have hardware setup)
    # (b) Hardware (If user has hardware setup)
        if self.mode == "simulation": 
            return #simulation
        elif self.mode == "hardware": 
            return #hardware
        

class TakeUserMethodInput: 



class CheckFilePath:

    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
    
    def check(self) -> bool:
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"Invalid filepath: {self.filepath}")
        else:
            return True


class CheckFileExists:

    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
    
    def check(self) -> bool:
        if CheckFilePath(self.filepath).check(): 
            if not os.path.isfile(self.filepath):
                raise FileNotFoundError(f"File not found: {self.filepath}")
        
            if os.path.getsize(self.filepath) == 0:
                raise ValueError(f"File is empty: {self.filepath}")
        
            if not os.access(self.filepath, os.R_OK):
                raise PermissionError(f"File is not readable: {self.filepath}")

        return True
    

class GetFile:

    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
    
    def get(self) -> pd.DataFrame:
        if CheckFileExists(self.filepath): 
            if self.filepath.endswith(".csv"):
                return pd.read_csv(self.filepath)
            if self.filepath.endswith(".parquet"):
                return pd.read_parquet(self.filepath)
            raise ValueError(f"Unsupported file format: {self.filepath}")
    

class CheckPort:

    def __init__(self, port: str) -> None:
        self.port = port 

    def check(self) -> bool:
        if not self.port:
            raise ValueError("Port should not be empty.")
        
        available_ports = serial.tools.list_ports.comports()
      
        print("Available Ports:\n")
        for port in available_ports:
            print(f"Port: {port.device}, Description: {port.description}")

        if self.port not in [port.device for port in available_ports]:
            raise ValueError(f"Invalid Port: '{self.port}'")
        
    def connect(self) -> serial.Serial:
        if self.check():
            try:
                ser = serial.Serial(self.port)
                return ser
            except serial.SerialException as e:
                raise RuntimeError(
                    f"Port Connection Failed: {self.port}, Error: {e}"
                )


class CheckBaudrate:

    def __init__(self, baudrate: int) -> None:
        self.baudrate = baudrate

    def check(self) -> bool:
        if not self.baudrate:
            raise ValueError("Baudrate should not be empty.")
        
        available_baudrates = [
            50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800,
            9600, 19200, 28800, 38400, 57600, 76800, 115200, 230400,
            460800, 576000, 921600
        ]
        
        if self.baudrate not in available_baudrates:
            raise ValueError(
                f"Invalid Baudrate: '{self.baudrate}'"
            )
        return True
    

class SelectBootLoaderDuration: 

    def __init__(self,duration: int | float) -> None: 
        self.duration = duration

    def select(self) -> None:
        if self.duration < 2.0:
            raise ValueError("Bootloader duration should be at least 2 seconds.")        
        # BOOTLOADER INTIALIZATION TIME:          
            # FOR MODERN ARDUINO:
                # Modern Arduino's bootloader normally finishes initializing in 1 to 2 seconds
                # 5-second delay is implemented as a safety margin.
            # FOR OLDER ARDUINO:
                # Older Arduino's bootloader might take around 4 to 8 seconds to initialize. 
                # Extend the sleep time to 10 seconds in that case        
        time.sleep(self.duration)


class ConnectHardware:

    def __init__(self, port: str, baudrate: int) -> None:
        self.port = port
        self.baudrate = baudrate
        self.ser = None

    def connect(self) -> serial.Serial:
        if (
            CheckPort(self.port).check()
            and CheckPort(self.port).connect()
            and CheckBaudrate(self.baudrate).check()
        ):
            self.ser = serial.Serial(
                self.port, self.baudrate, timeout=1
            )
            SelectBootLoaderDuration(5).select()
            return self.ser
        
    def close(self) -> None: 
        if self.ser and self.ser.is_open:
            self.ser.close()


class CheckSerialConnection:
    
    def __init__(self, ser_connection: serial.Serial) -> None:
        self.ser = ser_connection

    def check(self) -> bool:
        if not self.ser or not self.ser.is_open:
            raise RuntimeError("Serial connection must be open to collect data.")
        return True
    

class GetDataCollectionDuration:

    def __init__(self, duration: int | float) -> None:
        self.duration = duration

    def get(self) -> int | float: 
        if not self.duration > 0:
            raise ValueError("Invalid data collection duration.")
        return self.duration


class CheckValue: 
    def __init__(self, value: str) -> None:
        self.value = value

    def check(self):
        # CONSTANT VALUE IMPUTATION: 
        # We don't want the pipeline to stop.
        # Hence, we will be imputing the mean value obtained in our previous data.
        if not self.value:
            self.value = 512.16

        if not self.value.isdigit(): 
            self.value = 512.16

        return self.value  


class ConvertValue: 
    def __init__(self, value: str) -> None: 
        self.value = value

    def convert(self) -> float:
        return float(self.value) 
    

class DecodeValue:

    def __init__(self, value: str) -> None: 
        self.value = value

    def decode(self) -> str: 
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

            decoded_value = self.value.decode("latin-1", errors="ignore").strip()
            return decoded_value


class AppendData: 
    
    def __init__(self, data: list, current_timestamp: str, value: float) -> None: 
        self.current_timestamp = current_timestamp
        self.value = value
        self.data = data
    
    def append_data(self) -> None: 
        self.data.append(
            {
                "timestamp": self.current_timestamp,
                "value": self.value
            }
        )


class GetLiveBatch:

    def __init__(self, batch_duration: int | float = 2.0) -> None:
        self.batch_duration = batch_duration
        self.batch = []
        self.batch_start_time = time.time()

    def get(self, current_time: str, value: int | float) -> list | None:
        AppendData(self.batch, current_time, value).append_data()

        if time.time() - self.batch_start_time >= self.batch_duration:
            full_batch = self.batch
            self.batch = []  
            self.batch_start_time = time.time()  
            return full_batch

        return None


class GetDataFromHardware:

    def __init__(self, ser_connection: serial.Serial) -> None:
        self.ser = ser_connection

    def get(self):
        start_time = time.time()
        duration = GetDataCollectionDuration(300).get()

        while time.time() - start_time < duration:
            try:
                current_time = datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S.%f"
                )
                value = self.ser.readline()
                value = DecodeValue(value).decode()
                value = CheckValue(value).check()
                value = ConvertValue(value).convert()

                batch = GetLiveBatch(2.0).get(
                    current_time, value
                )
                
                if batch is not None:
                    yield batch

            except serial.SerialException as e:
                raise RuntimeError(
                    f"Serial interface disconnected during data collection: {e}"
                )
            

class IngestHardware: 
    
    def __init__(self, port: str, baudrate: int) -> None:
        self.port = port 
        self.baudrate = baudrate

    def ingest(self) -> list:
        ser_connection = ConnectHardware().connect()
        return GetDataFromHardware(ser_connection).get()

class ReadCsv:

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path

    def read_rows(self):
        with open(self.file_path, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                if row:
                    yield row


class GetCsvBatch:

    def __init__(self, reader_instance: ReadCsv, batch_duration_sec: float = 2.0) -> None:
        self.reader = reader_instance
        self.batch_duration = datetime.timedelta(seconds=batch_duration_sec)

    def get_batches(self):
        current_batch = []
        batch_start_time = None

        for row in self.reader.read_rows():
            timestamp_str, value = row[0], row[1]
            row_time = datetime.datetime.strptime(
                timestamp_str, "%Y-%m-%d %H:%M:%S.%f"
            )

            if batch_start_time is None:
                batch_start_time = row_time

            if row_time - batch_start_time < self.batch_duration:
                current_batch.append((timestamp_str, int(value)))
            else:
                yield current_batch
                current_batch = [(timestamp_str, int(value))]
                batch_start_time = row_time

        if current_batch:
            yield current_batch



class IngestData: 

    def __init__(self, method: str) -> None: 
        # More inputs are needed
        self.method = method.lower()

    def ingest(self) -> None : 
        if self.method == "simulation":
            SimulationIngest()
        elif self.method == "hardware":
            HardwareIngest()
        else : 
            raise ValueError("Choose either simulation or hardware as an option.")

