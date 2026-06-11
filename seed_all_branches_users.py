import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartoffer_django.settings')
import django
django.setup()

from core.models import Company, Branch
from accounts.models import Person, Role, EmployeeRole, Team

# ─── Config ──────────────────────────────────────────────────────
DEFAULT_PASSWORD = 'Ararhni@123'
DEFAULT_TEAM_NAME = 'موظف'

# ─── Branches to create ──────────────────────────────────────────
# (branch_name, company_name)
new_branches = [
    ('طريف', 'شركة الأهلي للتدريب'),
    ('الدوادمة', 'شركة الأهلي للتدريب'),
    ('خميس مشيط', 'شركة الفاو'),
    ('نساء حفر الباطن', 'شركة الفاو'),
    ('الفاو رياض', 'شركة الفاو'),
    ('المورد الوافي', 'شركة المورد'),
    ('روت', 'شركة الجذور الرقمية'),
]

# ─── Roles to create ─────────────────────────────────────────────
new_roles = [
    'موظف',
    'مشرف تدريب',
]

# ─── Users data ──────────────────────────────────────────────────
users_data = [
    # طريف
    {'name': 'منيفه محسن حمدان الطرفاوي', 'email': 'altrfawyamasamh@gmail.com', 'mobile': '966534000000', 'branch': 'طريف', 'role': 'موظف'},
    {'name': 'مهنا مروي قروط العنزي', 'email': 'f5rblue@gmail.com', 'mobile': '966534000000', 'branch': 'طريف', 'role': 'موظف'},
    {'name': 'نادر احمد محمد الغيطاني', 'email': 'nader101001@gmail.com', 'mobile': '966570000000', 'branch': 'طريف', 'role': 'موظف'},
    {'name': 'في بنت صالح محمد العنزي', 'email': 'fieo876@hotmail.com', 'mobile': '966570000000', 'branch': 'طريف', 'role': 'موظف'},
    {'name': 'منى تركي غريب الخالدي', 'email': 'shbybalblwy@gmail.com', 'mobile': '966548000000', 'branch': 'طريف', 'role': 'موظف'},
    {'name': 'فايزة عيد محمد االرويلي', 'email': 'Fayzhfxr100@gmail.com', 'mobile': '966552000000', 'branch': 'طريف', 'role': 'موظف'},
    {'name': 'ابرار هاشم محمد العنزي', 'email': 'Abrar12345678890@gmail.com', 'mobile': '966530000000', 'branch': 'طريف', 'role': 'موظف'},
    {'name': 'مرهج فهد هوير الحازمي', 'email': 'Hkhk507@icloud.com', 'mobile': '966504000000', 'branch': 'طريف', 'role': 'موظف'},
    {'name': 'اثير محمد علي الاشجعي', 'email': 'at4224785@gmail.com', 'mobile': '966536000000', 'branch': 'طريف', 'role': 'موظف'},

    # الدوادمة
    {'name': 'ممتازه حمد ناصر القحطاني', 'email': 'momt1418@gmail.com', 'mobile': '966552000000', 'branch': 'الدوادمة', 'role': 'موظف'},
    {'name': 'مشاري سفاح الحربي', 'email': 'meshari.alharbi@ararhni.com', 'mobile': '966563000000', 'branch': 'الدوادمة', 'role': 'مشرف تدريب'},
    {'name': 'صهيب أحمد فالح السلايطة', 'email': 'sohaib.alslaytah@ararhni.com', 'mobile': '966570000000', 'branch': 'الدوادمة', 'role': 'مدير فرع'},
    {'name': 'أ.ابتسام رشيد العتيبي', 'email': 'ebtisam.alotaibi@ararhni.com', 'mobile': '966563000000', 'branch': 'الدوادمة', 'role': 'موظف'},
    {'name': 'أ.نجود جزاء العتيبي', 'email': 'nujood.alotaibi@ararhni.com', 'mobile': '966565000000', 'branch': 'الدوادمة', 'role': 'موظف'},
    {'name': 'أ.نوره حمد عياد العتيبي', 'email': 'nourah.alotaibi@ararhni.com', 'mobile': '966561000000', 'branch': 'الدوادمة', 'role': 'موظف'},
    {'name': 'أ.وصايف مرضي فهد المطيري', 'email': 'wasaif.almutairi@ararhni.com', 'mobile': '966529000000', 'branch': 'الدوادمة', 'role': 'موظف'},
    {'name': 'أ.نوف عتيق ضفا العتيبي', 'email': 'nouf.alotaibi@ararhni.com', 'mobile': '966563000000', 'branch': 'الدوادمة', 'role': 'موظف'},
    {'name': 'أ.غزوى غزاي ناحي المقاطي', 'email': 'ghazwa.almuqati@ararhni.com', 'mobile': '966535000000', 'branch': 'الدوادمة', 'role': 'موظف'},
    {'name': 'أ.يوسف محمد يوسف أحمد', 'email': 'yousif.ahmed@ararhni.com', 'mobile': '966570000000', 'branch': 'الدوادمة', 'role': 'موظف'},
    {'name': 'أ.بدر محمد مرزوق العتيبي', 'email': 'bader.alotaibi@ararhni.com', 'mobile': '966570000000', 'branch': 'الدوادمة', 'role': 'موظف'},
    {'name': 'أ.السيد احمد محمد سالم', 'email': 'alsayed.salem@ararhni.com', 'mobile': '966570000000', 'branch': 'الدوادمة', 'role': 'موظف'},
    {'name': 'أ.محمد صلاح النور ادريس', 'email': 'mohamed.salah@ararhni.com', 'mobile': '966570000000', 'branch': 'الدوادمة', 'role': 'موظف'},
    {'name': 'أ.جمال صدقي علي العزي', 'email': 'gamal.alizzi@ararhni.com', 'mobile': '966563000000', 'branch': 'الدوادمة', 'role': 'موظف'},
    {'name': 'أ.فهد عبدالله الكرشمي', 'email': 'fahad.alkarashmi@ararhni.com', 'mobile': '966561000000', 'branch': 'الدوادمة', 'role': 'موظف'},
    {'name': 'أ.خالد حامد عبدالرحمن محمد', 'email': 'khalid.hamed@ararhni.com', 'mobile': '966570000000', 'branch': 'الدوادمة', 'role': 'موظف'},

    # خميس مشيط
    {'name': 'سارة محمد سعيد القحطاني', 'email': 'sara.qahtani@ararhni.com', 'mobile': '966557000000', 'branch': 'خميس مشيط', 'role': 'موظف'},
    {'name': 'زهرة محمد عبد الله الشايب', 'email': 'zahra.alshaib@ararhni.com', 'mobile': '966504000000', 'branch': 'خميس مشيط', 'role': 'موظف'},
    {'name': 'سامية سعد زايد الشهري', 'email': 'samia.shahri@ararhni.com', 'mobile': '966557000000', 'branch': 'خميس مشيط', 'role': 'موظف'},
    {'name': 'نهال جار الله محمد الصعيب', 'email': 'nihal.alsuaib@ararhni.com', 'mobile': '966579000000', 'branch': 'خميس مشيط', 'role': 'موظف'},
    {'name': 'شذي علي صالح ال مداوي', 'email': 'shatha.almadawi@ararhni.com', 'mobile': '966557000000', 'branch': 'خميس مشيط', 'role': 'موظف'},
    {'name': 'نايف جار الله محمد الصعيب', 'email': 'naif.alsuaib@ararhni.com', 'mobile': '966539000000', 'branch': 'خميس مشيط', 'role': 'موظف'},
    {'name': 'تركي القحطاني', 'email': 'Turki_Al_Qahtani@ararhni.com', 'mobile': '966553000000', 'branch': 'خميس مشيط', 'role': 'مشرف تدريب'},
    {'name': 'خالد محمد سعيد القحطاني', 'email': 'khaled.qahtani@ararhni.com', 'mobile': '966559000000', 'branch': 'خميس مشيط', 'role': 'موظف'},
    {'name': 'عبدالله حسن الاسمري', 'email': 'abdullah_asmary@ararhni.com', 'mobile': '966553000000', 'branch': 'خميس مشيط', 'role': 'موظف'},

    # نساء حفر الباطن
    {'name': 'فتون العنزي', 'email': 'fatoon.alanzi@ararhni.com', 'mobile': '966557000000', 'branch': 'نساء حفر الباطن', 'role': 'موظف'},
    {'name': 'ريوف الشمري', 'email': 'riyof.alshammari@ararhni.com', 'mobile': '966506000000', 'branch': 'نساء حفر الباطن', 'role': 'موظف'},
    {'name': 'امجاد الحربي', 'email': 'amjad.alharbi@ararhni.com', 'mobile': '966538000000', 'branch': 'نساء حفر الباطن', 'role': 'موظف'},
    {'name': 'شاديه العنزي', 'email': 'shadia.alanzi@ararhni.com', 'mobile': '966550000000', 'branch': 'نساء حفر الباطن', 'role': 'موظف'},
    {'name': 'نوره العنزي', 'email': 'noura.alanzi@ararhni.com', 'mobile': '966550000000', 'branch': 'نساء حفر الباطن', 'role': 'موظف'},

    # روت
    {'name': 'سارة علي خلوفة الشهري', 'email': 'sara.shahri@ararhni.com', 'mobile': '966533000000', 'branch': 'روت', 'role': 'موظف'},
    {'name': 'بسام ابو نصر', 'email': 'b.abualnasser@root-jo.com', 'mobile': '962790000000', 'branch': 'روت', 'role': 'موظف'},
    {'name': 'علاء حسان', 'email': 'alaa@root-jo.com', 'mobile': '962789000000', 'branch': 'روت', 'role': 'موظف'},
    {'name': 'شام العزام', 'email': 'shamazzam961@gmail.com', 'mobile': '962791000000', 'branch': 'روت', 'role': 'موظف'},
    {'name': 'نضال العبيدات', 'email': 'nidalobeidat@root-jo.com', 'mobile': '962789000000', 'branch': 'روت', 'role': 'موظف'},
    {'name': 'لانا طوالبة', 'email': 'lana_alqadery@root-jo.com', 'mobile': '962789000000', 'branch': 'روت', 'role': 'موظف'},

    # المورد الوافي
    {'name': 'فاطمة عيد الرويلي', 'email': 'f.alruwaili@ararhni.com', 'mobile': '966570000000', 'branch': 'المورد الوافي', 'role': 'موظف'},
    {'name': 'طيف مفلح', 'email': 'teif_mofleh@ararhni.com', 'mobile': '966568000000', 'branch': 'المورد الوافي', 'role': 'موظف'},

    # الفاو رياض
    {'name': 'احمد السبع', 'email': 'ahmed_sabea@ararhni.com', 'mobile': '966561000000', 'branch': 'الفاو رياض', 'role': 'موظف'},
    {'name': 'اثير العنزى', 'email': 'atheer_mohammad@ararhni.com', 'mobile': '966561000000', 'branch': 'الفاو رياض', 'role': 'موظف'},
    {'name': 'مؤمن نافذ القطب', 'email': 'moamen.qotb@ararhni.com', 'mobile': '966561000000', 'branch': 'الفاو رياض', 'role': 'موظف'},
]


