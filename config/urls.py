from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI
from apps.rooms.api import router as rooms_router
from apps.bookings.api import router as bookings_router

api = NinjaAPI(
    title="Linkex SmartHotel API",
    version="1.0.0",
    description="نظام إدارة الفندق الذكي - الغرف، محرك التوفر، والحجوزات",
    docs_url="/docs"
)

api.add_router("/rooms", rooms_router)
api.add_router("/bookings", bookings_router)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),
]
