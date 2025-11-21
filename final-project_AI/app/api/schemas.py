from typing import Dict, List
from pydantic import BaseModel, Field


class UploadIn(BaseModel):
    pdf_id: int = Field(alias="productId")
    fileUrl: str


class ChatIn(BaseModel):
    pdf_id: int = Field(alias="productId")
    question: str
    chatMessage: List[Dict[str, str]] = Field(default_factory=list, alias="messages")