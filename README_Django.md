# Smart Offer - Django Version

نسخة Django من نظام إدارة المعاهد والمراكز التدريبية.

## 🚀 البدء السريع

### 1. إنشاء البيئة الافتراضية

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. تثبيت المتطلبات

```bash
pip install -r requirements.txt
```

### 3. تهيئة قاعدة البيانات

```bash
python manage.py migrate
```

### 4. إنشاء مستخدم Admin

```bash
python create_superuser.py
```

أو:

```bash
python manage.py createsuperuser
```

### 5. تشغيل السيرفر

```bash
python manage.py runserver
```

الوصول على: http://127.0.0.1:8000/

- Admin Panel: http://127.0.0.1:8000/admin/
- API Root: http://127.0.0.1:8000/api/

## 🔑 بيانات الدخول الافتراضية

- **Email:** admin@smartoffer.com
- **Password:** admin123

## 📁 هيكل المشروع

```
smartoffer_django/
├── settings.py          # الإعدادات
├── urls.py              # روابط URL
├── wsgi.py              # WSGI
└── asgi.py              # ASGI (WebSocket)

core/                    # الإعدادات الأساسية
├── models.py            # Company, Branch, Bank, MasterCategory
├── serializers.py       # Serializers
├── views.py             # ViewSets
└── admin.py             # Admin Panel

accounts/                # حسابات المستخدمين
├── models.py            # Person (Custom User), Team, BranchAccess
├── serializers.py       # Serializers + JWT
├── views.py             # ViewSets
├── admin.py             # Admin
└── managers.py          # Custom User Manager

students/                # الطلاب
├── models.py            # Contact, Student
├── serializers.py       # Serializers
└── views.py             # ViewSets

courses/                 # الدورات
├── models.py            # Master, Course
├── serializers.py       # Serializers
└── views.py             # ViewSets

registrations/           # التسجيلات
├── models.py            # Account, Attach, AccountAttach, AccountCondition, AccountNote
├── serializers.py       # Serializers
└── views.py             # ViewSets

finance/                 # الماليات
├── models.py            # Payment, PaymentOut, Deposit, Withdraw, BillBuy, Offer, Call
├── serializers.py       # Serializers
└── views.py             # ViewSets

reports/                 # التقارير (قريباً)
notifications/           # الإشعارات (قريباً)
```

## 🔌 API Endpoints

### المصادقة (Authentication)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login/` | تسجيل الدخول (JWT) |

### الكيانات الرئيسية

| Resource | Endpoint |
|----------|----------|
| Companies | `/api/companies/` |
| Branches | `/api/branches/` |
| Banks | `/api/banks/` |
| Master Categories | `/api/master-categories/` |
| Teams | `/api/teams/` |
| Persons | `/api/persons/` |
| Contacts | `/api/contacts/` |
| Students | `/api/students/` |
| Masters | `/api/masters/` |
| Courses | `/api/courses/` |
| Accounts | `/api/accounts/` |
| Payments | `/api/payments/` |
| Offers | `/api/offers/` |

### Actions مخصصة

```
GET  /api/persons/me/                    # بيانات المستخدم الحالي
GET  /api/students/by_mobile/?mobile=xxx # البحث برقم الجوال
GET  /api/accounts/by_branch/?branch_id=1 # التسجيلات حسب الفرع
GET  /api/offers/by_branch/?branch_id=1   # العروض حسب الفرع
```

## 🗄️ قاعدة البيانات

### SQLite (Development)

افتراضياً يستخدم SQLite للتطوير:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### PostgreSQL (Production)

للإنتاج، عدل `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'smartoffer',
        'USER': 'postgres',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 🔒 الصلاحيات

النظام يستخدم JWT Token للمصادقة:

1. احصل على التوكن:
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@smartoffer.com","password":"admin123"}'
```

2. استخدم التوكن في الهيدر:
```bash
curl http://localhost:8000/api/students/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 📊 المميزات الم implemented

- [x] Models كاملة لكل الكيانات
- [x] Django Admin Panel
- [x] REST API مع DRF
- [x] JWT Authentication
- [x] Filtering و Searching
- [x] Serializers مع relations
- [x] Actions مخصصة للـ APIs

## 🔧 قيد التطوير

- [ ] WebSocket Notifications
- [ ] Jasper Reports / PDF Export
- [ ] Excel Import/Export
- [ ] SMS Integration
- [ ] Email Integration
- [ ] Frontend (React/Vue)

## 📝 ملاحظات

- المشروع يدعم اللغة العربية بالكامل
- RTL جاهز للواجهة
- يمكن استيراد البيانات من قاعدة البيانات القديمة (PostgreSQL)
