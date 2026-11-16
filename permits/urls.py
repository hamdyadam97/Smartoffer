from django.urls import path

from . import views

urlpatterns = [
    path('permits/', views.PermitListView.as_view(), name='permit-list'),
    path('permits/create/', views.PermitCreateView.as_view(), name='permit-create'),
    path('permits/templates/', views.PermitTemplateListView.as_view(), name='permittemplate-list'),
    path('permits/templates/create/', views.PermitTemplateCreateView.as_view(), name='permittemplate-create'),
    path('permits/templates/<int:pk>/update/', views.PermitTemplateUpdateView.as_view(), name='permittemplate-update'),
    path('permits/templates/<int:pk>/preview/', views.permit_template_preview, name='permittemplate-preview'),
    path('permits/<int:pk>/', views.PermitDetailView.as_view(), name='permit-detail'),
    path('permits/<int:pk>/pdf/', views.permit_pdf, name='permit-pdf'),
    path('permits/<int:pk>/send/', views.permit_send, name='permit-send'),
    path('permits/<int:pk>/cancel/', views.permit_cancel, name='permit-cancel'),
]
