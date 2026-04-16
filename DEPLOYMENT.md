# دليل النشر خطوة بخطوة 🚀

## الموقف عام

- عندك **VPS** على Hostinger (الـ IP: `89.116.228.76`)
- عندك **دومين**: `smartoffer.m3had-system.cloud`
- عندك **مشروع Python تاني** شغال على port `8000` على نفس السيرفر
- المشروع الجديد (Smart Offer) هيشتغل على **Docker** و هيتعرض من خلال الدومين الجديد

---

## الخطة بالعربي

1. **المشروع الجديد** هيشتغل جوه Docker containers (Django + PostgreSQL + Redis + nginx)
2. **nginx بتاع Docker** هيستمع على port `8080` داخل السيرفر
3. **nginx الأصلي** المثبت على Ubuntu (بتاع Hostinger) هيستقبل الدومين `smartoffer.m3had-system.cloud` على port `80` ويوجّهه لـ `localhost:8080`
4. **مشروع Python التاني** على port `8000` هيفضل شغال زي ما هو بدون أي تأثير

---

## المتطلبات اللي لازم تكون جهزتها قبل ما تبدأ

| المتطلب | الحالة |
|---------|--------|
| VPS شغال على Ubuntu | ✅ عندك |
| دومين موجه للـ VPS | ✅ `smartoffer.m3had-system.cloud` |
| GitHub repo للمشروع | ✅ `hamdyadam97/Smartoffer` |
| Secrets على GitHub | لازم تتأكد منها |

### تأكد من Secrets على GitHub

ادخل على الرابط ده:
```
https://github.com/hamdyadam97/Smartoffer/settings/secrets/actions
```

لازم تكون موجودة:
- `VPS_HOST` = `89.116.228.76`
- `VPS_USERNAME` = `root`
- `VPS_SSH_KEY` = المفتاح الخاص للـ SSH

لو مش موجودة، الـ Auto Deploy مش ه يشتغل.

---

## الخطوة 1: أول مرة تشغّل المشروع على السيرفر

### 1.1 ادخل على السيرفر بالـ SSH

افتح **Terminal** (أو PowerShell) على جهازك واكتب:

```bash
ssh root@89.116.228.76
```

### 1.2 تأكد إن المشروع نزل على السيرفر

```bash
cd /docker/smartoffer
```

لو لقيت نفسك جوه المجلد، يبقى كويس.

**لو مش موجود** (أول مرة)، نزله بالأمر ده:

```bash
mkdir -p /docker/smartoffer
cd /docker/smartoffer
git clone https://github.com/hamdyadam97/Smartoffer.git .
```

### 1.3 جهّز ملف البيئة `.env`

```bash
cd /docker/smartoffer
cp .env.example .env
nano .env
```

هيفتحلك محرر النصوص. **غيّر** القيم دي:

```env
# ==== لازم تغيرهم ====
SECRET_KEY=اكتب-هنا-مفتاح-قوي-طويل-جدا
DB_PASSWORD=اكتب-هنا-باسورد-قوي
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=اكتب-هنا-باسورد-ادمن

# ==== دول جاهزين ====
DEBUG=False
ALLOWED_HOSTS=smartoffer.m3had-system.cloud,89.116.228.76
CSRF_TRUSTED_ORIGINS=https://smartoffer.m3had-system.cloud
CORS_ALLOW_ALL_ORIGINS=False
CORS_ALLOWED_ORIGINS=https://smartoffer.m3had-system.cloud
```

**عشان تحفظ وتقفل:**
- اضغط `Ctrl + O` (حفظ)
- اضغط `Enter`
- اضغط `Ctrl + X` (خروج)

### 1.4 عدّل nginx الأصلي (اللي على Ubuntu)

ده **أهم خطوة**. عشان الدومين يوصل للمشروع الجديد:

```bash
nano /etc/nginx/sites-available/default
```

**أضف** في **أول الملف** (قبل أي `server` block تاني) الكود ده:

