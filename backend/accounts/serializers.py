from asyncio import Task

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from rest_framework import exceptions, serializers

User = get_user_model()

from .models import Category, User, Task


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'role', 'email')
        read_only_fields = ('id',)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        min_length=8,
    )
    password_match = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        min_length=8,
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'role', 'email', 'password', 'password_match')

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('Email already registered.')
        return value

    def validate(self, data):
        if data['password'] != data['password_match']:
            raise serializers.ValidationError({'password_match': 'The passwords do not match.'})  # nosec B105
        return data

    def create(self, validated_data):
        validated_data.pop('password_match')
        return User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            username=validated_data['username'],
            role=validated_data.get('role'),
        )


class EmailBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            return None
        if user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid credentials.')

        if not user.check_password(password):
            raise exceptions.AuthenticationFailed('Invalid credentials.')

        attrs['user'] = user
        return attrs

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]

class TaskSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = Task
        fields = ["id", "description", "completed", "category"]

class TaskSerializer(serializers.ModelSerializer):
    responsible = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        required=False,
    )
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        required=False,
        allow_null=True,
    )
    completed = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = Task
        fields = ["id", "description", "completed", "category", "responsible"]