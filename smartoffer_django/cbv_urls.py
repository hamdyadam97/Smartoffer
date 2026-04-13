"""
Class-Based Views URLs - All Apps
"""
from django.urls import path

# Core CBV
from core.cbv_views import (
    CompanyListCreateAPIView, CompanyDetailAPIView,
    BranchListCreateAPIView, BranchDetailAPIView,
    BranchStatisticsAPIView, BranchActiveListAPIView,
    BankListCreateAPIView, BankDetailAPIView,
    MasterCategoryListCreateAPIView, MasterCategoryDetailAPIView
)

# Accounts CBV
from accounts.cbv_views import (
    LoginAPIView, LogoutAPIView,
    PersonListCreateAPIView, PersonDetailAPIView, CurrentUserAPIView,
    TeamListCreateAPIView, TeamDetailAPIView,
    RoleListCreateAPIView, RoleDetailAPIView,
    EmployeeRoleListCreateAPIView, EmployeeRoleDetailAPIView,
    EmployeePerformanceListCreateAPIView, EmployeePerformanceDetailAPIView,
    BranchAccessListCreateAPIView, BranchAccessDetailAPIView
)

# Students CBV
from students.cbv_views import (
    ContactListCreateAPIView, ContactDetailAPIView,
    StudentListCreateAPIView, StudentDetailAPIView,
    StudentCoursesAPIView
)

# Courses CBV
from courses.cbv_views import (
    MasterListCreateAPIView, MasterDetailAPIView, MasterCoursesAPIView,
    CourseListCreateAPIView, CourseDetailAPIView,
    CourseStudentsAPIView, CourseStatisticsAPIView
)

# Registrations CBV
from registrations.cbv_views import (
    AccountListCreateAPIView, AccountDetailAPIView,
    AccountPaymentsAPIView, AccountSummaryAPIView,
    AttachTypeListCreateAPIView,
    AttachListCreateAPIView, AttachDetailAPIView,
    AccountAttachListCreateAPIView,
    AccountConditionListCreateAPIView, AccountConditionDetailAPIView,
    AccountNoteListCreateAPIView, AccountNoteDetailAPIView
)

# Finance CBV
from finance.cbv_views import (
    PaymentListCreateAPIView, PaymentDetailAPIView, PaymentStatisticsAPIView,
    PaymentOutListCreateAPIView,
    DepositListCreateAPIView, DepositDetailAPIView,
    WithdrawListCreateAPIView,
    BillBuyTypeListCreateAPIView,
    BillBuyListCreateAPIView, BillBuyDetailAPIView,
    OfferListCreateAPIView, OfferDetailAPIView, OfferConvertAPIView,
    CallListCreateAPIView, CallDetailAPIView
)

