import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartoffer_django.settings')
import django
django.setup()

from accounts.models import Person, Role, EmployeeRole, Team
from core.models import Branch, Company

# ─── Config ──────────────────────────────────────────────────────
DEFAULT_PASSWORD = 'Ararhni@123'
DEFAULT_TEAM_NAME = 'موظف'

# ─── Branch name mapping (source -> DB branch name) ──────────────
BRANCH_NAME_MAP = {
    'روت': 'روت',
    'القريات': 'الأهلي القريات (رجال)',
    'عرعر': 'الأهلي عرعر (رجال)',
    'المورد الوافي': 'المورد الوافي',
    'الفاو رياض': 'الفاو رياض',
    'معهد الثقة الدائمة': 'الثقة الدائمة',
    'حفر الباطن': 'الفاو حفر الباطن (رجال)',
    'مؤسسة صرخة': 'مؤسسة صرخة',
    'آفاق التطوير - الدمام': 'آفاق التطور',
    'سكاكا': 'الأهلي سكاكا (رجال)',
    'القصيم': 'الفاو القصيم (رجال)',
    'المعهد الاهلي المنصورية': 'الأهلي المنصورية (رجال)',
}

# ─── Role name mapping (source -> DB role name) ──────────────────
ROLE_NAME_MAP = {
    'Branch Managereee': 'مدير فرع',
    'Branch Manager': 'مدير فرع',
    'المكتب الرئيسى HR & Accounting & مدير الأفرع': 'مدير فرع',
    'CEO': 'مدير تنفيذى',
    '': 'موظف',
    'موظف': 'موظف',
    'مشرف تدريب': 'مشرف تدريب',
}

# ─── Roles to ensure exist ───────────────────────────────────────
ROLES_TO_ENSURE = ['موظف', 'مشرف تدريب', 'مدير فرع', 'مدير تنفيذى']

