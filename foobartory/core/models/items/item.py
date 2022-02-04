import uuid

from pydantic import BaseModel


class Item(BaseModel):
    id = uuid.uuid4()
