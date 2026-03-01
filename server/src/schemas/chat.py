from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    date: Optional[date] = None


class GenerateRequest(BaseModel):
    date: date


class GenerateResponse(BaseModel):
    message: str
    chat_id: str


class ChatResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    date: Optional[date]
    trigger: str
    llm_model: str
    total_input_tokens: int
    total_output_tokens: int
    created_at: datetime
