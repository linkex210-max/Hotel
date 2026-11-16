from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from ninja import Schema
from apps.rooms.schemas import RoomTypeOut

class AvailabilityCheckIn(Schema):
    check_in: date
    check_out: date
    room_type_id: Optional[int] = None
    guests_count: Optional[int] = None

class AvailableRoomOut(Schema):
    id: int
    room_number: str
    floor: int
    room_type: RoomTypeOut
    total_nights: int
    total_price: Decimal

class BookingIn(Schema):
    room_id: int
    guest_name: str
    guest_email: str
    guest_phone: str
    check_in: date
    check_out: date
    notes: Optional[str] = ""

class BookingOut(Schema):
    id: int
    reference_code: str
    room_id: int
    room_number: str
    room_type_name: str
    guest_name: str
    guest_email: str
    guest_phone: str
    check_in: date
    check_out: date
    total_nights: int
    total_price: Decimal
    status: str
    notes: Optional[str] = ""
    created_at: datetime

    @staticmethod
    def resolve_room_number(obj):
        return obj.room.room_number

    @staticmethod
    def resolve_room_type_name(obj):
        return obj.room.room_type.name

    @staticmethod
    def resolve_total_nights(obj):
        return (obj.check_out - obj.check_in).days
