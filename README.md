# 🏨 Linkex SmartHotel - Backend API

المستودع الخلفي (Backend) لنظام **Linkex SmartHotel** لإدارة الفنادق والحجوزات الذكية.
مبني بلغة **Python** وإطار عمل **Django** مع **Django Ninja** لتقديم واجهات REST API سريعة وتوليد مستندات Swagger تفاعلية تلقائياً وفق معيار OpenAPI 3.1.

---

## 🚀 التشغيل السريع (للمطورين والفرونت إند)

### 1. إعداد البيئة الافتراضية وتثبيت الحزم
```bash
# إنشاء البيئة الافتراضية
python -m venv .venv

# تفعيل البيئة:
# على Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# أو على Linux/macOS:
source .venv/bin/activate

# تثبيت الحزم المطلوبة
pip install -r requirements.txt
```

### 2. تجهيز قاعدة البيانات وتعبئة البيانات التجريبية
```bash
# إنشاء وتطبيق الجداول
python manage.py migrate

# تعبئة الغرف والتصنيفات التجريبية بضغطة زر
python manage.py seed_data
```

### 3. تشغيل خادم التطوير
```bash
python manage.py runserver
```

---

## 📖 روابط التوثيق ولوحة التحكم

* **توثيق الـ API التفاعلي (Swagger UI):**
  👉 [http://localhost:8000/api/docs](http://localhost:8000/api/docs)
* **ملف المواصفات المعياري (OpenAPI Schema):**
  👉 `http://localhost:8000/api/openapi.json`
* **لوحة تحكم الإدارة (Django Admin):**
  👉 [http://localhost:8000/admin/](http://localhost:8000/admin/)
  * **اسم المستخدم:** `admin`
  * **كلمة المرور:** `admin123`

---

## 🔌 دليل الـ Endpoints للفرونت إند (Frontend Integration)

### 1️⃣ شاشة النزيل (اختيار التواريخ وحجز الغرفة):
* **فحص توفر الغرف وحساب الأسعار:**
  * `POST /api/bookings/availability`
  * **المدخلات (JSON):**
    ```json
    {
      "check_in": "2026-11-20",
      "check_out": "2026-11-23",
      "guests_count": 2
    }
    ```
  * **المخرجات:** قائمة بالغرف الشاغرة مع `total_nights` و `total_price` محسوبة آلياً.
* **تأكيد وإنشاء الحجز:**
  * `POST /api/bookings/`
  * **المدخلات (JSON):**
    ```json
    {
      "room_id": 1,
      "guest_name": "أحمد عبدالله",
      "guest_email": "ahmed@example.com",
      "guest_phone": "+966501234567",
      "check_in": "2026-11-20",
      "check_out": "2026-11-23",
      "notes": "غرفة هادئة في طابق علوي"
    }
    ```
  * **المخرجات:** تفاصيل الحجز كاملة مع `reference_code` (مثل `LX-3B9A1F`).

### 2️⃣ شاشة الاستقبال (Reception Dashboard):
* **مصفوفة الغرف الملونة وحالاتها:**
  * `GET /api/rooms/` (يمكن الفلترة عبر `?status=available` أو `?floor=1`).
* **استعلام سريع عن الحجز برمز الحجز أو QR:**
  * `GET /api/bookings/ref/{reference_code}`
* **تسجيل وصول النزيل (Check-in):**
  * `POST /api/bookings/{booking_id}/check-in` (يحول الحجز إلى `checked_in` والغرفة إلى `occupied`).
* **تسجيل مغادرة النزيل (Check-out):**
  * `POST /api/bookings/{booking_id}/check-out` (يحول الحجز إلى `checked_out` والغرفة إلى `cleaning`).

---

## 🧪 تشغيل اختبارات الوحدة الآلية (Unit Tests)
```bash
python manage.py test apps.bookings
```

---

## 🐳 التشغيل عبر Docker (اختياري)
```bash
docker compose up --build
```
