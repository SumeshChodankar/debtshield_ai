from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class Tactic(str, Enum):
    APPEAL_HISTORY = "appeal_history"
    CITE_HARDSHIP = "cite_hardship"
    COMPETING_OFFER = "competing_offer"
    POLITE_REQUEST = "polite_request"
    FIRM_DEMAND = "firm_demand"

class Observation(BaseModel):
    turn: int
    current_apr: float
    current_fee: float
    balance: float
    monthly_min: float
    creditor_mood: str 
    last_creditor_message: str

class Action(BaseModel):
    thought_process: str = Field(..., description="Internal reasoning before the message")
    tactic: Tactic
    requested_apr: Optional[float] = None
    requested_fee: Optional[float] = None
    message: str = Field(..., description="The actual text sent to the creditor")

class Reward(BaseModel):
    score: float
    details: str