```nginx
server {
    listen 80;
    server_name smartoffer.m3had-system.cloud;

    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**تحذير:** سيب `server` block بتاع مشروع Python التاني زي ما هو. ما تمسحش حاجة.

بعدين شغّل الأوامر دي للتأكد:

```bash
nginx -t
systemctl reload nginx
```

لو ظهر `syntax is ok` يبقى تمام.

### 1.5 شغّل المشروع

```bash
cd /docker/smartoffer
docker compose down
docker compose up -d --build
```

استنى شوية لحد ما يخلص البناء.

### 1.6 شغّل الميجراشنز والستاتيك

```bash
docker compose exec backend python manage.py migrate --noinput
docker compose exec backend python manage.py collectstatic --noinput
```

### 1.7 تأكد إن كل containers شغالة

```bash
docker compose ps
```

لازم تلاقي حاجة زي كده (كلهم `Up`):

```
NAME                 STATUS
smartoffer-backend   Up
smartoffer-nginx     Up
smartoffer-db        Up
smartoffer-redis     Up
smartoffer-certbot   Up
```

### 1.8 اختبر الموقع

افتح في المتصفح:
```
http://smartoffer.m3had-system.cloud
```

**مفروض يشتغل** 🎉

---

## الخطوة 2: التحديث التلقائي (Auto Deploy)

من دلوقتي، أي تعديل على جهازك:

### على Windows (جهازك):

```bash
cd G:\smartoffer
git add .
git commit -m "اي وصف للتعديل"
git push origin main
```

### هيحصل إيه تلقائيًا؟

1. **GitHub Actions** هيبني الـ Frontend React
2. هيرفع `frontend/dist` على الريبو
3. هيدخل على الـ VPS بالـ SSH
4. هيسحب آخر كود
5. هيشغّل `./deploy.sh` اللي بيعمل كل حاجة (build + migrations + static)

### تقدر تتابع التقدم من هنا:

```
https://github.com/hamdyadam97/Smartoffer/actions
```

---

## الخطوة 3: لو حابب تعمل تحديث يدوي من السيرفر

لو Auto Deploy واقف لأي سبب، افتح SSH واكتب:

```bash
cd /docker/smartoffer
git pull origin main
./deploy.sh
```

ده هيعمل نفس الخطوات بالظبط.

---

## الخطوة 4: SSL / HTTPS (اختياري لكن مهم) 🔒

بعد ما يشتغل على HTTP، عايز تجيب شهادة SSL.

### 4.1 وقف nginx Docker مؤقتًا

```bash
cd /docker/smartoffer
docker compose stop nginx
```

### 4.2 اجلب الشهادة

```bash
docker run -it --rm \
  -v /docker/smartoffer/certbot/conf:/etc/letsencrypt \
  -v /docker/smartoffer/certbot/www:/var/www/certbot \
  -p 80:80 \
  certbot/certbot certonly --standalone \
  -d smartoffer.m3had-system.cloud \
  --agree-tos \
  -m admin@example.com
```

هيسألك سؤال، اكتب `Y` وادوس Enter.

### 4.3 ارجع شغّل nginx Docker

```bash
docker compose start nginx
```

### 4.4 بعدها قولي

هعدّل `nginx.conf` عشان يشتغل على HTTPS.

---

## استكشاف الأخطاء

### لو `http://smartoffer.m3had-system.cloud` مش بيفتح

1. **تأكد إن nginx الأصلي شغال:**
   ```bash
   systemctl status nginx
   ```

2. **تأكد إن Docker nginx شغال على 8080:**
   ```bash
   docker compose ps
   ss -tlnp | grep 8080
   ```

3. **شوف سجلات الأخطاء:**
   ```bash
   docker compose logs nginx
   docker compose logs backend
   ```

### لو الـ API مش بيرد

```bash
docker compose logs backend
```

### لو static files (CSS/JS) مش بتظهر

```bash
docker compose exec backend python manage.py collectstatic --noinput
docker compose restart nginx
```

---

## ملخص سريع للأوامر

| الهدف | الأمر |
|-------|-------|
| دخول السيرفر | `ssh root@89.116.228.76` |
| تشغيل المشروع | `cd /docker/smartoffer && docker compose up -d` |
| تحديث يدوي | `cd /docker/smartoffer && git pull && ./deploy.sh` |
| سجلات nginx | `docker compose logs -f nginx` |
| سجلات backend | `docker compose logs -f backend` |
| إعادة تشغيل backend | `docker compose restart backend` |
| Django shell | `docker compose exec backend python manage.py shell` |
| إنشاء superuser | `docker compose exec backend python manage.py createsuperuser` |

---

**لو واجهت أي مشكلة، ابعت رسالة بالخطأ وهساعدك.**
