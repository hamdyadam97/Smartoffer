"""
URLs for Class-Based Views (CBV) - Messaging App
"""
from django.urls import path

from .cbv_views import (
    InternalMessageListCreateAPIView,
    InternalMessageDetailAPIView,
    InternalMessageMarkAsReadAPIView,
    InternalMessageInboxAPIView,
    InternalMessageSentAPIView,
)

urlpatterns = [
    path('internal-messages/', InternalMessageListCreateAPIView.as_view(), name='internalmessage-list'),
    path('internal-messages/inbox/', InternalMessageInboxAPIView.as_view(), name='internalmessage-inbox'),
    path('internal-messages/sent/', InternalMessageSentAPIView.as_view(), name='internalmessage-sent'),
    path('internal-messages/<int:pk>/', InternalMessageDetailAPIView.as_view(), name='internalmessage-detail'),
    path('internal-messages/<int:pk>/mark-as-read/', InternalMessageMarkAsReadAPIView.as_view(), name='internalmessage-mark-as-read'),
]
