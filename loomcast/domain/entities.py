from __future__ import annotations

from enum import Enum
from typing import Any

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
    size_bytes: int | None = None
    modified_at: str | None = None
    digest: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)


class CatalogEntry(BaseModel):
    """Pure domain entity representing a model catalog entry."""

    name: str
    description: str | None = None
    publisher: str | None = None
    tags: list[str] = Field(default_factory=list)
    default_runtime: RuntimeType | None = None


class ChatMessage(BaseModel):
    """Pure domain entity representing a chat message."""

    role: str
    content: str


class VerificationResult(BaseModel):
    """Pure domain entity representing the verification result of a model."""

    model: str
    runtime_type: RuntimeType
    verified: bool
    digest: str | None = None
    message: str
