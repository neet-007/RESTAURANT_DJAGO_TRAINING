from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserProfile

class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=255)
    re_password = serializers.CharField(max_length=255)

    def create(self, validated_data):
        return get_user_model().objects.create_user(email=validated_data.get('email'), password=validated_data.get('password'))

    def validate(self, attrs):
        if get_user_model().objects.filter(email=attrs.get('email')).exists():
            raise serializers.ValidationError('email is already taken')
        if len(attrs.get('password')) < 8:
            raise serializers.ValidationError('password must be atleast 8 charectors long')
        if attrs.get('password') != attrs.get('re_password'):
            raise serializers.ValidationError('password and re_passowrd must be equal')
        return super().validate(attrs)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=255)

    def validate(self, attrs):
       if len(attrs.get('password')) < 8:
           raise serializers.ValidationError('password must be atleast 8 charectors long')
       return super().validate(attrs)


class UserSerializer(serializers.ModelSerializer):
    groups = serializers.SerializerMethodField(method_name='get_groups')
    class Meta:
        model = get_user_model()
        fields = ['email', 'groups']

    def get_groups(self, obj):
        return [group.name for group in obj.groups.all()]


class UserProfileSerializer(serializers.ModelSerializer):
    groups = serializers.SerializerMethodField(method_name='get_groups')
    class Meta:
        model = UserProfile
        fields = '__all__'

    def get_groups(self, obj):
        return [group.name for group in obj.user.groups.all()]