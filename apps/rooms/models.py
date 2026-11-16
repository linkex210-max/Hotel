from django.db import models

class RoomType(models.Model):
    name = models.CharField(max_length=100, verbose_name="اسم التصنيف")
    description = models.TextField(blank=True, verbose_name="الوصف")
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="السعر لليلة الواحدة")
    capacity = models.PositiveIntegerField(default=2, verbose_name="سعة النزلاء")
    amenities = models.JSONField(default=list, blank=True, verbose_name="المميزات والخدمات")
    image_url = models.CharField(max_length=500, blank=True, default="", verbose_name="رابط الصورة")

    class Meta:
        verbose_name = "تصنيف غرفة"
        verbose_name_plural = "تصنيفات الغرف"

    def __str__(self):
        return f"{self.name} - {self.price_per_night} ريال/ليلة"


class Room(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = 'available', 'متاحة'
        OCCUPIED = 'occupied', 'مشغولة'
        MAINTENANCE = 'maintenance', 'صيانة'
        CLEANING = 'cleaning', 'تنظيف'

    room_number = models.CharField(max_length=20, unique=True, verbose_name="رقم الغرفة")
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='rooms', verbose_name="نوع الغرفة")
    floor = models.PositiveIntegerField(default=1, verbose_name="الطابق")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE, verbose_name="الحالة")
    is_active = models.BooleanField(default=True, verbose_name="نشطة")

    class Meta:
        verbose_name = "غرفة"
        verbose_name_plural = "الغرف"
        ordering = ['room_number']

    def __str__(self):
        return f"غرفة {self.room_number} ({self.room_type.name}) - {self.get_status_display()}"
