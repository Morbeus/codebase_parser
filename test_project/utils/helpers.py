from config.settings import DEBUG
import sys
from typing import Union, Optional

# Conditional import
if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

def calculate_sum(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """Calculate the sum of two numbers."""
    if DEBUG:
        print(f"Calculating sum of {a} and {b}")
    return a + b

def calculate_product(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """Calculate the product of two numbers."""
    if DEBUG:
        print(f"Calculating product of {a} and {b}")
    return a * b

# Type alias export
Number = Union[int, float]

# Dynamic function creation
def create_operation(operation: Literal["add", "multiply"]) -> callable:
    """Dynamically create an operation function."""
    if operation == "add":
        return calculate_sum
    return calculate_product 