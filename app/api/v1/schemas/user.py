from pydantic import BaseModel, validator, Field
from datetime import datetime
from typing import Any, Optional, List

class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None

