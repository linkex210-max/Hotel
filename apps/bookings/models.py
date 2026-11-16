import uuid
import secrets
from django.db import models
from apps.rooms.models import Room

def generate_booking_reference():
    return f"LX-{secrets.token_hex(3).upper()}"

class Booking(models.Model):
    class Status(models.TextChoices):
        CONFIRMED = 'confirmed', 'مؤكد'
        CHECKED_IN = 'checked_in', 'تم تسجيل الوصول'
        CHECKED_OUT = 'checked_out', 'تم تسجيل المغادرة'
        CANCELLED = 'cancelled', 'ملغي'

    reference_code = models.CharField(
        max_length=20,
        unique=True,
        default=generate_booking_reference,
        verbose_name="رمز الحجز المرجعي"
    )
    room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name='bookings', verbose_name="الغرفة")
    guest_name = models.CharField(max_length=150, verbose_name="اسم النزيل")
    guest_email = models.EmailField(verbose_name="البريد الإلكتروني")
    guest_phone = models.CharField(max_length=30, verbose_name="رقم الهاتف")
    check_in = models.DateField(verbose_name="تاريخ الوصول")
    check_out = models.DateField(verbose_name="تاريخ المغادرة")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="إجمالي المبلغ")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CONFIRMED, verbose_name="حالة الحجز")
    notes = models.TextField(blank=True, verbose_name="ملاحظات إضافية")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        verbose_name = "حجز"
        verbose_name_plural = "الحجوزات"
        ordering = ['-created_at']

    def __str__(self):
        return f"حجز {self.reference_code} - {self.guest_name} (غرفة {self.room.room_number})"
