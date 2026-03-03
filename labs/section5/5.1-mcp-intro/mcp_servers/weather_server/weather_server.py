from typing import Dict, Any
import requests
from mcp.server.fastmcp import FastMCP
import logging

class WeatherToolServer:
    """A simple MCP server providing weather-related tools."""
    
    def __init__(self, name="weather"):
        self.mcp = FastMCP(name)
        self.API_BASE = "https://api.weather.gov"
        self._register_tools()
    
    def _make_request(self, url: str) -> Dict[str, Any]:
        """Make a request to the weather API."""
        headers = {"User-Agent": "weather-app/1.0", "Accept": "application/geo+json"}
        try:
            logging.debug(f"Making request to {url}")
            response = requests.get(url, headers=headers, timeout=10.0)
            response.raise_for_status()
            logging.debug(f"Response status: {response.status_code}")
            return response.json()
        except Exception as e:
            logging.error(f"Error in API request: {str(e)}")
            return {}
    
    def _register_tools(self):
        """Register all weather tools with the MCP server."""
        
        @self.mcp.tool()
        def get_alerts(state: str) -> str:
            """Get weather alerts for a US state.
            
            Args:
                state: Two-letter US state code (e.g. CA, NY)
            """
            data = self._make_request(f"{self.API_BASE}/alerts/active/area/{state}")
            
            if not data.get("features"):
                return "No active alerts for this state."
                
            alerts = []
            for feature in data["features"]:
                props = feature["properties"]
                alerts.append(f"Event: {props.get('event')}\nArea: {props.get('areaDesc')}\nSeverity: {props.get('severity')}")
            
            return "\n---\n".join(alerts)
        
        @self.mcp.tool()
        def get_forecast(latitude: float, longitude: float) -> str:
            """Get weather forecast for a location.
            
            Args:
                latitude: Latitude of the location
                longitude: Longitude of the location
            """
            # Get points data and extract forecast URL
            points_data = self._make_request(f"{self.API_BASE}/points/{latitude},{longitude}")
            if not points_data:
                return "Unable to fetch forecast data for this location."
                
            forecast_url = points_data.get("properties", {}).get("forecast", "")
            if not forecast_url:
                return "Forecast URL not available."
                
            # Get the actual forecast
            forecast_data = self._make_request(forecast_url)
            if not forecast_data:
                return "Unable to fetch forecast."
                
            # Format just the essential information
            result = []
            for period in forecast_data.get("properties", {}).get("periods", [])[:3]:
                result.append(f"{period['name']}: {period['temperature']}°{period['temperatureUnit']}, {period['shortForecast']}")
                
            return "\n".join(result)
    
    def get_server(self):
        """Return the configured MCP server."""
        print('Returning server to start MCP client')
        return self.mcp

# Export the server as a common name for inspector to pick it up.
app: FastMCP = WeatherToolServer().get_server()

if __name__ == "__main__":
    app.run(transport="stdio")