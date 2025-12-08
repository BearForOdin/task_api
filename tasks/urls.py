from django.urls import path
from .views import UserRegisterView
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [
    path('auth/register/', UserRegisterView.as_view(), name='auth-register'),
] + router.urls
