from pydantic import BaseModel
from enum import Enum
class Operation(str, Enum):
    add = "add"
    subtract = "subtract"
    multiply = "multiply"
    divide = "divide"

class Calculator(BaseModel):
    x: float
    y: float
    operation: str

def handle_calculation(input_data: Calculator) -> str:
    """Process the calculation request and return a result"""
    x = input_data.x
    y = input_data.y

    operator: Operation = input_data.operation
    
    if operator == 'add':
        result = x + y
    elif operator == 'subtract':
        result = x - y
    elif operator == 'multiply':
        result = x * y
    elif operator == 'divide':
        result = x / y if y != 0 else 'Error: Division by zero'
    
    return result