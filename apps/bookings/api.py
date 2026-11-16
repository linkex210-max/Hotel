from typing import List, Optional
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from ninja import Router, Query
from ninja.errors import HttpError
from .models import Booking
from .schemas import (
    AvailabilityCheckIn,
    AvailableRoomOut,
    BookingIn,
    BookingOut,
)
from .services import (
    get_available_rooms,
    create_booking,
    process_check_in,
    process_check_out,
)

router = Router(tags=["الحجوزات ومحرك التوفر (Bookings)"])

@router.post("/availability", response=List[AvailableRoomOut], summary="محرك التحقق من توفر الغرف وحساب الأسعار")
def check_availability(request, payload: AvailabilityCheckIn):
    """
    يفحص الشواغر لفترة زمنية محددة ويمنع التضارب،
    ويعيد قائمة الغرف مع إجمالي السعر المحسوب لعدد الليالي.
    """
    try:
        return get_available_rooms(
            check_in=payload.check_in,
            check_out=payload.check_out,
            room_type_id=payload.room_type_id,
            guests_count=payload.guests_count,
        )
    except ValidationError as e:
        raise HttpError(400, str(e.message if hasattr(e, 'message') else e))


@router.post("/", response={201: BookingOut}, summary="إنشاء حجز جديد (آمن ومعزول ضد التعارض)")
def make_booking(request, payload: BookingIn):
    """
    إنشاء حجز جديد بعد فحص التعارض وقفل السجل في قاعدة البيانات.
    يولد رمز مرجعي فريد (مثل LX-A1B2C3) يمكن استخدامه لتوليد QR Code.
    """
    try:
        booking = create_booking(
            room_id=payload.room_id,
            guest_name=payload.guest_name,
            guest_email=payload.guest_email,
            guest_phone=payload.guest_phone,
            check_in=payload.check_in,
            check_out=payload.check_out,
            notes=payload.notes or "",
        )
        return 201, booking
    except ValidationError as e:
        raise HttpError(400, str(e.message if hasattr(e, 'message') else e))


@router.get("/", response=List[BookingOut], summary="استعراض قائمة الحجوزات مع الفلترة")
def list_bookings(
    request,
    status: Optional[str] = Query(None, description="حالة الحجز (confirmed, checked_in, checked_out, cancelled)"),
    room_id: Optional[int] = Query(None, description="معرف الغرفة"),
    reference_code: Optional[str] = Query(None, description="رمز الحجز المرجعي"),
):
    """قائمة الحجوزات لمكتب الاستقبال ولوحة التحكم."""
    queryset = Booking.objects.select_related('room', 'room.room_type').all()
    if status:
        queryset = queryset.filter(status=status)
    if room_id:
        queryset = queryset.filter(room_id=room_id)
    if reference_code:
        queryset = queryset.filter(reference_code__iexact=reference_code.strip())
    return queryset


@router.get("/ref/{reference_code}", response=BookingOut, summary="استرجاع الحجز عبر الرمز المرجعي (QR Code / البحث السريع)")
def get_booking_by_reference(request, reference_code: str):
    return get_object_or_404(
        Booking.objects.select_related('room', 'room.room_type'),
        reference_code__iexact=reference_code.strip()
    )


@router.get("/{booking_id}", response=BookingOut, summary="استرجاع تفاصيل الحجز عبر المعرف")
def get_booking(request, booking_id: int):
    return get_object_or_404(
        Booking.objects.select_related('room', 'room.room_type'),
        id=booking_id
    )


@router.post("/{booking_id}/check-in", response=BookingOut, summary="تسجيل الوصول (Check-in)")
def check_in(request, booking_id: int):
    """
    تسجيل وصول النزيل في الاستقبال:
    يغير حالة الحجز إلى checked_in وحالة الغرفة إلى occupied.
    """
    booking = get_object_or_404(Booking.objects.select_related('room', 'room.room_type'), id=booking_id)
    try:
        return process_check_in(booking)
    except ValidationError as e:
        raise HttpError(400, str(e.message if hasattr(e, 'message') else e))


@router.post("/{booking_id}/check-out", response=BookingOut, summary="تسجيل المغادرة (Check-out)")
def check_out(request, booking_id: int):
    """
    تسجيل مغادرة النزيل:
    يغير حالة الحجز إلى checked_out وحالة الغرفة إلى cleaning تمهيداً لتجهيزها.
    """
    booking = get_object_or_404(Booking.objects.select_related('room', 'room.room_type'), id=booking_id)
    try:
        return process_check_out(booking)
    except ValidationError as e:
        raise HttpError(400, str(e.message if hasattr(e, 'message') else e))
