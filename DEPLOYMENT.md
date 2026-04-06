# دليل النشر - Deployment Guide

<div dir="rtl">

## الطريقة الأولى: النشر باستخدام Docker (موصى بها)

### المتطلبات
- VPS مع Ubuntu 20.04+ أو Debian 11+
- Docker و Docker Compose مثبتين
- 2GB+ RAM
- 20GB+ مساحة تخزين

### خطوات النشر

#### 1. تجهيز الخادم (VPS)

```bash
# تسجيل الدخول للخادم
ssh root@your-server-ip

# تشغيل سكريبت الإعداد
wget https://raw.githubusercontent.com/yourusername/smartoffer/main/setup-vps.sh
chmod +x setup-vps.sh
./setup-vps.sh
```

أو يدوياً:

```bash
# تحديث النظام
apt update && apt upgrade -y

# تثبيت Docker
curl -fsSL https://get.docker.com | sh
usermod -aG docker $USER

# تثبيت Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

#### 2. نسخ المشروع

```bash
mkdir -p /opt/smartoffer
cd /opt/smartoffer
git clone https://github.com/yourusername/smartoffer.git .
```

#### 3. إعداد ملف البيئة

```bash
cp .env.example .env
nano .env
```

عدل المتغيرات التالية:
```env
SECRET_KEY=your-secure-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
CSRF_TRUSTED_ORIGINS=https://your-domain.com

# Database
DB_PASSWORD=your-secure-db-password

# Admin User
ADMIN_EMAIL=admin@your-domain.com
ADMIN_PASSWORD=your-secure-admin-password

# Email (اختياري)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

#### 4. تشغيل المشروع

```bash
docker-compose up -d
```

#### 5. إنشاء مستخدم Admin

```bash
docker-compose exec backend python manage.py createsuperuser
```

#### 6. إعداد SSL (HTTPS) باستخدام Let's Encrypt

```bash
# تثبيت Certbot
docker run -it --rm \
  -v /opt/smartoffer/certbot/conf:/etc/letsencrypt \
  -v /opt/smartoffer/certbot/www:/var/www/certbot \
  -p 80:80 \
  certbot/certbot certonly --standalone -d your-domain.com -d www.your-domain.com

# تحديث nginx.conf لاستخدام SSL
```

### إدارة المشروع

```bash
# عرض حالة الخدمات
docker-compose ps

# مشاهدة السجلات
docker-compose logs -f backend
docker-compose logs -f nginx

# إعادة تشغيل الخدمات
docker-compose restart

# تحديث المشروع
docker-compose pull
docker-compose up -d

# نسخ احتياطي للقاعدة
./backup.sh
```

---

## الطريقة الثانية: النشر التلقائي عبر GitHub Actions

### 1. إعداد Secrets في GitHub

اذهب إلى Settings → Secrets and variables → Actions

أضف الـ Secrets التالية:

| Secret | الوصف |
|--------|-------|
| `DOCKER_USERNAME` | اسم المستخدم في Docker Hub |
| `DOCKER_PASSWORD` | كلمة مرور Docker Hub |
| `VPS_HOST` | عنوان IP الخاص بالخادم |
| `VPS_USERNAME` | اسم المستخدم للـ SSH |
| `VPS_SSH_KEY` | مفتاح SSH الخاص (كامل مع BEGIN/END) |

### 2. إعداد مفتاح SSH على الخادم

```bash
# على الخادم VPS
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# إنشاء مفتاح (اختياري)
ssh-keygen -t ed25519 -C "github-actions"

# عرض المفتاح العام
 cat ~/.ssh/id_ed25519.pub >> ~/.ssh/authorized_keys

# عرض المفتاح الخاص (انسخه كاملاً)
cat ~/.ssh/id_ed25519
```

انسخ المفتاح الخاص كاملاً والصقه في GitHub Secret `VPS_SSH_KEY`

### 3. إعداد Docker Hub

- أنشئ حساب على [hub.docker.com](https://hub.docker.com)
- أنشئ repository باسم `smartoffer`
- احصل على Access Token من Account Settings → Security

### 4. النشر التلقائي

الآن كل push على branch `main` سيقوم تلقائياً بـ:
1. بناء Docker image
2. رفعه على Docker Hub
3. نشره على VPS

---

## الطريقة الثالثة: النشر اليدوي

```bash
# على VPS
cd /opt/smartoffer

# سحب آخر تحديث
git pull origin main

# بناء Docker image محلياً
docker build -t smartoffer:latest .

# تشغيل
docker-compose down
docker-compose up -d
```

---

## استكشاف الأخطاء

### مشكلة: لا يمكن الاتصال بالقاعدة

```bash
# التحقق من حالة قاعدة البيانات
docker-compose ps db
docker-compose logs db

# إعادة تشغيل القاعدة
docker-compose restart db
```

### مشكلة: الصفحات لا تعمل (404)

```bash
# التحقق من nginx
docker-compose logs nginx

# إعادة بناء static files
docker-compose exec backend python manage.py collectstatic --noinput
```

### مشكلة: خطأ في migrations

```bash
# حذف Migration غير ناجح
docker-compose exec backend python manage.py migrate --fake-zero
docker-compose exec backend python manage.py migrate
```

---

## نصائح الأمان

1. **لا ترفع ملف `.env` على GitHub**
2. **استخدم كلمة سر قوية لقاعدة البيانات**
3. **حدث `SECRET_KEY` في الإنتاج**
4. **استخدم جدار نار (Firewall)**:
   ```bash
   ufw allow 80/tcp
   ufw allow 443/tcp
   ufw allow 22/tcp
   ufw enable
   ```
5. **فعّل HTTPS** باستخدام Let's Encrypt

---

## تحديث المشروع

### تحديث يدوي:
```bash
cd /opt/smartoffer
git pull
docker-compose down
docker-compose up -d --build
```

### تحديث تلقائي:
التحديثات على branch `main` سيتم نشرها تلقائياً.

</div>
