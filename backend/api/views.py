from django.db.models import Prefetch, Count, Q
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import *
from .models import *
from addons.permissions import *
from tasks import *

# Create your views here.


class AuthViewSet(viewsets.GenericViewSet):
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()

    def get_permissions(self):
        if self.action in ['login', 'register']:
            return [AllowAny()]
        return super().get_permissions()

    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        return TokenObtainPairView.as_view()(request._request)

    @action(detail=False, methods=['post'], url_path='refresh')
    def refresh(self, request):
        return TokenRefreshView.as_view()(request._request)

    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request, *args, **kwargs):        
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        response_data = {
            'message': 'Пользователь успешно создан',
            'username': user.username,
            'email': user.email,
            'phone': user.phone
        }

        return Response(response_data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='user')
    def user(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(detail=False, methods=['delete'], url_path='delete')
    def delete(self, request):
        request.user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'], url_path='change-password')
    def change_password(self, request):
        user = request.user
        serializer = UserChangePasswordSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(serializer.validated_data['password']):
            return Response(
                {"password": "Неверный текущий пароль"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response(
            {"message": "Пароль успешно изменен"},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['patch'], url_path='update')
    def patch_user(self, request):
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['delete'], url_path='avatar')
    def delete_avatar(self, request):
        user = request.user

        if not user.avatar:
            return Response(
                {"detail": "Аватар отсутствует"},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            # Удаляем файл с диска
            if os.path.isfile(user.avatar.path):
                os.remove(user.avatar.path)

            # Очищаем поле в базе данных
            user.avatar = None
            user.save()

            return Response(
                {"detail": "Аватар успешно удален"},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"detail": f"Ошибка при удалении аватара: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def list(self, request, *args, **kwargs):
        if not request.user.is_staff and not request.user.is_superuser:
            return Response(status=status.HTTP_404_NOT_FOUND)
        instance = self.get_queryset()
        serializer = self.get_serializer(instance, many=True)
        return Response(serializer.data)


class GroupViewSet(viewsets.GenericViewSet):
    @action(detail=True, methods=['get'], url_path='group-list')
    def group_list(self, request, pk=None):
        group = get_object_or_404(
            Group.objects.filter(owner=request.user),
            pk=pk
        )
        characters = GroupCharacters.objects.filter(group=group)
        serializer = GroupCharacterSerializer(characters, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='invite')
    def invite(self, request, pk=None):
        invitation = get_object_or_404(
            Group.objects.filter(owner=request.user),
            pk=pk
        ).invitation
        email = request.data.get('email')
        if not email:
            return Response(
                {'error': 'Email обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        send_invitation_email.delay(email, invitation)
        return Response(status=status.HTTP_200_OK)

    def list(self, request):
        groups = Group.objects.filter(owner=request.user)
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data)
