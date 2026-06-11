import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartoffer_django.settings')
import django
django.setup()

from accounts.models import Person, Team
from core.models import Branch

# ─── Configuration ───────────────────────────────────────────────
DEFAULT_PASSWORD = 'Ararhni@123'
DEFAULT_BRANCH_NAME = 'الأهلي عرعر (رجال)'
DEFAULT_TEAM_NAME = 'موظف'  # Code: EMP

# ─── Users data ──────────────────────────────────────────────────
# Format: (full_name, email)
# Email fixes applied:
#   1. faisalalrwele512@ararhni -> faisalalrwele512@ararhni.com
#   8. fawaz.ahedhal@araghni.com -> fawaz.ahedhal@ararhni.com
#   11 & 13 have no email -> auto-generated

users_data = [
    ('فيصل مفضي الرويلي', 'faisalalrwele512@ararhni.com'),
    ('رايد مشرف العنزي', 'raed@ararhni.com'),
    ('تركي سفاح المجلاد', 'turki.almajlad@ararhni.com'),
    ('عبدالاله علي حوران العنزي', 'abdelelahali@ararhni.com'),
    ('عمر رمضان ابوبكر جلال', 'omarramadan42036@ararhni.com'),
    ('عبدالعزيز فهد رويحل العنزي', 'abdulaziz.fahad.alenezi@ararhni.com'),
    ('ياسمين نفاج نايل الضلعان', 'yasmeen@ararhni.com'),
    ('فواز عبيد عبدالعزيز الهذال', 'fawaz.ahedhal@ararhni.com'),
    ('ماهر عامر سعود العنزي', 'maher@ararhni.com'),
    ('مراد محمد تاج عبدالرحمن جرادات', 'murad.jaradat@ararhni.com'),
    ('علي حسين خلف الاشجعي', 'ali.ashjaee@ararhni.com'),
    ('طاهر محمد عبدالحميد', 'tahir.abdelhamid@ararhni.com'),
    ('عصام عبدالعظيم يوسف يوسف', 'esam_yousef@ararhni.com'),
    ('مصطفي عمر كامل شعيرة', 'muostafa@ararhni.com'),
    ('مشعل فارس مشعل العنزي', 'm.f.alanzi@ararhni.com'),
    ('احمد عيسى', 'ahmedessa2025@ararhni.com'),
    ('خالد عبدالحكيم السيد مفتاح', 'khalid.alsyed@ararhni.com'),
    ('أشرف عبد الفتاح مصلح أبو فارس', 'ashraf.abufaris@ararhni.com'),
    ('احمد صلاح عبدالهادي خليل', 'a_salah@ararhni.com'),
    ('علاء الدين عمر جمعة ابوجياب', 'abujayyab10@ararhni.com'),
    ('أسامة حمزة', 'o.h.alhussien@ararhni.com'),
    ('مصطفى شعيرة', 'mustafaa.eabdalhakim@ararhni.com'),
    ('طارق نبيل', 'tareknabil98@ararhni.com'),
    ('عمر ابولاوي', 'omar-desginer@ararhni.com'),
    ('هيثم هدية', 'haitham.salah@ararhni.com'),
    ('HR', 'hr@ararhni.com'),
    ('إدارة المعهد الأهلي عرعر', 'manage.ahli@ararhni.com'),
]


def split_name(full_name):
    """
    Split Arabic full name into first, second, third, forth.
    Simple 4-part splitting logic.
    """
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
        # More than 4 parts: merge middle parts into third_name
        return parts[0], parts[1], ' '.join(parts[2:-1]), parts[-1]


def main():
    # Get default branch
    try:
        branch = Branch.objects.get(name=DEFAULT_BRANCH_NAME)
        print(f'Using branch: {branch.name} (code={branch.code})')
    except Branch.DoesNotExist:
        print(f'ERROR: Branch "{DEFAULT_BRANCH_NAME}" not found!')
        print('Available branches:')
        for b in Branch.objects.all():
            print(f'  - {b.name}')
        sys.exit(1)

    # Get default team
    team = None
    try:
        team = Team.objects.get(name=DEFAULT_TEAM_NAME)
        print(f'Using team: {team.name} (code={team.code})')
    except Team.DoesNotExist:
        print(f'WARNING: Team "{DEFAULT_TEAM_NAME}" not found. Users will have no team.')

    created_count = 0
    updated_count = 0
    skipped_count = 0

    for full_name, email in users_data:
        first_name, second_name, third_name, forth_name = split_name(full_name)

        user, created = Person.objects.get_or_create(
            email__iexact=email,
            defaults={
                'email': email,
                'first_name': first_name,
                'second_name': second_name,
                'third_name': third_name,
                'forth_name': forth_name,
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
            created_count += 1
            print(f'[CREATED] {full_name} -> {email}')
        else:
            # Update existing user info (optional)
            user.first_name = first_name
            user.second_name = second_name
            user.third_name = third_name
            user.forth_name = forth_name
            user.is_staff = True
            user.is_active = True
            user.branch = branch
            if team:
                user.team = team
            user.save()
            updated_count += 1
            print(f'[UPDATED] {full_name} -> {email}')

    print('\n' + '=' * 50)
    print(f'Done!  Created: {created_count}  |  Updated: {updated_count}')
    print(f'Default password for all new users: {DEFAULT_PASSWORD}')
    print('=' * 50)


if __name__ == '__main__':
    main()
