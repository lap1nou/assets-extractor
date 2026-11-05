from pydantic import BaseModel, Field

class Account(BaseModel):
    username: str
    domain: str | None        # no default -> required (but can be null)
    host: str | None
    password: str | None
    hash: str | None

class Host(BaseModel):
    ip: str = Field(description="ip address of the host")
    hostname: str | None = Field(default="", description="hostname of the host, if present")

class MissionAssets(BaseModel):
    accounts: list[Account]

class ImageAssets(BaseModel):
    transcript: str
    assets: list[Host]
    accounts: list[Account]

SCHEMA = MissionAssets.model_json_schema()