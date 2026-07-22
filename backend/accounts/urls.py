from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LoginView, LogoutView, MeView, RegisterView, TaskViewSet, CategoryViewSet, UserViewSet

app_name = 'accounts'

router = DefaultRouter()
router.register(r'me/tasks', TaskViewSet, basename='me-tasks')
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', MeView.as_view(), name='me'),
    path('', include(router.urls)),
]
