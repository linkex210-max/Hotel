from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('reference_code', 'guest_name', 'room', 'check_in', 'check_out', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'check_in', 'check_out')
    search_fields = ('reference_code', 'guest_name', 'guest_phone', 'guest_email', 'room__room_number')
    readonly_fields = ('reference_code', 'created_at', 'updated_at')
