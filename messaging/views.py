from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter

from .models import InternalMessage
from .serializers import InternalMessageSerializer


class IsAuthenticated(permissions.IsAuthenticated):
    pass


class InternalMessageViewSet(viewsets.ModelViewSet):
    queryset = InternalMessage.objects.all()
    serializer_class = InternalMessageSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['sender', 'recipient', 'message_type', 'is_read']
    search_fields = ['subject', 'body']

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        message = self.get_object()
        if message.recipient != request.user:
            return Response({'detail': 'غير مصرح'}, status=status.HTTP_403_FORBIDDEN)
        message.is_read = True
        message.save()
        return Response(self.get_serializer(message).data)

    @action(detail=False, methods=['get'])
    def inbox(self, request):
        messages = InternalMessage.objects.filter(recipient=request.user)
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def sent(self, request):
        messages = InternalMessage.objects.filter(sender=request.user)
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)


router = DefaultRouter()
router.register(r'internal-messages', InternalMessageViewSet, basename='internal-messages')
