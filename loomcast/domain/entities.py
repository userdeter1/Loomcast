from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class RuntimeType(str, Enum):
    """Supported local LLM runtime backends."""
    OLLAMA = "ollama"
    LMSTUDIO = "lmstudio"
    LLAMACPP = "llamacpp"


class Model(BaseModel):
    """Pure domain entity representing an LLM model."""
    name: str
    runtime_type: RuntimeType
    size_bytes: Optional[int] = None
    modified_at: Optional[str] = None
    digest: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)


class CatalogEntry(BaseModel):
    """Pure domain entity representing a model catalog entry."""
    name: str
    description: Optional[str] = None
    publisher: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    default_runtime: Optional[RuntimeType] = None


class ChatMessage(BaseModel):
    """Pure domain entity representing a chat message."""
    role: str
    content: str


class VerificationResult(BaseModel):
    """Pure domain entity representing the verification result of a model."""
    model: str
    runtime_type: RuntimeType
    verified: bool
    digest: Optional[str] = None
    message: str

