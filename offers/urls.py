from django.urls import path
from . import views

urlpatterns = [
    # StudentOffer
    path('student-offers/', views.StudentOfferListView.as_view(), name='studentoffer-list'),
    path('student-offers/<int:pk>/', views.StudentOfferDetailView.as_view(), name='studentoffer-detail'),
    path('student-offers/create/', views.StudentOfferCreateView.as_view(), name='studentoffer-create'),
    path('student-offers/<int:pk>/update/', views.StudentOfferUpdateView.as_view(), name='studentoffer-update'),
    path('student-offers/<int:pk>/delete/', views.StudentOfferDeleteView.as_view(), name='studentoffer-delete'),

    # OfferRecipient
    path('offer-recipients/', views.OfferRecipientListView.as_view(), name='offerrecipient-list'),
    path('offer-recipients/<int:pk>/', views.OfferRecipientDetailView.as_view(), name='offerrecipient-detail'),
    path('offer-recipients/create/', views.OfferRecipientCreateView.as_view(), name='offerrecipient-create'),
    path('offer-recipients/<int:pk>/update/', views.OfferRecipientUpdateView.as_view(), name='offerrecipient-update'),
    path('offer-recipients/<int:pk>/delete/', views.OfferRecipientDeleteView.as_view(), name='offerrecipient-delete'),

    # OfferNote
    path('offer-notes/', views.OfferNoteListView.as_view(), name='offernote-list'),
    path('offer-notes/<int:pk>/', views.OfferNoteDetailView.as_view(), name='offernote-detail'),
    path('offer-notes/create/', views.OfferNoteCreateView.as_view(), name='offernote-create'),
    path('offer-notes/<int:pk>/update/', views.OfferNoteUpdateView.as_view(), name='offernote-update'),
    path('offer-notes/<int:pk>/delete/', views.OfferNoteDeleteView.as_view(), name='offernote-delete'),
]
