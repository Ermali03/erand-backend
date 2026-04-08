from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    roles: list[str]
    email: str

class TokenPayload(BaseModel):
    sub: str | None = None
    role: str | None = None
    roles: list[str] | None = None
