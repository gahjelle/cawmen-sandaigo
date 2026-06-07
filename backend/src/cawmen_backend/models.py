"""Shared Pydantic base model."""

from pydantic import BaseModel, ConfigDict


class FrozenModel(BaseModel):
    """Base model that forbids unknown fields and is frozen once built."""

    model_config = ConfigDict(extra="forbid", frozen=True)
