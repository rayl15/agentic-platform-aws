from pydantic import BaseModel

class WeatherReport(BaseModel):
    location: str

# This function takes in the arguments defined as a pydantic model.
def weather_report(input_data: WeatherReport) -> str:
    """Weather report tool"""    
    # NOTE: In a real implementation, we'd call an external API here.
    result = f"The weather is sunny and 70 degrees in {input_data.location}."
    return result