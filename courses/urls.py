from django.urls import path
from .views import (
    course_create_ajax,
    CourseListView, CourseDetailView, CourseUpdateView, CourseDeleteView,
)

urlpatterns = [
    path('courses/', CourseListView.as_view(), name='course-list'),
    path('courses/ajax/create/', course_create_ajax, name='course-create-ajax'),
    path('courses/<int:pk>/', CourseDetailView.as_view(), name='course-detail'),
    path('courses/<int:pk>/update/', CourseUpdateView.as_view(), name='course-update'),
    path('courses/<int:pk>/delete/', CourseDeleteView.as_view(), name='course-delete'),
]
