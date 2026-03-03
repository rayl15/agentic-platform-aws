from enum import Enum
from pydantic import BaseModel

class Operation(str, Enum):
    add = "add"
    subtract = "subtract"
    multiply = "multiply"
    divide = "divide"

class Calculator(BaseModel):
    operation: Operation
    x: float
    y: float

class WeatherReportInput(BaseModel):
    location: str

# This function takes in the arguments defined as a pydantic model.
def weather_report(input: WeatherReportInput) -> str:
    """Weather report tool"""    
    
    # NOTE: In a real implementation, we'd call an external API here.
    return "The weather is sunny and 70 degrees."

def handle_calculation(args: Calculator) -> float:
    """Process the calculation request and return a result"""
    x = args.x
    y = args.y

    operator: Operation = args.operation
    
    if operator == 'add':
        result = x + y
    elif operator == 'subtract':
        result = x - y
    elif operator == 'multiply':
        result = x * y
    elif operator == 'divide':
        result = x / y if y != 0 else 'Error: Division by zero'

    return result