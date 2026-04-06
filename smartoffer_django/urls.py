"""
URL configuration for smartoffer_django project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from accounts.views import (
    TeamViewSet, PersonViewSet, BranchAccessViewSet, CustomTokenObtainPairView,
    RoleViewSet, EmployeeRoleViewSet, EmployeePerformanceViewSet,
    ForgotPasswordView, ResetPasswordView
)
from core.views import CompanyViewSet, BranchViewSet, BankViewSet, MasterCategoryViewSet
from students.views import ContactViewSet, StudentViewSet
from courses.views import MasterViewSet, CourseViewSet
from registrations.views import (
    AccountViewSet, AttachTypeViewSet, AttachViewSet,
    AccountAttachViewSet, AccountConditionViewSet, AccountNoteViewSet
)
from finance.views import (
    PaymentViewSet, PaymentOutViewSet, DepositViewSet, WithdrawViewSet,
    BillBuyTypeViewSet, BillBuyViewSet, OfferViewSet, CallViewSet
)

# Create router
router = DefaultRouter()

# Accounts
router.register(r'teams', TeamViewSet, basename='teams')
router.register(r'roles', RoleViewSet, basename='roles')
router.register(r'employee-roles', EmployeeRoleViewSet, basename='employee-roles')
router.register(r'employee-performances', EmployeePerformanceViewSet, basename='employee-performances')
router.register(r'persons', PersonViewSet, basename='persons')
router.register(r'branch-accesses', BranchAccessViewSet, basename='branch-accesses')

# Core
router.register(r'companies', CompanyViewSet, basename='companies')
router.register(r'branches', BranchViewSet, basename='branches')
router.register(r'banks', BankViewSet, basename='banks')
router.register(r'master-categories', MasterCategoryViewSet, basename='master-categories')

# Students
router.register(r'contacts', ContactViewSet, basename='contacts')
router.register(r'students', StudentViewSet, basename='students')

# Courses
router.register(r'masters', MasterViewSet, basename='masters')
router.register(r'courses', CourseViewSet, basename='courses')

# Registrations
router.register(r'accounts', AccountViewSet, basename='accounts')
router.register(r'attach-types', AttachTypeViewSet, basename='attach-types')
router.register(r'attaches', AttachViewSet, basename='attaches')
router.register(r'account-attaches', AccountAttachViewSet, basename='account-attaches')
router.register(r'account-conditions', AccountConditionViewSet, basename='account-conditions')
router.register(r'account-notes', AccountNoteViewSet, basename='account-notes')

# Finance
router.register(r'payments', PaymentViewSet, basename='payments')
router.register(r'payment-outs', PaymentOutViewSet, basename='payment-outs')
router.register(r'deposits', DepositViewSet, basename='deposits')
router.register(r'withdraws', WithdrawViewSet, basename='withdraws')
router.register(r'bill-buy-types', BillBuyTypeViewSet, basename='bill-buy-types')
router.register(r'bill-buys', BillBuyViewSet, basename='bill-buys')
router.register(r'calls', CallViewSet, basename='calls')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('api/auth/reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    path('api/offers/', include('offers.urls')),
    path('api/messaging/', include('messaging.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/reports/', include('reports.urls')),
    # Swagger / OpenAPI
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Serve React frontend for all non-API routes in production
    urlpatterns += [
        re_path(r'^.*$', TemplateView.as_view(template_name='index.html')),
    ]
