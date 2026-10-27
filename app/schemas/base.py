from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    """Response schema that can be built straight from a database model."""

    model_config = ConfigDict(from_attributes=True)
