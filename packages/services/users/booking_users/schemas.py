from pydantic import BaseModel


class LoginResponse(BaseModel):
    token: str
    token_type: str = "bearer"
