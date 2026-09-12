from pydantic import BaseModel, Field, EmailStr


class CreateAccountSchema(BaseModel):
    email: EmailStr = Field(max_length=128)
    password: str = Field(min_length=4, max_length=64)
