from datetime import date, timedelta
from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from apps.rooms.models import RoomType, Room
from apps.bookings.models import Booking
from apps.bookings.services import (
    get_available_rooms,
    create_booking,
    is_room_available,
    process_check_in,
    process_check_out
)

class SmartHotelBookingEngineTest(TestCase):
    def setUp(self):
        self.deluxe_type = RoomType.objects.create(
            name="Deluxe Suite",
            price_per_night=Decimal("250.00"),
            capacity=2,
            amenities=["WiFi", "King Bed", "Smart TV"]
        )
        self.room_101 = Room.objects.create(
            room_number="101",
            room_type=self.deluxe_type,
            floor=1
        )

    def test_availability_and_price_calculation(self):
        today = date.today()
        check_in = today + timedelta(days=2)
        check_out = today + timedelta(days=5)  # 3 nights

        available = get_available_rooms(check_in, check_out)
        self.assertEqual(len(available), 1)
        self.assertEqual(available[0]["total_nights"], 3)
        self.assertEqual(available[0]["total_price"], Decimal("750.00"))

    def test_booking_creation_and_double_booking_prevention(self):
        today = date.today()
        check_in = today + timedelta(days=2)
        check_out = today + timedelta(days=5)

        # 1. إنشاء الحجز الأول بنجاح
        booking1 = create_booking(
            room_id=self.room_101.id,
            guest_name="أسامة محمد",
            guest_email="osama@example.com",
            guest_phone="+966500000000",
            check_in=check_in,
            check_out=check_out,
        )
        self.assertEqual(booking1.total_price, Decimal("750.00"))
        self.assertTrue(booking1.reference_code.startswith("LX-"))

        # 2. التأكد من أن الغرفة لم تعد متاحة في نفس الفترة
        self.assertFalse(is_room_available(self.room_101.id, check_in, check_out))

        # 3. التأكد من منع التعارض المتقاطع (مثلاً حجز من يوم 3 إلى 6)
        overlap_check_in = today + timedelta(days=3)
        overlap_check_out = today + timedelta(days=6)
        with self.assertRaises(ValidationError):
            create_booking(
                room_id=self.room_101.id,
                guest_name="عميل آخر",
                guest_email="other@example.com",
                guest_phone="+966511111111",
                check_in=overlap_check_in,
                check_out=overlap_check_out,
            )

    def test_check_in_and_check_out_flow(self):
        today = date.today()
        booking = create_booking(
            room_id=self.room_101.id,
            guest_name="نزيل تجريبي",
            guest_email="test@example.com",
            guest_phone="+966522222222",
            check_in=today,
            check_out=today + timedelta(days=1),
        )

        # تسجيل الوصول
        process_check_in(booking)
        self.room_101.refresh_from_db()
        self.assertEqual(booking.status, Booking.Status.CHECKED_IN)
        self.assertEqual(self.room_101.status, Room.Status.OCCUPIED)

        # تسجيل المغادرة
        process_check_out(booking)
        self.room_101.refresh_from_db()
        self.assertEqual(booking.status, Booking.Status.CHECKED_OUT)
        self.assertEqual(self.room_101.status, Room.Status.CLEANING)
