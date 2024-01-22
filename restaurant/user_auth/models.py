from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin, Group
# Create your models here.

class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            return ValueError('email field is required')

        email = self.normalize_email(email)
        user = self.model(email=email)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, password=None):

        user = self.create_user(email=email, password=password)
        user.is_staff = True
        user.is_admin = True
        user.is_superuser = True
        user.save()
        return user

class User(AbstractBaseUser, PermissionsMixin):
    username = None
    USERNAME_FIELD = "email"
    email = models.EmailField(unique=True)
    groups = models.ManyToManyField(Group)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    REQUIRED_FIELDS = []
    objects = MyUserManager()

class UserProfile(models.Model):
    class IntegerChoices(models.IntegerChoices):
        MANAGER = 1, 'Mangaer'
        DELIVERY_CREW = 2, 'Delivery Crew'
        USER = 3, 'User'
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=125)
    first_name = models.CharField(max_length=125, blank=True, null=True)
    last_name = models.CharField(max_length=125, blank=True, null=True)
    role = models.IntegerField(choices=IntegerChoices.choices, default=IntegerChoices.USER)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
