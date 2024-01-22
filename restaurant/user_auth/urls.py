from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('managers', views.managers_view)
router.register('user-profile', views.UserProfileView)
urlpatterns = [
    path('register', views.register_view.as_view(), name='register'),
    path('login', views.login_view.as_view(), name='login'),
    path('logout', views.logout_view.as_view(), name='logout'),
    path('get-csrf', views.csrf_token_view.as_view(), name='get-csrf'),
    path('', include(router.urls),)
]