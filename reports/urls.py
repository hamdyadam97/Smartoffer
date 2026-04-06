from django.urls import path
from .views import (
    DashboardStatsView, FinancialReportView,
    ExportExcelView, ExportPDFView
)

urlpatterns = [
    path('dashboard-stats/', DashboardStatsView.as_view(), name='dashboard_stats'),
    path('financial/', FinancialReportView.as_view(), name='financial_report'),
    path('export/excel/<str:report_type>/', ExportExcelView.as_view(), name='export_excel'),
    path('export/pdf/<str:report_type>/', ExportPDFView.as_view(), name='export_pdf'),
]
