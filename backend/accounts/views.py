"""Views for the accounts app."""
from django.conf import settings
from rest_framework import status, viewsets, filters
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from .permissions import IsResponsible

from .serializers import (
    CategorySerializer,
    LoginSerializer,
    RegisterSerializer,
    UserSerializer,
    TaskSerializer,
)
from .models import Category, Task, User


def _set_auth_cookies(response, access_token: str, refresh_token: str) -> None:
    """Attach the JWT tokens to the response as HttpOnly cookies.

    `Secure` is enabled outside DEBUG so the dev server (http://localhost)
    keeps working. In production (https) the cookie is only sent over TLS.
    """
    common = {
        "httponly": True,
        "secure": settings.JWT_COOKIE_SECURE,
        "samesite": settings.JWT_COOKIE_SAMESITE,
        "path": settings.JWT_COOKIE_PATH,
    }
    response.set_cookie(
        settings.ACCESS_TOKEN_COOKIE,
        access_token,
        max_age=settings.ACCESS_TOKEN_COOKIE_MAX_AGE,
        **common,
    )
    response.set_cookie(
        settings.REFRESH_TOKEN_COOKIE,
        refresh_token,
        max_age=settings.REFRESH_TOKEN_COOKIE_MAX_AGE,
        **common,
    )


def _clear_auth_cookies(response) -> None:
    for name in (settings.ACCESS_TOKEN_COOKIE, settings.REFRESH_TOKEN_COOKIE):
        response.delete_cookie(
            name,
            path=settings.JWT_COOKIE_PATH,
            samesite=settings.JWT_COOKIE_SAMESITE,
        )

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Allows listing and retrieving details of existing users.
    Read-only (list/retrieve).
    """
    queryset = User.objects.all().order_by("id")
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

class RegisterView(APIView):
    """POST /api/auth/register/ — create new user."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """POST /api/auth/login/ — authenticate and set JWT cookies."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        token_serializer = TokenObtainPairSerializer()
        tokens = token_serializer.get_token(user)
        access_token = str(tokens.access_token)
        refresh_token = str(tokens)

        response = Response(UserSerializer(user).data, status=status.HTTP_200_OK)
        _set_auth_cookies(response, access_token, refresh_token)
        return response


class LogoutView(APIView):
    """POST /api/auth/logout/ — clear JWT cookies."""

    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get(settings.REFRESH_TOKEN_COOKIE)
        if refresh_token:
            try:
                RefreshToken(refresh_token).blacklist()
            except TokenError:
                # Token already invalid/expired — still clear the cookies.
                pass
        response = Response(status=status.HTTP_204_NO_CONTENT)
        _clear_auth_cookies(response)
        return response


class MeView(APIView):
    """GET /api/auth/me/ — return the currently authenticated user."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_data = UserSerializer(request.user).data

        tasks_qs = Task.objects.filter(responsible=request.user)

        category_id = request.query_params.get("category")
        if category_id:
            tasks_qs = tasks_qs.filter(category_id=category_id)

        completed = request.query_params.get("completed")
        if completed is not None:
            tasks_qs = tasks_qs.filter(completed=completed.lower() in ["true", "1"])

        paginator = PageNumberPagination()
        paginator.page_size = 10
        paginated_tasks = paginator.paginate_queryset(tasks_qs, request)

        tasks_data = TaskSerializer(paginated_tasks, many=True).data

        return paginator.get_paginated_response({
            "user": user_data,
            "tasks": tasks_data,
        })

class TaskViewSet(viewsets.ModelViewSet):
    """ViewSet for managing tasks."""
    queryset = Task.objects.all().order_by("id")
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsResponsible]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["category", "completed"]
    search_fields = ["description"]

    def get_queryset(self):
        return Task.objects.filter(responsible=self.request.user)

    def perform_create(self, serializer):
        declared = list(serializer.validated_data.get("responsible", []))
        merged = [self.request.user] + [u for u in declared if u != self.request.user]
        seen = set()
        unique = []
        for u in merged:
            if u.pk not in seen:
                seen.add(u.pk)
                unique.append(u)

        category = serializer.validated_data.get("category")
        if category is None:
            category, _ = Category.objects.get_or_create(name="Geral")

        serializer.save(responsible=unique, category=category)

class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for managing categories."""
    queryset = Category.objects.all().order_by("id")
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]