from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, EmailStr


class PlanRequest(BaseModel):
    email_id: EmailStr = Field(..., description="User email for storing travel plan")
    city: str = Field(..., min_length=2, max_length=80)
    check_in: date
    check_out: date
    adults: int = Field(default=2, ge=1, le=10)
    budget_amount: float = Field(default=50000, ge=0)
    budget_currency: str = Field(default="INR", min_length=3, max_length=3)
    style: str = Field(default="balanced", description="balanced, luxury, foodie, culture")


class PlanResponse(BaseModel):
    email_id: str
    destination: str
    check_in: Optional[str] = None
    check_out: Optional[str] = None
    weather: str
    hotels: str
    restaurants: str
    attractions: str
    currency: str
    itinerary: str
    budget_optimizer: str
    final_response: str
    generated_at: str
    warning: Optional[str] = None


class ChatRequest(BaseModel):
    email_id: EmailStr = Field(..., description="User email to fetch travel plan")
    message: str = Field(..., min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    email_id: str
    user_message: str
    bot_response: str
