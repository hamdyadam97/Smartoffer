from django.urls import path
from .views import (
    MasterListView, MasterDetailView, MasterCreateView, MasterUpdateView, MasterDeleteView,
    master_create_ajax, master_info_ajax,
    CourseListView, CourseDetailView, CourseCreateView, CourseUpdateView, CourseDeleteView,
)

urlpatterns = [
    path('masters/', MasterListView.as_view(), name='master-list'),
    path('masters/create/', MasterCreateView.as_view(), name='master-create'),
    path('masters/ajax/create/', master_create_ajax, name='master-create-ajax'),
    path('masters/ajax/info/<int:pk>/', master_info_ajax, name='master-info-ajax'),
    path('masters/<str:slug>/', MasterDetailView.as_view(), name='master-detail'),
    path('masters/<str:slug>/update/', MasterUpdateView.as_view(), name='master-update'),
    path('masters/<str:slug>/delete/', MasterDeleteView.as_view(), name='master-delete'),

    path('courses/', CourseListView.as_view(), name='course-list'),
    path('courses/create/', CourseCreateView.as_view(), name='course-create'),
    path('courses/<int:pk>/', CourseDetailView.as_view(), name='course-detail'),
    path('courses/<int:pk>/update/', CourseUpdateView.as_view(), name='course-update'),
    path('courses/<int:pk>/delete/', CourseDeleteView.as_view(), name='course-delete'),
]
