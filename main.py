from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
import os
from geolocation_service import GeolocationService
from config import config

app = FastAPI(title="Store Coverage API", version="1.0.0")

# Initialize the geolocation service
geo_service = GeolocationService()

class LocationRequest(BaseModel):
    latitude: float
    longitude: float
    company_id: str
    store_id: Optional[str] = None

class LocationResponse(BaseModel):
    store_id: str
    region_name: str
    company_id: str

@app.get("/")
async def root():
    return {"message": "Store Coverage API - Use /check-coverage endpoint"}

@app.post("/check-coverage")
async def check_coverage(request: LocationRequest):
    """
    Check if a geolocation is covered by a store.
    
    - If store_id is not provided: returns the first store that covers the location
    - If store_id is provided: returns the store_id if it covers the location, otherwise 404
    """
    try:
        result = geo_service.check_coverage(
            latitude=request.latitude,
            longitude=request.longitude,
            company_id=request.company_id,
            store_id=request.store_id
        )
        
        if result is None:
            raise HTTPException(status_code=404, detail="Location not covered by any store")
        
        return LocationResponse(**result)
    
    except HTTPException as e:
        # Deixe o FastAPI tratar HTTPException normalmente
        raise e
    except Exception as e:
        import traceback
        print("Erro interno:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/check-coverage")
async def check_coverage_get(
    latitude: float = Query(..., description="Latitude coordinate"),
    longitude: float = Query(..., description="Longitude coordinate"),
    company_id: str = Query(..., description="Company ID"),
    store_id: Optional[str] = Query(None, description="Optional store ID")
):
    """
    GET version of check-coverage endpoint for easier testing
    """
    request = LocationRequest(
        latitude=latitude,
        longitude=longitude,
        company_id=company_id,
        store_id=store_id
    )
    return await check_coverage(request)

