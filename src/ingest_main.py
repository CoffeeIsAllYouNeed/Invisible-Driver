

# ===============================================

class DataIngest:
    # There is no input needed for simulation only hardware needs input 
    # Add them as we go ahead 
    def ingest(method_name: str) -> None:
        _check_method_input(method_name)


# ===============================================

def _clean_name(method_name: str) -> str:
    # Reuse whenever needed
    cleaned_method_name = method_name.lower().strip()
    return cleaned_method_name

# ===============================================

def _check_method_input(method_name: str) -> bool:
    # Create a general class out of this 
    cleaned_method_name = _clean_name(method_name)
    if not cleaned_method_name:
        raise ValueError("Method cannot be empty!")
    
    available_methods = ["simulation", "hardware"]
    if cleaned_method_name not in available_methods:
        raise ValueError(
            f"'{method_name}' is not a valid method.\n"
            "AVAILABLE METHODS:\n"
            "1) simulation\n"
            "2) hardware"
        )
    return True

# ===============================================
    



