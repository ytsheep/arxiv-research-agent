from pydantic import BaseModel


class UserPreferenceItem(BaseModel):
    key: str
    value: str


class UserPreferencesResponse(BaseModel):
    success: bool = True
    preferences: dict = {}
