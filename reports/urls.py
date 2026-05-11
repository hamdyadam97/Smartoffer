from django.urls import path
from . import views

urlpatterns = [
    # StudentOffer
    path('reports/', views.ReportSnapshotListView.as_view(), name='reportsnapshot-list'),
    path('reports/<str:slug>/', views.ReportSnapshotDetailView.as_view(), name='reportsnapshot-detail'),
    path('reports/create/', views.ReportSnapshotCreateView.as_view(), name='reportsnapshot-create'),
    path('reports/<str:slug>/update/', views.ReportSnapshotUpdateView.as_view(), name='reportsnapshot-update'),
    path('reports/<str:slug>/delete/', views.ReportSnapshotDeleteView.as_view(), name='reportsnapshot-delete'),
    path('reports/ajax/create/', views.reportsnapshot_create_ajax, name='reportsnapshot-create-ajax'),
    path('reports/ajax/<int:pk>/update/', views.reportsnapshot_update_ajax, name='reportsnapshot-update-ajax'),
]
