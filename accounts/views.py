from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail

from .models import Person
from .serializers import CustomTokenObtainPairSerializer, PersonSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class ForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'detail': 'البريد الإلكتروني مطلوب'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = Person.objects.get(email=email)
        except Person.DoesNotExist:
            return Response({'detail': 'إذا كان البريد مسجل لدينا، ستصلك رسالة إعادة التعيين'}, status=status.HTTP_200_OK)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_url = f"{request.scheme}://{request.get_host()}/reset-password?uid={uid}&token={token}"

        send_mail(
            subject='إعادة تعيين كلمة المرور - Smart Offer',
            message=f'اضغط على الرابط التالي لإعادة تعيين كلمة المرور:\n{reset_url}',
            from_email=None,
            recipient_list=[email],
            fail_silently=True,
        )
        return Response({'detail': 'إذا كان البريد مسجل لدينا، ستصلك رسالة إعادة التعيين'}, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        uid = request.data.get('uid')
        token = request.data.get('token')
        new_password = request.data.get('new_password')
        if not uid or not token or not new_password:
            return Response({'detail': 'جميع الحقول مطلوبة'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            pk = force_str(urlsafe_base64_decode(uid))
            user = Person.objects.get(pk=pk)
        except (Person.DoesNotExist, ValueError, TypeError, OverflowError):
            return Response({'detail': 'الرابط غير صالح'}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({'detail': 'الرابط غير صالح أو منتهي'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({'detail': 'تم إعادة تعيين كلمة المرور بنجاح'}, status=status.HTTP_200_OK)