def split_name(full_name):
    parts = full_name.strip().split()
    if len(parts) == 1:
        return parts[0], '', '', ''
    elif len(parts) == 2:
        return parts[0], '', '', parts[1]
    elif len(parts) == 3:
        return parts[0], parts[1], '', parts[2]
    elif len(parts) == 4:
        return parts[0], parts[1], parts[2], parts[3]
    else:
        return parts[0], parts[1], ' '.join(parts[2:-1]), parts[-1]


def main():
    # ─── 1. Create missing roles ─────────────────────────────────
    print('=== Creating Roles ===')
    roles_map = {}
    for role_name in new_roles:
        role, created = Role.objects.get_or_create(name=role_name)
        roles_map[role_name] = role
        print(f'{"CREATED" if created else "EXISTS"}: {role_name}')

    # Also fetch existing roles
    for role in Role.objects.all():
        roles_map[role.name] = role
    print()

    # ─── 2. Create branches ──────────────────────────────────────
    print('=== Creating Branches ===')
    branches_map = {}
    current_max = 0
    if Branch.objects.exists():
        current_max = Branch.objects.order_by('-code').first().code
    counter = current_max + 1

    for branch_name, company_name in new_branches:
        try:
            company = Company.objects.get(name=company_name)
        except Company.DoesNotExist:
            print(f'ERROR: Company "{company_name}" not found!')
            continue

        branch, created = Branch.objects.get_or_create(
            name=branch_name,
            defaults={
                'company': company,
                'code': counter,
                'sub_name': '',
            }
        )
        if created:
            counter += 1
            print(f'CREATED: {branch_name} (code={branch.code}) under {company_name}')
        else:
            print(f'EXISTS: {branch_name} (code={branch.code})')
        branches_map[branch_name] = branch

    # Fetch all branches for lookup
    for branch in Branch.objects.all():
        branches_map[branch.name] = branch
    print()

    # ─── 3. Get default team ─────────────────────────────────────
    team = None
    try:
        team = Team.objects.get(name=DEFAULT_TEAM_NAME)
        print(f'Using team: {team.name}')
    except Team.DoesNotExist:
        print(f'WARNING: Team "{DEFAULT_TEAM_NAME}" not found.')
    print()

    # ─── 4. Create users ─────────────────────────────────────────
    print('=== Creating Users ===')
    created_users = 0
    updated_users = 0
    created_roles = 0
    skipped = 0

    for idx, u in enumerate(users_data, 1):
        full_name = u['name']
        email = u['email'].strip().lower()
        mobile = u['mobile']
        branch_name = u['branch']
        role_name = u['role']

        first_name, second_name, third_name, forth_name = split_name(full_name)
        branch = branches_map.get(branch_name)
        role = roles_map.get(role_name)

        if not branch:
            print(f'[{idx}] SKIP: Branch "{branch_name}" not found for {full_name}')
            skipped += 1
            continue

        if not role:
            print(f'[{idx}] SKIP: Role "{role_name}" not found for {full_name}')
            skipped += 1
            continue

        # Create or update user
        user, created = Person.objects.get_or_create(
            email__iexact=email,
            defaults={
                'email': email,
                'first_name': first_name,
                'second_name': second_name,
                'third_name': third_name,
                'forth_name': forth_name,
                'mobile': mobile,
                'is_staff': True,
                'is_active': True,
                'is_superuser': False,
                'branch': branch,
                'team': team,
            }
        )

        if created:
            user.set_password(DEFAULT_PASSWORD)
            user.save(update_fields=['password'])
            created_users += 1
            status = 'CREATED'
        else:
            # Update fields
            user.first_name = first_name
            user.second_name = second_name
            user.third_name = third_name
            user.forth_name = forth_name
            user.mobile = mobile
            user.is_staff = True
            user.is_active = True
            user.branch = branch
            if team:
                user.team = team
            user.save()
            updated_users += 1
            status = 'UPDATED'

        # Create EmployeeRole
        er, er_created = EmployeeRole.objects.get_or_create(
            person=user,
            role=role,
            branch=branch
        )
        if er_created:
            created_roles += 1

        print(f'[{idx}] {status}: {full_name} | {email} | {branch_name} | {role_name}')

    print()
    print('=' * 60)
    print(f'Users Created: {created_users}')
    print(f'Users Updated: {updated_users}')
    print(f'EmployeeRoles Created: {created_roles}')
    print(f'Skipped: {skipped}')
    print(f'Default Password: {DEFAULT_PASSWORD}')
    print('=' * 60)


if __name__ == '__main__':
    main()
