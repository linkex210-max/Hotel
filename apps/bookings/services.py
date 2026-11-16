from datetime import date
from decimal import Decimal
from typing import Optional, List, Dict, Any
from django.db import transaction
from django.core.exceptions import ValidationError
from apps.rooms.models import Room
from .models import Booking

def validate_dates(check_in: date, check_out: date) -> int:
    """التحقق من صحة تواريخ الحجز وحساب عدد الليالي."""
    if check_out <= check_in:
        raise ValidationError("تاريخ المغادرة يجب أن يكون بعد تاريخ الوصول.")
    nights = (check_out - check_in).days
    if nights <= 0:
        raise ValidationError("مدة الإقامة يجب أن تكون ليلة واحدة على الأقل.")
    return nights


def get_available_rooms(
    check_in: date,
    check_out: date,
    room_type_id: Optional[int] = None,
    guests_count: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    محرك فحص التوفر:
    خوارزمية كشف تداخل الفترات الزمنية لمنع التعارض المزدوج:
    [start_a < end_b AND end_a > start_b]
    """
    nights = validate_dates(check_in, check_out)

    # الغرف المحجوزة في نفس الفترة (الحجوزات المؤكدة أو المقيمة)
    booked_room_ids = Booking.objects.filter(
        status__in=[Booking.Status.CONFIRMED, Booking.Status.CHECKED_IN],
        check_in__lt=check_out,
        check_out__gt=check_in,
    ).values_list('room_id', flat=True)

    rooms_qs = Room.objects.select_related('room_type').filter(
        is_active=True
    ).exclude(
        id__in=booked_room_ids
    ).exclude(
        status=Room.Status.MAINTENANCE
    )

    if room_type_id:
        rooms_qs = rooms_qs.filter(room_type_id=room_type_id)

    if guests_count:
        rooms_qs = rooms_qs.filter(room_type__capacity__gte=guests_count)

    result = []
    for room in rooms_qs:
        total_price = room.room_type.price_per_night * Decimal(nights)
        result.append({
            "id": room.id,
            "room_number": room.room_number,
            "floor": room.floor,
            "room_type": room.room_type,
            "total_nights": nights,
            "total_price": total_price,
        })
    return result


def is_room_available(room_id: int, check_in: date, check_out: date) -> bool:
    """التحقق مما إذا كانت غرفة محددة شاغرة خلال الفترة المطلوبة."""
    validate_dates(check_in, check_out)
    conflict_exists = Booking.objects.filter(
        room_id=room_id,
        status__in=[Booking.Status.CONFIRMED, Booking.Status.CHECKED_IN],
        check_in__lt=check_out,
        check_out__gt=check_in,
    ).exists()
    return not conflict_exists


@transaction.atomic
def create_booking(
    room_id: int,
    guest_name: str,
    guest_email: str,
    guest_phone: str,
    check_in: date,
    check_out: date,
    notes: str = ""
) -> Booking:
    """
    إنشاء حجز بأمان عالي (Atomic Transaction مع قفل الصف لمنع race condition):
    يمنع الحجز المزدوج حتى في حالات الطلبات المتزامنة في نفس اللحظة.
    """
    nights = validate_dates(check_in, check_out)

    # قفل الغرفة أثناء المعاملة لمنع أي طلب متزامن
    room = Room.objects.select_for_update().select_related('room_type').filter(id=room_id, is_active=True).first()
    if not room:
        raise ValidationError("الغرفة المطلوبة غير موجودة أو غير نشطة.")

    if room.status == Room.Status.MAINTENANCE:
        raise ValidationError("الغرفة تحت الصيانة حالياً ولا يمكن حجزها.")

    # إعادة التحقق داخل نطاق القفل
    has_conflict = Booking.objects.filter(
        room_id=room.id,
        status__in=[Booking.Status.CONFIRMED, Booking.Status.CHECKED_IN],
        check_in__lt=check_out,
        check_out__gt=check_in,
    ).exists()

    if has_conflict:
        raise ValidationError("عذراً، الغرفة لم تعد متاحة للتواريخ المحددة (تعارض في الحجز).")

    total_price = room.room_type.price_per_night * Decimal(nights)

    booking = Booking.objects.create(
        room=room,
        guest_name=guest_name.strip(),
        guest_email=guest_email.strip().lower(),
        guest_phone=guest_phone.strip(),
        check_in=check_in,
        check_out=check_out,
        total_price=total_price,
        status=Booking.Status.CONFIRMED,
        notes=notes.strip() if notes else ""
    )
    return booking


@transaction.atomic
def process_check_in(booking: Booking) -> Booking:
    """تسجيل دخول النزيل وتحديث حالة الغرفة إلى مشغولة."""
    if booking.status != Booking.Status.CONFIRMED:
        raise ValidationError(f"لا يمكن تسجيل الوصول لحجز بحالة: {booking.get_status_display()}")
    
    booking.status = Booking.Status.CHECKED_IN
    booking.save(update_fields=['status', 'updated_at'])

    booking.room.status = Room.Status.OCCUPIED
    booking.room.save(update_fields=['status'])
    return booking


@transaction.atomic
def process_check_out(booking: Booking) -> Booking:
    """تسجيل خروج النزيل وتحديث حالة الغرفة إلى تنظيف."""
    if booking.status != Booking.Status.CHECKED_IN:
        raise ValidationError(f"لا يمكن تسجيل المغادرة لحجز بحالة: {booking.get_status_display()}")

    booking.status = Booking.Status.CHECKED_OUT
    booking.save(update_fields=['status', 'updated_at'])

    booking.room.status = Room.Status.CLEANING
    booking.room.save(update_fields=['status'])
    return booking
