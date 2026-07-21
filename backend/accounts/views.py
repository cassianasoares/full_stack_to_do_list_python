"""Views for the accounts app."""
from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .serializers import (
    LoginSerializer,
    RegisterSerializer,
    UserSerializer,
)


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
    """GET /api/auth/me/ — return the currently authenticated user.

    Authentication is performed by the simplejwt cookie auth class, which
    reads the access token from the `Authorization` header. To accept the
    access token from the HttpOnly cookie, the view wraps the request and
    exposes the cookie value via the `HTTP_AUTHORIZATION` header.
    """

    permission_classes = [IsAuthenticated]

    def initial(self, request, *args, **kwargs):
        access = request.COOKIES.get(settings.ACCESS_TOKEN_COOKIE)
        if access and 'HTTP_AUTHORIZATION' not in request.META:
            request.META['HTTP_AUTHORIZATION'] = f'Bearer {access}'
        super().initial(request, *args, **kwargs)

    def get(self, request):
        return Response(UserSerializer(request.user).data)
