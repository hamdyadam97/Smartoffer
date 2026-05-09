from django.urls import path
from .views import (
    StudentListView, StudentDetailView,
    StudentCreateView, StudentUpdateView, StudentDeleteView,
)

urlpatterns = [
    path('students/', StudentListView.as_view(), name='student-list'),
    path('students/<int:pk>/', StudentDetailView.as_view(), name='student-detail'),
    path('students/create/', StudentCreateView.as_view(), name='student-create'),
    path('students/<int:pk>/update/', StudentUpdateView.as_view(), name='student-update'),
    path('students/<int:pk>/delete/', StudentDeleteView.as_view(), name='student-delete'),
]
