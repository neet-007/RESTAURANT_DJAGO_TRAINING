from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('cart', views.CartView)
router.register('order', views.OrderView)
router.register('table', views.TableView)
urlpatterns = [
    path('', include(router.urls))
]