# ─── Users data ──────────────────────────────────────────────────
users_data = [
    {'name': 'انس ابوعنزة', 'email': 'anas.abuanzeh@root-jo.com', 'mobile': '962791000000', 'branch': 'روت', 'role': 'Branch Managereee'},
    {'name': 'روز ابو خضر', 'email': 'rose.abukhader@root-jo.com', 'mobile': '962790000000', 'branch': 'روت', 'role': 'Branch Managereee'},
    {'name': 'عبدالعزيز محمد محترك الرويلي', 'email': 'abdulaziz.alruwaili@ararhni.com', 'mobile': '966502000000', 'branch': 'القريات', 'role': 'موظف'},
    {'name': 'tester', 'email': 'rawanseliem3@gmail.com', 'mobile': '966599000000', 'branch': 'عرعر', 'role': ''},
    {'name': 'منار العنزى', 'email': 'manar_alanzi@ararhni.com', 'mobile': '966561000000', 'branch': 'المورد الوافي', 'role': 'موظف'},
    {'name': 'نسرين ثروت نسرين ثروت المورد الوافى', 'email': 'nasreen.tharwat@ararhni.com', 'mobile': '966561000000', 'branch': 'المورد الوافي', 'role': 'موظف'},
    {'name': 'نوف الحربي', 'email': 'nofe_elharbi@ararhni.com', 'mobile': '966561000000', 'branch': 'المورد الوافي', 'role': 'موظف'},
    {'name': 'المهرا مدالله عويدات العنزي', 'email': 'elmohra_menatallaah@ararhni.com', 'mobile': '966554000000', 'branch': 'المورد الوافي', 'role': 'موظف'},
    {'name': 'هيام عمر علي عبدالله', 'email': 'drhoyam@ararhni.com', 'mobile': '966551000000', 'branch': 'المورد الوافي', 'role': 'موظف'},
    {'name': 'شهد خالد خليل الضويمر', 'email': 'shahad982.k@ararhni.com', 'mobile': '966551000000', 'branch': 'المورد الوافي', 'role': 'مشرف تدريب'},
    {'name': 'هيا عبدالرحمن الفالح', 'email': 'haya-alfaleh2024@ararhni.com', 'mobile': '966551000000', 'branch': 'المورد الوافي', 'role': 'Branch Managereee'},
    {'name': 'كمال حسنى', 'email': 'kamal_hosny@ararhni.com', 'mobile': '966569000000', 'branch': 'عرعر', 'role': 'موظف'},
    {'name': 'احلام العتيبى', 'email': 'ahlam.alotaibi@ararhni.com', 'mobile': '966570000000', 'branch': 'الفاو رياض', 'role': 'موظف'},
    {'name': 'د/ صفوة', 'email': 'safwa@ararhni.com', 'mobile': '966509000000', 'branch': 'المورد الوافي', 'role': 'موظف'},
    {'name': 'سيد فرج', 'email': 'sayed_faraj@ararhni.com', 'mobile': '966570000000', 'branch': 'سكاكا', 'role': 'موظف'},
    {'name': 'يزيد سرحان العنزي', 'email': 'yazeed_sarhan@ararhni.com', 'mobile': '966507000000', 'branch': 'عرعر', 'role': 'موظف'},
    {'name': 'فرج عويد العنزي', 'email': 'farage_alanzi@ararhni.com', 'mobile': '966567000000', 'branch': 'عرعر', 'role': 'موظف'},
    {'name': 'علي حسين الاشجعي', 'email': 'ali_hussuin@ararhni.com', 'mobile': '966536000000', 'branch': 'عرعر', 'role': 'موظف'},
    {'name': 'طاهر محمد', 'email': 'taher_mohammad@ararhni.com', 'mobile': '966507000000', 'branch': 'عرعر', 'role': 'موظف'},
    {'name': 'سعيد كمال', 'email': 'sead_kamal@ararhni.com', 'mobile': '966559000000', 'branch': 'معهد الثقة الدائمة', 'role': 'المكتب الرئيسى HR & Accounting & مدير الأفرع'},
    {'name': 'سعد دياب', 'email': 'saad_diab@ararhni.com', 'mobile': '966553000000', 'branch': 'عرعر', 'role': 'المكتب الرئيسى HR & Accounting & مدير الأفرع'},
    {'name': 'مصطفى صلاح', 'email': 'mustafaa_salah@ararhni.com', 'mobile': '966543000000', 'branch': 'مؤسسة صرخة', 'role': 'موظف'},
    {'name': 'اايهاب لطفى', 'email': 'ehablotfy442@gmail.com', 'mobile': '966564000000', 'branch': 'حفر الباطن', 'role': 'موظف'},
    {'name': 'عاطف عبدالرحمن', 'email': 'aatefgalhom@gmail.com', 'mobile': '966569000000', 'branch': 'حفر الباطن', 'role': 'موظف'},
    {'name': 'تهاني عائض لافي العنزي', 'email': 'tahany_alanazi@ararhni.com', 'mobile': '966532000000', 'branch': 'معهد الثقة الدائمة', 'role': 'موظف'},
    {'name': 'تغريد فيصل حوران العنزي', 'email': 'taghreed_fisal@ararhni.com', 'mobile': '966530000000', 'branch': 'معهد الثقة الدائمة', 'role': 'موظف'},
    {'name': 'محمد عواض الحارثي', 'email': 'mohamed.awad@ararhni.com', 'mobile': '966550000000', 'branch': 'الفاو رياض', 'role': 'موظف'},
    {'name': 'صقر احمد الشمري', 'email': 'saqr.shamry@ararhni.com', 'mobile': '966557000000', 'branch': 'الفاو رياض', 'role': 'موظف'},
    {'name': 'زهيرة جمال ناصر القضاة', 'email': 'marketing-manager@ararhni.com', 'mobile': '966539000000', 'branch': 'القصيم', 'role': 'مشرف تدريب'},
    {'name': 'لدن أحمد العييري', 'email': 'dan_alyiri@ararhni.com', 'mobile': '966561000000', 'branch': 'القصيم', 'role': 'موظف'},
    {'name': 'ابتهال سليمان الصقعوب', 'email': 'ibtihal.alsaquob@ararhni.com', 'mobile': '966570000000', 'branch': 'القصيم', 'role': 'موظف'},
    {'name': 'عبدالله يحيى القرني', 'email': 'afaaqaltatawour@ararhni.com', 'mobile': '966539000000', 'branch': 'آفاق التطوير - الدمام', 'role': 'موظف'},
    {'name': 'أحمد سعيد', 'email': 'ahmed.saed@ararhni.com', 'mobile': '966506000000', 'branch': 'آفاق التطوير - الدمام', 'role': 'موظف'},
    {'name': 'محمود قسام', 'email': 'mahmoudashraf374@ararhni.com', 'mobile': '966540000000', 'branch': 'آفاق التطوير - الدمام', 'role': 'موظف'},
    {'name': 'جيهان اشرف حسن عبدة', 'email': 'gehan.ashraf@ararhni.com', 'mobile': '966535000000', 'branch': 'معهد الثقة الدائمة', 'role': 'موظف'},
    {'name': 'ابتهال الحربى', 'email': 'ebtehal.alharbi@ararhni.com', 'mobile': '966512000000', 'branch': 'حفر الباطن', 'role': 'موظف'},
    {'name': 'نوف الحربى', 'email': 'nof_elharby@ararhni.com', 'mobile': '966512000000', 'branch': 'القصيم', 'role': 'موظف'},
    {'name': 'محمد خاطر', 'email': 'mohammed_khater@ararhni.com', 'mobile': '966554000000', 'branch': 'القصيم', 'role': 'موظف'},
    {'name': 'لمى الحربي', 'email': 'lama.alharbi@ararhni.com', 'mobile': '966512000000', 'branch': 'القصيم', 'role': 'موظف'},
    {'name': 'عمر فالح', 'email': 'omar.faleh10@ararhni.com', 'mobile': '966523000000', 'branch': 'القصيم', 'role': 'موظف'},
    {'name': 'على ابراهيم', 'email': 'ali.ibrahim@ararhni.com', 'mobile': '966561000000', 'branch': 'القصيم', 'role': 'موظف'},
    {'name': 'ابوالقاسم مبارك عباس مبارك', 'email': 'abwalqasim2025@ararhni.com', 'mobile': '966554000000', 'branch': 'القصيم', 'role': 'مشرف تدريب'},
    {'name': 'منيره عبدالله ناصر خبراني', 'email': 'munera_khbrani@ararhni.com', 'mobile': '966591000000', 'branch': 'حفر الباطن', 'role': 'موظف'},
    {'name': 'لمار عبدالله حسين والبي', 'email': 'lamar_hassan@ararhni.com', 'mobile': '966552000000', 'branch': 'حفر الباطن', 'role': 'موظف'},
    {'name': 'دانه زايد حمود الحربي', 'email': 'dana_alharbi@ararhni.com', 'mobile': '966552000000', 'branch': 'حفر الباطن', 'role': 'موظف'},
    {'name': 'عبير محمد حوران العنزي', 'email': 'abeer_alanazi@ararhni.com', 'mobile': '966502000000', 'branch': 'حفر الباطن', 'role': 'موظف'},
    {'name': 'عبداله تركي', 'email': 'abdullah.turky@ararhni.com', 'mobile': '966502000000', 'branch': 'حفر الباطن', 'role': 'موظف'},
    {'name': 'ثامر ساير العنزي', 'email': 'thamer.s@ararhni.com', 'mobile': '966556000000', 'branch': 'حفر الباطن', 'role': 'موظف'},
    {'name': 'عبدالرحمن الطرقي', 'email': 'abd.alturqi@ararhni.com', 'mobile': '966569000000', 'branch': 'حفر الباطن', 'role': 'موظف'},
    {'name': 'نايف ناجي عبدالرحمن', 'email': 'naif_abdulrahman@ararhni.com', 'mobile': '966560000000', 'branch': 'آفاق التطوير - الدمام', 'role': 'موظف'},
    {'name': 'عبدالله شبيب العساف', 'email': 'abdullah.asaf@ararhni.com', 'mobile': '966547000000', 'branch': 'آفاق التطوير - الدمام', 'role': 'موظف'},
    {'name': 'احمد نصرالدين', 'email': 'a.s.nasreldin@ararhni.com', 'mobile': '966582000000', 'branch': 'آفاق التطوير - الدمام', 'role': 'موظف'},
    {'name': 'منى منصور العسيري', 'email': 'aseerimona90@ararhni.com', 'mobile': '966534000000', 'branch': 'آفاق التطوير - الدمام', 'role': 'موظف'},
    {'name': 'بديعه عرفه', 'email': 'badea_shalaby@ararhni.com', 'mobile': '966542000000', 'branch': 'آفاق التطوير - الدمام', 'role': 'موظف'},
    {'name': 'سارا مساعد الفريدي', 'email': 'sarah.alfaridi@ararhni.com', 'mobile': '966538000000', 'branch': 'آفاق التطوير - الدمام', 'role': 'مشرف تدريب'},
    {'name': 'اواب عبدالله', 'email': 'awab.abdullah@ararhni.com', 'mobile': '966569000000', 'branch': 'معهد الثقة الدائمة', 'role': 'موظف'},
    {'name': 'محمد خلف', 'email': 'moh.khalil@ararhni.com', 'mobile': '966546000000', 'branch': 'معهد الثقة الدائمة', 'role': 'موظف'},
    {'name': 'إيمان فتحي محمود', 'email': 'eman.fathy@ararhni.com', 'mobile': '966543000000', 'branch': 'معهد الثقة الدائمة', 'role': 'موظف'},
    {'name': 'مشاعل زيد علي المزيد', 'email': 'mashael_almazeed@ararhni.com', 'mobile': '966593000000', 'branch': 'سكاكا', 'role': 'موظف'},
    {'name': 'ألماس عبدالرحمن فهد العنزي', 'email': 'almas_alanazi@ararhni.com', 'mobile': '966507000000', 'branch': 'سكاكا', 'role': 'موظف'},
    {'name': 'وسام نايف عبدالرحمن السرحاني', 'email': 'wisam_alsarhan@ararhni.com', 'mobile': '966554000000', 'branch': 'سكاكا', 'role': 'موظف'},
    {'name': 'أفنان فواز خلف الحيزان', 'email': 'afnan_alhayzan@ararhni.com', 'mobile': '966538000000', 'branch': 'سكاكا', 'role': 'موظف'},
    {'name': 'روان صالح محمد السعران', 'email': 'rowan_alsaran@ararhni.com', 'mobile': '966501000000', 'branch': 'سكاكا', 'role': 'موظف'},
    {'name': 'محمد قطب بسيوني الفلال', 'email': 'muhammad_alfallal@ararhni.com', 'mobile': '966533000000', 'branch': 'سكاكا', 'role': 'موظف'},
    {'name': 'خطاب عبدالرحمن شويحط الرويلي', 'email': 'khitab_alrwaily@ararhni.com', 'mobile': '966558000000', 'branch': 'سكاكا', 'role': 'موظف'},
    {'name': 'عبدالعزيز عوض عاقل الرويلي', 'email': 'abdulaziz_alrwaily@ararhni.com', 'mobile': '966597000000', 'branch': 'سكاكا', 'role': 'موظف'},
    {'name': 'موفق نائب سليمان الشمري', 'email': 'moufaq_alshammari@ararhni.com', 'mobile': '966578000000', 'branch': 'سكاكا', 'role': 'موظف'},
    {'name': 'محمد يوسف عبد أبوالشيخ', 'email': 'muhammad_abualsheikh@ararhni.com', 'mobile': '966578000000', 'branch': 'سكاكا', 'role': 'موظف'},
    {'name': 'عبدالرحمن عبدالله فلاح الدندني', 'email': 'abdulrahman_aldandani@ararhni.com', 'mobile': '966532000000', 'branch': 'سكاكا', 'role': 'موظف'},
    {'name': 'بندر محمد سليمان الدرعان', 'email': 'bandar_aldirean@ararhni.com', 'mobile': '966532000000', 'branch': 'سكاكا', 'role': 'موظف'},
    {'name': 'مالك عيد علي الضويحي', 'email': 'malik_aldawihii@ararhni.com', 'mobile': '966532000000', 'branch': 'سكاكا', 'role': 'موظف'},
    {'name': 'عبدالمعطي اسماعيل الدرعان', 'email': 'shahaiieI_aldirean@ararhni.com', 'mobile': '966558000000', 'branch': 'سكاكا', 'role': 'موظف'},
    {'name': 'طلال قاعد', 'email': 'talal.alshalikhi@ararhni.com', 'mobile': '966539000000', 'branch': 'المعهد الاهلي المنصورية', 'role': 'Branch Managereee'},
    {'name': 'خالد محمد ناصر', 'email': 'khaled.naser@ararhni.com', 'mobile': '966535000000', 'branch': 'الفاو رياض', 'role': 'موظف'},
    {'name': 'لافي خليف العنزي', 'email': 'lafi_alenezi@ararhni.com', 'mobile': '966555000000', 'branch': 'الفاو رياض', 'role': 'موظف'},
    {'name': 'سلطان ثامر ثاير العنزى', 'email': 'sultan.alanazi@ararhni.com', 'mobile': '966567000000', 'branch': 'الفاو رياض', 'role': 'Branch Managereee'},
    {'name': 'اثير العنزى', 'email': 'atheer_mohammad@ararhni.com', 'mobile': '966555000000', 'branch': 'الفاو رياض', 'role': 'موظف'},
    {'name': 'محمد محمود الليثي', 'email': 'mohammed.ahmed@ararhni.com', 'mobile': '966559000000', 'branch': 'الفاو رياض', 'role': 'موظف'},
    {'name': 'عبد الله مبارك', 'email': 'abdo.18@ararhni.com', 'mobile': '966553000000', 'branch': 'الفاو رياض', 'role': 'موظف'},
    {'name': 'مشعل فارس العنزى', 'email': 'm.f.alanzi@ararhni.com', 'mobile': '966560000000', 'branch': 'عرعر', 'role': 'موظف'},
    {'name': 'فواز عبيد عبدالعزيز الهذال', 'email': 'fawaz.alhedhal@ararhni.com', 'mobile': '966558000000', 'branch': 'عرعر', 'role': 'موظف'},
    {'name': 'عبدالعزيز فهد رويحل العنزي', 'email': 'abdulaziz.fahad.alenezi@ararhni.com', 'mobile': '966533000000', 'branch': 'عرعر', 'role': 'موظف'},
    {'name': 'شكري عبد النبي مصطفى محمد', 'email': 'shokry.abdelnaby.mostafa@ararhni.com', 'mobile': '966507000000', 'branch': 'عرعر', 'role': 'مشرف تدريب'},
    {'name': 'احمد أبو عيطه', 'email': 'ahmed.abuaita@ararhni.com', 'mobile': '966508000000', 'branch': 'آفاق التطوير - الدمام', 'role': 'Branch Managereee'},
    {'name': 'محمد جزاف اسماعيل', 'email': 'ararnni@gmail.com', 'mobile': '966555000000', 'branch': 'عرعر', 'role': 'المكتب الرئيسى HR & Accounting & مدير الأفرع'},
    {'name': 'صقر بن ثامر الوثيرى', 'email': 'saqr_alanizi@ararhni.com', 'mobile': '966567000000', 'branch': 'حفر الباطن', 'role': 'المكتب الرئيسى HR & Accounting & مدير الأفرع'},
    {'name': 'وسام ابوخضر', 'email': 'dev-manager@ararhni.com', 'mobile': '966570000000', 'branch': 'عرعر', 'role': 'CEO'},
    {'name': 'هيثم صلاح هدية', 'email': 'haitham.salah@ararhni.com', 'mobile': '966553000000', 'branch': 'عرعر', 'role': 'موظف'},
    {'name': 'احمد عبدالحكيم', 'email': 'a.hakim@ararhni.com', 'mobile': '966502000000', 'branch': 'الفاو رياض', 'role': 'موظف'},
    {'name': 'حمدى', 'email': 'hamdy.adam@ararhni.com', 'mobile': '569736794', 'branch': 'مؤسسة صرخة', 'role': ''},
    {'name': 'شيماء محمد جاااد', 'email': 'shaima.jadallah@ararhni.com', 'mobile': '593761628', 'branch': 'مؤسسة صرخة', 'role': 'موظف'},
    {'name': 'محمد نبيل', 'email': 'moh.nabil@ararhni.com', 'mobile': '966540000000', 'branch': 'آفاق التطوير - الدمام', 'role': 'موظف'},
    {'name': 'محمد طه مشعل', 'email': 'mohammed.mashal@ararhni.com', 'mobile': '966500000000', 'branch': 'آفاق التطوير - الدمام', 'role': 'موظف'},
    {'name': 'فارس القحطاني', 'email': 'fares.q1422@ararhni.com', 'mobile': '549846627', 'branch': 'آفاق التطوير - الدمام', 'role': 'موظف'},
    {'name': 'علي آل محمود', 'email': 'ali_almahmoud@ararhni.com', 'mobile': '580036132', 'branch': 'آفاق التطوير - الدمام', 'role': 'موظف'},
    {'name': 'دلال الخالدي', 'email': 'dalal.alkhalidi@ararhni.com', 'mobile': '966598000000', 'branch': 'آفاق التطوير - الدمام', 'role': 'موظف'},
    {'name': 'فارس السويلم', 'email': 'fariis1188@ararhni.com', 'mobile': '966563000000', 'branch': 'القصيم', 'role': 'موظف'},
    {'name': 'علي العقيل', 'email': 'ali7.aqeel@ararhni.com', 'mobile': '966509000000', 'branch': 'القصيم', 'role': 'موظف'},
    {'name': 'اروى يوسف الدغيري', 'email': 'arwa174198@ararhni.com', 'mobile': '966563000000', 'branch': 'القصيم', 'role': 'موظف'},
    {'name': 'افنان بنت عبدالله البازعي', 'email': 'afnan_bazz@ararhni.com', 'mobile': '966570000000', 'branch': 'القصيم', 'role': 'موظف'},
    {'name': 'ابراهيم العبرة', 'email': 'abdulmalik.kreidis@ararhni.com', 'mobile': '966533000000', 'branch': 'القصيم', 'role': 'موظف'},
    {'name': 'احمد عثمان', 'email': 'a_othman@ararhni.com', 'mobile': '966534000000', 'branch': 'القصيم', 'role': 'Branch Managereee'},
    {'name': 'بدر عطاالله العنزي', 'email': 'bader.alanazi@ararhni.com', 'mobile': '966537000000', 'branch': 'حفر الباطن', 'role': 'موظف'},
    {'name': 'مذود حمود العنزي', 'email': 'mudhawwd.aleanzi@ararhni.com', 'mobile': '504322597', 'branch': 'حفر الباطن', 'role': 'موظف'},
    {'name': 'محمود طه', 'email': 'mahmoud.taha1019@gmail.com', 'mobile': '535745365', 'branch': 'حفر الباطن', 'role': 'موظف'},
    {'name': 'محمد حسانين', 'email': 'mohamed.hassanein@ararhni.com', 'mobile': '966501000000', 'branch': 'حفر الباطن', 'role': 'موظف'},
    {'name': 'فيصل نائف المطيري', 'email': 'faisal.almutairi@ararhni.com', 'mobile': '966508000000', 'branch': 'حفر الباطن', 'role': 'موظف'},
    {'name': 'فتحي ملح', 'email': 'fathi@ararhni.com', 'mobile': '549828035', 'branch': 'حفر الباطن', 'role': 'موظف'},
    {'name': 'عبدالله عقلاء العنزي', 'email': 'abdullah.alanazi@ararhni.com', 'mobile': '555927241', 'branch': 'حفر الباطن', 'role': 'موظف'},
    {'name': 'عبدالعزيز ملوح', 'email': 'abdulaziz.malouh@ararhni.com', 'mobile': '553046127', 'branch': 'حفر الباطن', 'role': 'موظف'},
    {'name': 'عبدالرحمن الشمري', 'email': 'abdulrahman.alshammari@ararhni.com', 'mobile': '561028533', 'branch': 'حفر الباطن', 'role': 'موظف'},
    {'name': 'خالد الطيب', 'email': 'khalid.altayb@ararhni.com', 'mobile': '556548262', 'branch': 'حفر الباطن', 'role': 'موظف'},
    {'name': 'تامر عجيزة', 'email': 'tamer.a@ararhni.com', 'mobile': '550175976', 'branch': 'حفر الباطن', 'role': 'موظف'},
    {'name': 'بلال الحبشي', 'email': 'belal.h@ararhni.com', 'mobile': '535829530', 'branch': 'حفر الباطن', 'role': 'موظف'},
    {'name': 'احمد فالح الشمري', 'email': 'a.faleh@ararhni.com', 'mobile': '560302578', 'branch': 'حفر الباطن', 'role': 'موظف'},
    {'name': 'هشام عمر', 'email': 'hisham.omar@ararhni.com', 'mobile': '507153592', 'branch': 'حفر الباطن', 'role': 'موظف'},
    {'name': 'عبيد الشمري', 'email': 'obid.alshammari@ararhni.com', 'mobile': '533491571', 'branch': 'حفر الباطن', 'role': 'موظف'},
    {'name': 'ممدوح عبدالله العنزي', 'email': 'mamdoh@ararhni.com', 'mobile': '552673327', 'branch': 'حفر الباطن', 'role': 'موظف'},
    {'name': 'مشعل نومان العنزي', 'email': 'meshaal.alanazi@ararhni.com', 'mobile': '555791861', 'branch': 'حفر الباطن', 'role': 'موظف'},
    {'name': 'فاطمة الشمري', 'email': 'fatsh1225@gmail.com', 'mobile': '508344700', 'branch': 'حفر الباطن', 'role': 'موظف'},
    {'name': 'عبدالله حمود الشمري', 'email': 'abd.alshammary@ararhni.com', 'mobile': '502105650', 'branch': 'حفر الباطن', 'role': 'المكتب الرئيسى HR & Accounting & مدير الأفرع'},
    {'name': 'محمد كامل', 'email': 'm.kamel@ararhni.com', 'mobile': '502858217', 'branch': 'حفر الباطن', 'role': 'موظف'},
    {'name': 'متعب العنزي', 'email': 'mutaab.nori@ararhni.com', 'mobile': '540541312', 'branch': 'حفر الباطن', 'role': 'موظف'},
    {'name': 'فواز مخلف الشمري', 'email': 'fawaz.mek@ararhni.com', 'mobile': '599955989', 'branch': 'حفر الباطن', 'role': 'موظف'},
    {'name': 'فهد شفق الشمري', 'email': 'fahad.shf@ararhni.com', 'mobile': '551910195', 'branch': 'حفر الباطن', 'role': 'مشرف تدريب'},
    {'name': 'عبدالهادي نصر', 'email': 'abdelhadynasr@ararhni.com', 'mobile': '966591000000', 'branch': 'حفر الباطن', 'role': 'موظف'},
    {'name': 'سعد شفق الشمري', 'email': 'saad@ararhni.com', 'mobile': '554881850', 'branch': 'حفر الباطن', 'role': 'موظف'},
    {'name': 'فواز حماد الشمري', 'email': 'f.alshammary@ararhni.com', 'mobile': '509121638', 'branch': 'حفر الباطن', 'role': 'موظف'},
    {'name': 'منصور العنزي', 'email': 'mansuranad2000@gmail.com', 'mobile': '531373396', 'branch': 'عرعر', 'role': 'موظف'},
    {'name': 'ماهر العنزي', 'email': 'maher@ararhni.com', 'mobile': '557622461', 'branch': 'عرعر', 'role': 'موظف'},
    {'name': 'عمر رمضان أبوبكر', 'email': 'omarramadan42036@ararhni.com', 'mobile': '966557000000', 'branch': 'عرعر', 'role': 'موظف'},
    {'name': 'علاء الدين عمر', 'email': 'abujayyab10@ararhni.com', 'mobile': '966508000000', 'branch': 'عرعر', 'role': 'موظف'},
    {'name': 'عصام عبدالعظيم', 'email': 'esam_yousef@ararhni.com', 'mobile': '966535000000', 'branch': 'عرعر', 'role': 'موظف'},
    {'name': 'عبدالقادر محمود', 'email': 'abdelgader@ararhni.com', 'mobile': '502599313', 'branch': 'عرعر', 'role': ''},
    {'name': 'عبدالاله العنزي', 'email': 'abdelelahali@ararhni.com', 'mobile': '563206870', 'branch': 'عرعر', 'role': 'مشرف تدريب'},
    {'name': 'راشد القضاة', 'email': 'rashed.alqudah@ararhni.com', 'mobile': '562956263', 'branch': 'عرعر', 'role': 'موظف'},
    {'name': 'خالد عبدالحكيم', 'email': 'khalid.alsyed@ararhni.com', 'mobile': '966540000000', 'branch': 'عرعر', 'role': 'موظف'},
    {'name': 'احمد احمد عيسي', 'email': 'ahmedessa2025@ararhni.com', 'mobile': '570053531', 'branch': 'عرعر', 'role': 'موظف'},
    {'name': 'احمد صلاح', 'email': 'a_salah@ararhni.com', 'mobile': '506988845', 'branch': 'عرعر', 'role': 'موظف'},
    {'name': 'عمر أبو لاوي', 'email': 'omarabulawid@gmail.com', 'mobile': '580940178', 'branch': 'عرعر', 'role': 'موظف'},
    {'name': 'أسامة حمزة', 'email': 'o.h.alhussien@ararhni.com', 'mobile': '503308007', 'branch': 'عرعر', 'role': 'موظف'},
    {'name': 'مصطفي عمر', 'email': 'muostafa@ararhni.com', 'mobile': '966549000000', 'branch': 'عرعر', 'role': 'موظف'},
    {'name': 'طارق نبيل', 'email': 'tareknabil98@ararhni.com', 'mobile': '966552000000', 'branch': 'عرعر', 'role': 'موظف'},
    {'name': 'رايد العنزي', 'email': 'raed@ararhni.com', 'mobile': '550858395', 'branch': 'عرعر', 'role': 'المكتب الرئيسى HR & Accounting & مدير الأفرع'},
    {'name': 'فيصل الرويلي', 'email': 'faisalalrwele512@ararhni.com', 'mobile': '552399009', 'branch': 'عرعر', 'role': 'المكتب الرئيسى HR & Accounting & مدير الأفرع'},
    {'name': 'محمد رحيم', 'email': 'muhammad_alaleem@ararhni.com', 'mobile': '966531000000', 'branch': 'سكاكا', 'role': 'مشرف تدريب'},
    {'name': 'فرح العنزي', 'email': 'farah_alanazi@ararhni.com', 'mobile': '966537000000', 'branch': 'سكاكا', 'role': 'موظف'},
    {'name': 'علي عمر', 'email': 'ali_babiker@ararhni.com', 'mobile': '532430022', 'branch': 'سكاكا', 'role': 'موظف'},
    {'name': 'علاء علي', 'email': 'alaa_ali@ararhni.com', 'mobile': '966583000000', 'branch': 'سكاكا', 'role': 'موظف'},
    {'name': 'عبدالواحد الحموان', 'email': 'abdulwahed_aihamwan@ararhni.com', 'mobile': '966538000000', 'branch': 'سكاكا', 'role': ''},
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
    # ─── 1. Ensure roles exist ─────────────────────────────────────
    print('=== Ensuring Roles ===')
    roles_map = {}
    for role_name in ROLES_TO_ENSURE:
        role, created = Role.objects.get_or_create(name=role_name)
        roles_map[role_name] = role
        print(f'{"CREATED" if created else "EXISTS"}: {role_name}')
    print()

    # ─── 2. Create missing branches/companies ──────────────────────
    print('=== Ensuring Branches/Companies ===')

    # Ensure company and branch for مؤسسة صرخة
    company_sarakh, company_created = Company.objects.get_or_create(
        name='مؤسسة صرخة',
        defaults={'sub_name': ''}
    )
    if company_created:
        print(f'CREATED company: مؤسسة صرخة')
    else:
        print(f'EXISTS company: مؤسسة صرخة')

    current_max = 0
    if Branch.objects.exists():
        current_max = Branch.objects.order_by('-code').first().code
    counter = current_max + 1

    branch_sarakh, branch_created = Branch.objects.get_or_create(
        name='مؤسسة صرخة',
        defaults={
            'company': company_sarakh,
            'code': counter,
            'sub_name': '',
        }
    )
    if branch_created:
        counter += 1
        print(f'CREATED branch: مؤسسة صرخة (code={branch_sarakh.code})')
    else:
        print(f'EXISTS branch: مؤسسة صرخة (code={branch_sarakh.code})')

    # Build branches lookup
    branches_map = {}
    for branch in Branch.objects.all():
        branches_map[branch.name] = branch
    print()

    # ─── 3. Get default team ───────────────────────────────────────
    team = None
    try:
        team = Team.objects.get(name=DEFAULT_TEAM_NAME)
        print(f'Using team: {team.name}')
    except Team.DoesNotExist:
        print(f'WARNING: Team "{DEFAULT_TEAM_NAME}" not found.')
    print()

    # ─── 4. Create/Update users ────────────────────────────────────
    print('=== Creating/Updating Users ===')
    created_users = 0
    updated_users = 0
    created_employee_roles = 0
    skipped = 0

    for idx, u in enumerate(users_data, 1):
        full_name = u['name']
        email = u['email'].strip().lower()
        mobile = u['mobile']
        source_branch = u['branch']
        source_role = u['role']

        first_name, second_name, third_name, forth_name = split_name(full_name)

        # Map branch
        db_branch_name = BRANCH_NAME_MAP.get(source_branch)
        branch = branches_map.get(db_branch_name) if db_branch_name else None

        # Map role
        db_role_name = ROLE_NAME_MAP.get(source_role)
        role = roles_map.get(db_role_name) if db_role_name else None

        if not branch:
            print(f'[{idx}] SKIP: Branch "{source_branch}" -> "{db_branch_name}" not found for {full_name}')
            skipped += 1
            continue

        if not role:
            print(f'[{idx}] SKIP: Role "{source_role}" -> "{db_role_name}" not found for {full_name}')
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

        # Create EmployeeRole if not exists
        er, er_created = EmployeeRole.objects.get_or_create(
            person=user,
            role=role,
            branch=branch
        )
        if er_created:
            created_employee_roles += 1

        print(f'[{idx}] {status}: {full_name} | {email} | {db_branch_name} | {db_role_name}')

    print()
    print('=' * 60)
    print(f'Users Created: {created_users}')
    print(f'Users Updated: {updated_users}')
    print(f'EmployeeRoles Created: {created_employee_roles}')
    print(f'Skipped: {skipped}')
    print(f'Default Password: {DEFAULT_PASSWORD}')
    print('=' * 60)


if __name__ == '__main__':
    main()
