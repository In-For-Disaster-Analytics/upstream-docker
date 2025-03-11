from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field, validator


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None
