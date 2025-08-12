from pydantic import BaseModel

from app.schemas.attendance import StatusOptions


class MarkPresenceData(BaseModel):
    status: StatusOptions
