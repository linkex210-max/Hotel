from typing import List, Optional
from django.shortcuts import get_object_or_404
from ninja import Router, Query
from .models import Room, RoomType
from .schemas import RoomOut, RoomTypeOut

router = Router(tags=["الغرف والتصنيفات (Rooms)"])

@router.get("/types", response=List[RoomTypeOut], summary="استعراض جميع تصنيفات الغرف")
def list_room_types(request):
    """قائمة بكافة تصنيفات الغرف ومواصفاتها وأسعارها."""
    return RoomType.objects.all()

@router.get("/types/{type_id}", response=RoomTypeOut, summary="تفاصيل تصنيف محدد")
def get_room_type(request, type_id: int):
    return get_object_or_404(RoomType, id=type_id)

@router.get("/", response=List[RoomOut], summary="استعراض قائمة الغرف مع إمكانية الفلترة")
def list_rooms(
    request,
    room_type_id: Optional[int] = Query(None, description="معرف نوع الغرفة"),
    status: Optional[str] = Query(None, description="حالة الغرفة (available, occupied, maintenance, cleaning)"),
    floor: Optional[int] = Query(None, description="رقم الطابق")
):
    """
    استعراض جميع الغرف مع فلترة اختيارية بحسب النوع، الحالة أو الطابق.
    يستخدم في شاشة الاستقبال وشاشات العرض.
    """
    queryset = Room.objects.select_related('room_type').filter(is_active=True)
    if room_type_id:
        queryset = queryset.filter(room_type_id=room_type_id)
    if status:
        queryset = queryset.filter(status=status)
    if floor:
        queryset = queryset.filter(floor=floor)
    return queryset

@router.get("/{room_id}", response=RoomOut, summary="تفاصيل غرفة محددة")
def get_room(request, room_id: int):
    return get_object_or_404(Room.objects.select_related('room_type'), id=room_id)
