from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
router = DefaultRouter()
router.register('delivery-crew', views.DeliveryCrewView)
router.register('category', views.CategoryView)
router.register('menu-item', views.MenuItemView)
router.register('delivery-crew-to-order', views.DeliveryCrewToOrder)
urlpatterns = [
    path('', include(router.urls)),
]