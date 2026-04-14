"""
URLs for Class-Based Views (CBV) - Offers App
"""
from django.urls import path

from .cbv_views import (
    # StudentOffer
    StudentOfferListCreateAPIView,
    StudentOfferDetailAPIView,
    StudentOfferSendAPIView,
    StudentOfferRecipientsAPIView,
    
    # OfferRecipient
    OfferRecipientListCreateAPIView,
    OfferRecipientDetailAPIView,
    
    # OfferNote
    OfferNoteListCreateAPIView,
    OfferNoteDetailAPIView,
)

urlpatterns = [
    # StudentOffer URLs
    path('student-offers/', StudentOfferListCreateAPIView.as_view(), name='studentoffer-list'),
    path('student-offers/<int:pk>/', StudentOfferDetailAPIView.as_view(), name='studentoffer-detail'),
    path('student-offers/<int:pk>/send-offer/', StudentOfferSendAPIView.as_view(), name='studentoffer-send-offer'),
    path('student-offers/<int:pk>/recipients/', StudentOfferRecipientsAPIView.as_view(), name='studentoffer-recipients'),
    
    # OfferRecipient URLs
    path('offer-recipients/', OfferRecipientListCreateAPIView.as_view(), name='offerrecipient-list'),
    path('offer-recipients/<int:pk>/', OfferRecipientDetailAPIView.as_view(), name='offerrecipient-detail'),
    
    # OfferNote URLs
    path('offer-notes/', OfferNoteListCreateAPIView.as_view(), name='offernote-list'),
    path('offer-notes/<int:pk>/', OfferNoteDetailAPIView.as_view(), name='offernote-detail'),
]
