from typing import Any, Dict

from pydantic import BaseModel, Field


class Message(BaseModel):
    fromRole: str = ""
    fromName: str = ""
    toRole: str = ""
    toName: str = ""
    body: str = ""
    read: bool = False
    createdAt: str = ""
    readAt: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)
