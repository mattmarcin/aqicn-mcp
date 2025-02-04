from typing import Optional
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel
import httpx
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
AQICN_API_KEY = os.environ.get("AQICN_API_KEY")
if not AQICN_API_KEY:
    raise ValueError("AQICN_API_KEY environment variable is not set. Create a .env file or set it in your environment.")

AQICN_BASE_URL = "https://api.waqi.info"

# Response models
class AQIData(BaseModel):
    aqi: int
    station: str
    dominant_pollutant: Optional[str] = None
    time: str
    coordinates: dict

class StationInfo(BaseModel):
    name: str
    station_id: str
    coordinates: dict

# Create an MCP server
mcp = FastMCP("AQICN Air Quality API")

@mcp.tool()
def city_aqi(city: str) -> AQIData:
    """Get air quality data for a specific city."""
    url = f"{AQICN_BASE_URL}/feed/{city}/?token={AQICN_API_KEY}"
    
    with httpx.Client() as client:
        response = client.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data["status"] != "ok":
            raise Exception(f"Error fetching data: {data.get('data')}")
            
        result = data["data"]
        return AQIData(
            aqi=result["aqi"],
            station=result["city"]["name"],
            dominant_pollutant=result.get("dominentpol"),
            time=result["time"]["s"],
            coordinates={
                "lat": result["city"]["geo"][0],
                "lon": result["city"]["geo"][1]
            }
        )

@mcp.tool()
def geo_aqi(latitude: float, longitude: float) -> AQIData:
    """Get air quality data for a specific location using coordinates."""
    url = f"{AQICN_BASE_URL}/feed/geo:{latitude};{longitude}/?token={AQICN_API_KEY}"
    
    with httpx.Client() as client:
        response = client.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data["status"] != "ok":
            raise Exception(f"Error fetching data: {data.get('data')}")
            
        result = data["data"]
        return AQIData(
            aqi=result["aqi"],
            station=result["city"]["name"],
            dominant_pollutant=result.get("dominentpol"),
            time=result["time"]["s"],
            coordinates={
                "lat": result["city"]["geo"][0],
                "lon": result["city"]["geo"][1]
            }
        )

@mcp.tool()
def search_station(keyword: str) -> list[StationInfo]:
    """Search for air quality monitoring stations by keyword."""
    url = f"{AQICN_BASE_URL}/search/?token={AQICN_API_KEY}&keyword={keyword}"
    
    with httpx.Client() as client:
        response = client.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data["status"] != "ok":
            raise Exception(f"Error searching stations: {data.get('data')}")
        
        stations = []
        for station in data["data"]:
            stations.append(StationInfo(
                name=station["station"]["name"],
                station_id=str(station["uid"]),
                coordinates={
                    "lat": station["station"]["geo"][0],
                    "lon": station["station"]["geo"][1]
                }
            ))
        return stations

if __name__ == "__main__":
    mcp.run() 