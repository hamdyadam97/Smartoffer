# دليل النشر على Hostinger VPS

<div dir="rtl">

## المتطلبات

- VPS من Hostinger (Ubuntu 22.04+)
- 2GB+ RAM
- 20GB+ مساحة تخزين
- دومين متصل بالـ VPS (اختياري لكن مفضل)

---

## الخطوة 1: تجهيز الخادم

سجّل دخول على الـ VPS عبر SSH:

```bash
ssh root@your-server-ip
```

ثم نفّذ سكريبت الإعداد:

```bash
wget https://raw.githubusercontent.com/YOUR_USERNAME/smartoffer/main/setup-vps.sh
chmod +x setup-vps.sh
./setup-vps.sh
```

> **ملاحظة:** بعد تشغيل السكريبت، سجل خروج وعد دخول مرة ثانية حتى يتم تطبيق صلاحيات Docker.

---

## الخطوة 2: نسخ المشروع

```bash
cd /opt/smartoffer
git clone https://github.com/YOUR_USERNAME/smartoffer.git .
```

---

## الخطوة 3: إعداد ملف البيئة (.env)

```bash
cp .env.example .env
nano .env
```

عدّل المتغيرات التالية:

```env
# مفتاح سري قوي (يمكنك توليده من: https://djecrety.ir/)
SECRET_KEY=your-very-secure-secret-key-here

# الوضع الإنتاجي
DEBUG=False

# الدومين أو IP الخاص بالسيرفر
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,123.456.789.012
CSRF_TRUSTED_ORIGINS=https://your-domain.com

# كلمة سر قاعدة البيانات
DB_PASSWORD=your-secure-db-password

# بيانات حساب الأدمن
ADMIN_EMAIL=admin@your-domain.com
ADMIN_PASSWORD=your-secure-admin-password

# CORS (للـ Frontend)
CORS_ALLOW_ALL_ORIGINS=False
CORS_ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com

# إعدادات البريد (اختياري)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@your-domain.com
```

---

## الخطوة 4: النشر

بعد إعداد ملف `.env`، شغّل سكريبت النشر:

```bash
./deploy.sh
```

هذا السكريبت سوف:
1. يبني الـ Frontend تلقائياً باستخدام Docker (بدون تثبيت Node.js على الخادم)
2. يبني ويشغّل جميع الـ Containers
3. ينفّذ الـ Migrations
4. يجمع ملفات الـ Static
5. ينظّف الصور القديمة

---

## الخطوة 5: إعداد SSL (HTTPS) 🔒

### الطريقة الأولى: باستخدام Certbot + Docker

```bash
docker run -it --rm \
  -v /opt/smartoffer/certbot/conf:/etc/letsencrypt \
  -v /opt/smartoffer/certbot/www:/var/www/certbot \
  -p 80:80 \
  certbot/certbot certonly --standalone -d your-domain.com -d www.your-domain.com
```

بعد الحصول على الشهادة، عدّل `nginx.conf` وشغّل `./deploy.sh` مرة ثانية.

### الطريقة الثانية: باستخدام Certbot على النظام

```bash
apt install -y certbot python3-certbot-nginx
certbot --nginx -d your-domain.com -d www.your-domain.com
```

---

## إدارة المشروع

### عرض حالة الخدمات
```bash
cd /opt/smartoffer
docker-compose ps
```

### مشاهدة السجلات
```bash
# سجلات الـ Backend
docker-compose logs -f backend

# سجلات nginx
docker-compose logs -f nginx

# سجلات قاعدة البيانات
docker-compose logs -f db
```

### إعادة تشغيل الخدمات
```bash
docker-compose restart
```

### تحديث المشروع
```bash
cd /opt/smartoffer
git pull origin main
./deploy.sh
```

### الدخول إلى Django Shell
```bash
docker-compose exec backend python manage.py shell
```

### إنشاء Superuser يدوياً
```bash
docker-compose exec backend python manage.py createsuperuser
```

### نسخ احتياطي للقاعدة
```bash
./backup.sh
```

---

## استكشاف الأخطاء

### مشكلة: الصفحة البيضاء أو 404

```bash
# تأكد من بناء الـ Frontend
./deploy.sh

# تأكد من سجلات nginx
docker-compose logs nginx
```

### مشكلة: لا يمكن الاتصال بالـ API

```bash
# تأكد من حالة الـ Backend
docker-compose ps backend
docker-compose logs backend
```

### مشكلة: خطأ في Migrations

```bash
docker-compose exec backend python manage.py migrate --noinput
```

### مشكلة: الصور/الملفات لا تظهر

```bash
# تأكد من إعدادات Media
docker-compose exec backend python manage.py collectstatic --noinput
docker-compose restart nginx
```

---

## هيكل الخدمات (Docker Compose)

| الخدمة | الوصف | المنفذ |
|--------|-------|--------|
| `db` | PostgreSQL 15 | داخلي فقط |
| `redis` | Redis 7 | داخلي فقط |
| `backend` | Django + Gunicorn | داخلي: 8000 |
| `nginx` | خادم الويب + Static files | 80, 443 |
| `certbot` | تجديد شهادات SSL | - |

</div>
