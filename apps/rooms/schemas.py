from typing import List, Optional
from decimal import Decimal
from ninja import Schema

class RoomTypeOut(Schema):
    id: int
    name: str
    description: str
    price_per_night: Decimal
    capacity: int
    amenities: List[str] = []
    image_url: Optional[str] = ""

class RoomOut(Schema):
    id: int
    room_number: str
    floor: int
    status: str
    is_active: bool
    room_type: RoomTypeOut

class RoomBriefOut(Schema):
    id: int
    room_number: str
    floor: int
    status: str
    room_type_id: int
    room_type_name: str
    price_per_night: Decimal
