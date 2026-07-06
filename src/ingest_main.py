
from abc import ABC, abstractmethod
from typing import Dict, Type, Any
import serial.tools.list_ports
import time 

class AnyIngest(ABC):
    @abstractmethod
    def ingest(self) -> None:
        pass


class SimulationIngest(AnyIngest):
    EXPECTED_PARAMS = "None"
    def __init__(self) -> None:
        pass

    def ingest(self) -> None:
        pass


class HardwareIngest(AnyIngest):
    EXPECTED_PARAMS = "port (str), baud_rate (int)"
    def __init__(self, port: str, baud_rate: int) -> None:
        self.port = port
        self.baud_rate = baud_rate

    def ingest(self) -> None:
        available_ports = [p.device for p in serial.tools.list_ports.comports()]
        #_check_input("port", self.port, available_ports, [str])
        
        available_baudrates = [
            50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800,
            9600, 19200, 28800, 38400, 57600, 76800, 115200, 230400,
            460800, 576000, 921600
        ]
        _check_input("baudrate", self.baud_rate, available_baudrates, [int])
        _set_bootloader("s")


class DataIngest:
    _REGISTRY: Dict[str, Type[AnyIngest]] = {
        "simulation": SimulationIngest,
        "hardware": HardwareIngest
    }

    @classmethod
    def ingest(cls, method: str, **kwargs) -> None:
        cleaned_method = _clean_string(method)
        available_methods = list(cls._REGISTRY.keys())
        # GAME INTERFACE HAS TWO CHOICES: 
            # 1] Simulation (If user doesn't have hardware setup)
            # 2] Hardware (If user has hardware setup)
        _check_input("method", cleaned_method, available_methods, [str])
        
        worker_class = cls._REGISTRY[cleaned_method]
        
        try:
            ingest_class = worker_class(**kwargs)
            ingest_class.ingest() 
        except TypeError as e:
            expected_params = getattr(worker_class, "EXPECTED_PARAMS", "Not specified")    
            raise TypeError(
                f"Invalid arguments passed for '{worker_class.__name__}'.\n"
                f"Expected Parameters: {expected_params}\n"
            ) from e


def _clean_string(method_name: str) -> str:
    return method_name.lower().strip()


def _check_input(
        input_name: str, 
        input_val, 
        is_empty_allowed: bool,
        allowed_inputs: list, 
        allowed_dtypes: list, 
        min_val: int | float,
        max_val: int | float
        ) -> None: 
    # how to make allowed inputs optional here.
    if (input_val is None or input_val == "") and (is_empty_allowed == False): 
        raise ValueError(f"{input_name} cannot be empty!")
    
    if len(allowed_dtypes):
        if not isinstance(input_val, tuple(allowed_dtypes)):
            _display_valid_inputs(input_name, allowed_dtypes)
            raise TypeError(f"{input_name} has invalid data type. FOR VALID DATA-TYPES SCROLL UP.")
    
    clean_input = _clean_string(input_val) if isinstance(input_val, str) else input_val
    
    if len(allowed_inputs): 
        clean_allowed_inputs = [_clean_string(x) if isinstance(x, str) else x for x in allowed_inputs]

        if clean_input not in clean_allowed_inputs: 
            _display_valid_inputs(input_name, allowed_inputs)
            raise ValueError(f"'{input_val}' is invalid {input_name}.")

#--------------------------CHECK EMPTY INPUT-----------------------------#

def _handle_empty_input(
    input_name: str, 
    input_value: Any, 
    is_empty_allowed: bool, 
    default_input_value: Any = None
) -> Any: 
    
    if input_value is not None:
        return input_value

    if is_empty_allowed:
        return default_input_value
        
    raise ValueError(f"'{input_name}' cannot be empty or None!")
        

#--------------------------CHECK DATA RANGE-----------------------------#

def _handle_input_range(
    input_name: str, 
    input_value: int | float , 
    min_input_value: int | float,
    max_input_value: int | float
) -> int | float:
    
    if  min_input_value <= input_value <= max_input_value: 
        return input_value

    if input_value < min_input_value: 
        raise ValueError(f"Minimum {input_name} should be {min_input_value}.")
    
    raise ValueError(f"Maximum {input_name} should be {max_input_value}.")


#--------------------------CHECK ALLOWED INPUT VALUES-----------------------------#
    



#--------------------------CHECK INPUT-----------------------------#

def _check_input(
        input_name: str, 
        input_value, 
        is_empty_allowed: bool,
        allowed_inputs: list, 
        allowed_dtypes: list, 
        min_val: int | float,
        max_val: int | float,
        default_input_value: Any
        ) -> None: 
    
    non_empty_input_value = _handle_empty_input(
        input_name,
        input_value,
        is_empty_allowed,
        default_input_value
    )
    # Assuming the user's input data type is right !
    valid_input_value = _handle_input_validity(

    )
    
    if len(allowed_dtypes):
        if not isinstance(input_val, tuple(allowed_dtypes)):
            _display_valid_inputs(input_name, allowed_dtypes)
            raise TypeError(f"{input_name} has invalid data type. FOR VALID DATA-TYPES SCROLL UP.")
    
    clean_input = _clean_string(input_val) if isinstance(input_val, str) else input_val
    
    if len(allowed_inputs): 
        clean_allowed_inputs = [_clean_string(x) if isinstance(x, str) else x for x in allowed_inputs]

        if clean_input not in clean_allowed_inputs: 
            _display_valid_inputs(input_name, allowed_inputs)
            raise ValueError(f"'{input_val}' is invalid {input_name}.")
        








def _display_valid_inputs(input_name: str, allowed_inputs: list) -> None:
    if allowed_inputs and isinstance(allowed_inputs[0], type):
        print(f"Allowed {input_name} data types:")
    else:
        print(f"Available {input_name}s:")
    for i, allowed_input in enumerate(allowed_inputs):
        if isinstance(allowed_input, type):
            print(f"{i+1}] {allowed_input.__name__}")
        else:
            print(f"{i+1}] {allowed_input}")


def _set_boot_loader_duration(boot_init_duration: int | float) -> None: 
    # BOOTLOADER INTIALIZATION TIME:          
            # 1] FOR MODERN ARDUINO:
                # Modern Arduino's bootloader normally finishes initializing in 1 to 2 seconds
                # 5-second delay is implemented as a safety margin.
            # 2] FOR OLDER ARDUINO:
                # Older Arduino's bootloader might take around 4 to 8 seconds to initialize. 
                # Extend the sleep time to 10 seconds in that case
    
    input_name = "bootloader initialization duration"
    _check_input(input_name, boot_init_duration, )
    if not boot_init_duration: 
        boot_init_duration =  10.0
   # How will you deal with range ? 
    if boot_init_duration < 5.0: 
        raise ValueError("Minimum {input_name} should be 5 seconds.")
        
    time.sleep(boot_init_duration)

if __name__ == "__main__":
    try:
        DataIngest.ingest("hardware", port="COM6", baud_rate=115200)
    except Exception as e:
        print(e)