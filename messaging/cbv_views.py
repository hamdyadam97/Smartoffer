"""
Class-Based Views for Messaging App
API using Django REST Framework CBV instead of ViewSet
"""
from django.shortcuts import get_object_or_404
from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import InternalMessage
from .serializers import InternalMessageSerializer


class IsAuthenticated(permissions.IsAuthenticated):
    pass


# ============================================================
# InternalMessage API (Class-Based Views)
# ============================================================

class InternalMessageListCreateAPIView(generics.ListCreateAPIView):
    """
    GET  /api/messaging/internal-messages/     → List messages
    POST /api/messaging/internal-messages/     → Create message
    """
    queryset = InternalMessage.objects.all()
    serializer_class = InternalMessageSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['sender', 'recipient', 'message_type', 'is_read']
    search_fields = ['subject', 'body']

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)


class InternalMessageDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/messaging/internal-messages/<id>/  → Retrieve message
    PUT    /api/messaging/internal-messages/<id>/  → Update message
    PATCH  /api/messaging/internal-messages/<id>/  → Partial update
    DELETE /api/messaging/internal-messages/<id>/  → Delete message
    """
    queryset = InternalMessage.objects.all()
    serializer_class = InternalMessageSerializer
    permission_classes = [IsAuthenticated]


class InternalMessageMarkAsReadAPIView(APIView):
    """
    POST /api/messaging/internal-messages/<id>/mark-as-read/  → Mark message as read
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        message = get_object_or_404(InternalMessage, pk=pk)
        if message.recipient != request.user:
            return Response({'detail': 'غير مصرح'}, status=status.HTTP_403_FORBIDDEN)
        message.is_read = True
        message.save()
        return Response(InternalMessageSerializer(message).data)


class InternalMessageInboxAPIView(APIView):
    """
    GET /api/messaging/internal-messages/inbox/  → User inbox
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        messages = InternalMessage.objects.filter(recipient=request.user)
        serializer = InternalMessageSerializer(messages, many=True)
        return Response(serializer.data)


class InternalMessageSentAPIView(APIView):
    """
    GET /api/messaging/internal-messages/sent/  → User sent messages
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        messages = InternalMessage.objects.filter(sender=request.user)
        serializer = InternalMessageSerializer(messages, many=True)
        return Response(serializer.data)
