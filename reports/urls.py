from django.urls import path
from . import views

urlpatterns = [
    path('reports/', views.ReportSnapshotListView.as_view(), name='reportsnapshot-list'),
    path('reports/<int:pk>/', views.ReportSnapshotDetailView.as_view(), name='reportsnapshot-detail'),
    path('reports/create/', views.ReportSnapshotCreateView.as_view(), name='reportsnapshot-create'),
    path('reports/<int:pk>/update/', views.ReportSnapshotUpdateView.as_view(), name='reportsnapshot-update'),
    path('reports/<int:pk>/delete/', views.ReportSnapshotDeleteView.as_view(), name='reportsnapshot-delete'),
]
