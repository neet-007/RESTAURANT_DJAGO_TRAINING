from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.models import Group
from django.views.decorators.csrf import csrf_exempt, csrf_protect, ensure_csrf_cookie
from django.utils.decorators import method_decorator
from rest_framework import generics, status
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, UserProfileSerializer
from .models import UserProfile
import logging

logger = logging.getLogger(__name__)
# Create your views here.
@method_decorator(csrf_protect, name='dispatch')
class register_view(APIView):
    def post(self, request):
        serialized_data = RegisterSerializer(data=self.request.data)
        if serialized_data.is_valid():
            serialized_data.save()
            return Response({'success':f'user with email {serialized_data.validated_data.get("email")} successfully created'}, status=status.HTTP_201_CREATED)
        return Response({'error':serialized_data.errors.values()}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_protect, name='dispatch')
class login_view(APIView):
    def post(self, request):
        serialized_data = LoginSerializer(data=self.request.data, context={'request':request})

        if serialized_data.is_valid():
            user = authenticate(**serialized_data.validated_data)
            if user is not None:
                login(self.request, user)
                return Response({'success':'login successful'}, status=status.HTTP_200_OK)

            return Response({'error':'no user with provided credentials'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'error':serialized_data.errors.values()}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class logout_view(APIView):
    def post(self, request):
        logout(request)
        return Response({'success':'logout successfull'}, status=status.HTTP_200_OK)


class managers_view(ModelViewSet):
    queryset = get_user_model().objects.filter(groups__name__iexact='manager')
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        user_model = get_user_model()
        email = self.request.data.get('email')

        if email and user_model.objects.filter(email=email).exists():
            user = user_model.objects.get(email=email)
            Group.objects.get(name__iexact='manager').user_set.add(user)
            user.userprofile.role = 1
            user.save()
            logger.info('user with pk %d was added as a manager by user with pk %d',user.pk, self.request.user.pk)
            return Response({'success':f'user {user.email} is now a manager'}, status=status.HTTP_200_OK)

        return Response({'error':'email not provided or no user with this credintails'}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        group = Group.objects.get(name__iexact='manager')

        if group.user_set.filter(pk=user.pk).exists():
            group.user_set.remove(user)
            logger.info('user with pk %d was removed from managers by user with pk %d',user.pk, self.request.user.pk)
            return Response({'success':f'user {user.email} removed from managers'}, status=status.HTTP_200_OK)

        return Response({'error':'user is not a manager'})


class UserProfileView(ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        context['method'] = self.request.method
        return context


@method_decorator(ensure_csrf_cookie, name='dispatch')
class csrf_token_view(APIView):
    def get(self, request):
        return Response({'success':'csrf token generated'}, status=status.HTTP_201_CREATED)