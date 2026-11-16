from decimal import Decimal
from django.core.management.base import BaseCommand
from apps.rooms.models import RoomType, Room

class Command(BaseCommand):
    help = "إضافة بيانات أولية للغرف والتصنيفات للاختبار والتطوير"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("🌱 بدء إضافة البيانات الأولية..."))

        types_data = [
            {
                "name": "غرفة فردية قياسية (Standard Single)",
                "description": "غرفة مريحة مناسبة لرجال الأعمال والمسافرين الفرديين.",
                "price_per_night": Decimal("150.00"),
                "capacity": 1,
                "amenities": ["واي فاي سريع", "سرير فردي مريح", "مكتب عمل", "تلفاز ذكي"],
                "image_url": "https://images.unsplash.com/photo-1631049307264-da0ec9d70304?auto=format&fit=crop&w=600&q=80"
            },
            {
                "name": "غرفة مزدوجة ديلوكس (Deluxe Double)",
                "description": "غرفة واسعة مجهزة بسرير كينج وإطلالة جميلة على المدينة.",
                "price_per_night": Decimal("280.00"),
                "capacity": 2,
                "amenities": ["واي فاي سريع", "سرير كينج", "شرفة خاصة", "ميني بار", "ماكينة قهوة"],
                "image_url": "https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&w=600&q=80"
            },
            {
                "name": "جناح عائلي فاخر (Executive Family Suite)",
                "description": "جناح متكامل يضم غرفتي نوم وصالة معيشة مع كافة وسائل الراحة.",
                "price_per_night": Decimal("520.00"),
                "capacity": 4,
                "amenities": ["سريران كينج", "صالة معيشة منفصلة", "خدمة غرف VIP", "حمام جاكوزي", "إطلالة بانورامية"],
                "image_url": "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=600&q=80"
            }
        ]

        room_types = {}
        for t in types_data:
            obj, created = RoomType.objects.get_or_create(
                name=t["name"],
                defaults=t
            )
            room_types[t["name"]] = obj
            action = "تم إنشاء" if created else "موجود مسبقاً"
            self.stdout.write(f"  - {action}: {obj.name}")

        rooms_seed = [
            ("101", room_types["غرفة فردية قياسية (Standard Single)"], 1),
            ("102", room_types["غرفة فردية قياسية (Standard Single)"], 1),
            ("103", room_types["غرفة مزدوجة ديلوكس (Deluxe Double)"], 1),
            ("201", room_types["غرفة مزدوجة ديلوكس (Deluxe Double)"], 2),
            ("202", room_types["غرفة مزدوجة ديلوكس (Deluxe Double)"], 2),
            ("203", room_types["غرفة مزدوجة ديلوكس (Deluxe Double)"], 2),
            ("301", room_types["جناح عائلي فاخر (Executive Family Suite)"], 3),
            ("302", room_types["جناح عائلي فاخر (Executive Family Suite)"], 3),
        ]

        for room_num, rtype, floor in rooms_seed:
            _, created = Room.objects.get_or_create(
                room_number=room_num,
                defaults={"room_type": rtype, "floor": floor, "status": Room.Status.AVAILABLE}
            )
            action = "تمت إضافة" if created else "موجودة"
            self.stdout.write(f"  - {action} غرفة {room_num} (طابق {floor})")

        self.stdout.write(self.style.SUCCESS("✅ اكتملت تعبئة البيانات بنجاح!"))
