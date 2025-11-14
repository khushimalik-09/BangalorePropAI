from pydantic import BaseModel, Field

class PredictRequest(BaseModel):
    total_sqft: float = Field(..., gt=0, description="Total area in sqft")
    bhk: int = Field(..., ge=1, le=10, description="BHK count")
    bath: int = Field(..., ge=0, le=10, description="Bathroom count")
    location: str

class PredictResponse(BaseModel):
    predicted_price_lakhs: float
    model_version: str
    input: PredictRequest