urlpatterns = [
    # ============================================================
    # Authentication
    # ============================================================
    path('auth/login/', LoginAPIView.as_view(), name='cbv-login'),
    path('auth/logout/', LogoutAPIView.as_view(), name='cbv-logout'),
    
    # ============================================================
    # Accounts
    # ============================================================
    path('persons/', PersonListCreateAPIView.as_view(), name='cbv-person-list'),
    path('persons/me/', CurrentUserAPIView.as_view(), name='cbv-person-me'),
    path('persons/<int:pk>/', PersonDetailAPIView.as_view(), name='cbv-person-detail'),
    
    path('teams/', TeamListCreateAPIView.as_view(), name='cbv-team-list'),
    path('teams/<int:pk>/', TeamDetailAPIView.as_view(), name='cbv-team-detail'),
    
    path('roles/', RoleListCreateAPIView.as_view(), name='cbv-role-list'),
    path('roles/<int:pk>/', RoleDetailAPIView.as_view(), name='cbv-role-detail'),
    
    path('employee-roles/', EmployeeRoleListCreateAPIView.as_view(), name='cbv-employee-role-list'),
    path('employee-roles/<int:pk>/', EmployeeRoleDetailAPIView.as_view(), name='cbv-employee-role-detail'),
    
    path('employee-performances/', EmployeePerformanceListCreateAPIView.as_view(), name='cbv-performance-list'),
    path('employee-performances/<int:pk>/', EmployeePerformanceDetailAPIView.as_view(), name='cbv-performance-detail'),
    
    path('branch-accesses/', BranchAccessListCreateAPIView.as_view(), name='cbv-branch-access-list'),
    path('branch-accesses/<int:pk>/', BranchAccessDetailAPIView.as_view(), name='cbv-branch-access-detail'),
    
    # ============================================================
    # Core
    # ============================================================
    path('companies/', CompanyListCreateAPIView.as_view(), name='cbv-company-list'),
    path('companies/<int:pk>/', CompanyDetailAPIView.as_view(), name='cbv-company-detail'),
    
    path('branches/', BranchListCreateAPIView.as_view(), name='cbv-branch-list'),
    path('branches/active/', BranchActiveListAPIView.as_view(), name='cbv-branch-active'),
    path('branches/<int:pk>/', BranchDetailAPIView.as_view(), name='cbv-branch-detail'),
    path('branches/<int:pk>/statistics/', BranchStatisticsAPIView.as_view(), name='cbv-branch-statistics'),
    
    path('banks/', BankListCreateAPIView.as_view(), name='cbv-bank-list'),
    path('banks/<int:pk>/', BankDetailAPIView.as_view(), name='cbv-bank-detail'),
    
    path('master-categories/', MasterCategoryListCreateAPIView.as_view(), name='cbv-mastercategory-list'),
    path('master-categories/<int:pk>/', MasterCategoryDetailAPIView.as_view(), name='cbv-mastercategory-detail'),
    
    # ============================================================
    # Students
    # ============================================================
    path('contacts/', ContactListCreateAPIView.as_view(), name='cbv-contact-list'),
    path('contacts/<int:pk>/', ContactDetailAPIView.as_view(), name='cbv-contact-detail'),
    
    path('students/', StudentListCreateAPIView.as_view(), name='cbv-student-list'),
    path('students/<int:pk>/', StudentDetailAPIView.as_view(), name='cbv-student-detail'),
    path('students/<int:pk>/courses/', StudentCoursesAPIView.as_view(), name='cbv-student-courses'),
    
    # ============================================================
    # Courses
    # ============================================================
    path('masters/', MasterListCreateAPIView.as_view(), name='cbv-master-list'),
    path('masters/<int:pk>/', MasterDetailAPIView.as_view(), name='cbv-master-detail'),
    path('masters/<int:pk>/courses/', MasterCoursesAPIView.as_view(), name='cbv-master-courses'),
    
    path('courses/', CourseListCreateAPIView.as_view(), name='cbv-course-list'),
    path('courses/<int:pk>/', CourseDetailAPIView.as_view(), name='cbv-course-detail'),
    path('courses/<int:pk>/students/', CourseStudentsAPIView.as_view(), name='cbv-course-students'),
    path('courses/<int:pk>/statistics/', CourseStatisticsAPIView.as_view(), name='cbv-course-statistics'),
    
    # ============================================================
    # Registrations
    # ============================================================
    path('accounts/', AccountListCreateAPIView.as_view(), name='cbv-account-list'),
    path('accounts/summary/', AccountSummaryAPIView.as_view(), name='cbv-account-summary'),
    path('accounts/<int:pk>/', AccountDetailAPIView.as_view(), name='cbv-account-detail'),
    path('accounts/<int:pk>/payments/', AccountPaymentsAPIView.as_view(), name='cbv-account-payments'),
    
    path('attach-types/', AttachTypeListCreateAPIView.as_view(), name='cbv-attach-type-list'),
    path('attaches/', AttachListCreateAPIView.as_view(), name='cbv-attach-list'),
    path('attaches/<int:pk>/', AttachDetailAPIView.as_view(), name='cbv-attach-detail'),
    path('account-attaches/', AccountAttachListCreateAPIView.as_view(), name='cbv-account-attach-list'),
    
    path('account-conditions/', AccountConditionListCreateAPIView.as_view(), name='cbv-account-condition-list'),
    path('account-conditions/<int:pk>/', AccountConditionDetailAPIView.as_view(), name='cbv-account-condition-detail'),
    
    path('account-notes/', AccountNoteListCreateAPIView.as_view(), name='cbv-account-note-list'),
    path('account-notes/<int:pk>/', AccountNoteDetailAPIView.as_view(), name='cbv-account-note-detail'),
    
    # ============================================================
    # Finance
    # ============================================================
    path('payments/', PaymentListCreateAPIView.as_view(), name='cbv-payment-list'),
    path('payments/statistics/', PaymentStatisticsAPIView.as_view(), name='cbv-payment-statistics'),
    path('payments/<int:pk>/', PaymentDetailAPIView.as_view(), name='cbv-payment-detail'),
    
    path('payment-outs/', PaymentOutListCreateAPIView.as_view(), name='cbv-payment-out-list'),
    
    path('deposits/', DepositListCreateAPIView.as_view(), name='cbv-deposit-list'),
    path('deposits/<int:pk>/', DepositDetailAPIView.as_view(), name='cbv-deposit-detail'),
    
    path('withdraws/', WithdrawListCreateAPIView.as_view(), name='cbv-withdraw-list'),
    
    path('bill-buy-types/', BillBuyTypeListCreateAPIView.as_view(), name='cbv-bill-buy-type-list'),
    path('bill-buys/', BillBuyListCreateAPIView.as_view(), name='cbv-bill-buy-list'),
    path('bill-buys/<int:pk>/', BillBuyDetailAPIView.as_view(), name='cbv-bill-buy-detail'),
    
    path('offers/', OfferListCreateAPIView.as_view(), name='cbv-offer-list'),
    path('offers/<int:pk>/', OfferDetailAPIView.as_view(), name='cbv-offer-detail'),
    path('offers/<int:pk>/convert/', OfferConvertAPIView.as_view(), name='cbv-offer-convert'),
    
    path('calls/', CallListCreateAPIView.as_view(), name='cbv-call-list'),
    path('calls/<int:pk>/', CallDetailAPIView.as_view(), name='cbv-call-detail'),
]
