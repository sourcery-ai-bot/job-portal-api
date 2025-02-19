from rest_framework import serializers
from .models import CustomUser, Profile
from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework import status
from rest_framework.response import Response
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    profile_owner = UserProfileSerializer(read_only=True, many=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'first_name', 'last_name', 'phone',
                  'email', 'role', 'profile_owner')


class RegisterSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=68, min_length=2)
    last_name = serializers.CharField(max_length=68, min_length=2)
    password = serializers.CharField(
        max_length=68, min_length=6, write_only=True)
    role = serializers.CharField(max_length=30)

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name',
                  'last_name', 'password', 'phone', 'role']

    def validate(self, attrs):
        email = attrs.get('email', '')
        first_name = attrs.get('first_name', '')
        last_name = attrs.get('last_name', '')
        phone = attrs.get('phone', '')
        role = attrs.get('role', '')

        if not first_name.isalnum():
            raise serializers.ValidationError(
                'Invalid first name format (remove spaces if any)')

        if not last_name.isalnum():
            raise serializers.ValidationError(
                'Invalid last name format (remove spaces if any)')

        return attrs

    def create(self, validate_data):
        return CustomUser.objects.create_user(**validate_data)


class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=555)
    email = serializers.CharField(max_length=256)

    class Meta:
        model = CustomUser
        fields = ['token', 'email']


class ReVerifyEmailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()

    class Meta:
        model = CustomUser
        fields = ['email']


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=3)
    password = serializers.CharField(
        max_length=68, min_length=6, write_only=True)
    first_name = serializers.CharField(max_length=68, read_only=True)
    last_name = serializers.CharField(max_length=68, read_only=True)
    phone = serializers.CharField(max_length=68, read_only=True)
    role = serializers.CharField(max_length=10, read_only=True)

    tokens = serializers.SerializerMethodField()

    profile_owner = UserProfileSerializer(many=True, read_only=True)

    def get_tokens(self, obj):
        user = CustomUser.objects.get(email=obj['email'])

        return {
            'refresh': user.tokens()['refresh'],
            'access': user.tokens()['access']
        }

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name',
                  'phone', 'role', 'password', 'tokens', 'profile_owner']

    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')

        user = auth.authenticate(email=email, password=password)

        if not user:
            raise AuthenticationFailed('Invalid credentials, try again')
        if not user.is_active:
            raise AuthenticationFailed('Account disabled, contact admin')
        if not user.is_verified:
            raise AuthenticationFailed('Email is not verified')
        return {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone': user.phone,
            'role': user.role,
            'tokens': user.tokens,
            'profile_owner': user.profile_owner
        }


class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    class Meta:
        fields = ['email']


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        min_length=6, max_length=68, write_only=True)
    token = serializers.CharField(
        min_length=1, write_only=True)
    uidb64 = serializers.CharField(
        min_length=1, write_only=True)

    class Meta:
        fields = ['password', 'token', 'uidb64']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')

            id = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('The reset link is invalid', 401)

            user.set_password(password)
            user.save()

            return (user)
        except Exception as e:
            raise AuthenticationFailed('The reset link is invalid', 401)
        return super().validate(attrs)


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_messages = {
        'bad_token': ('Token is expired or invalid')
    }

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):

        try:
            RefreshToken(self.token).blacklist()

        except TokenError:
            self.fail('bad_token')


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    # resume = serializers.FileField('resume', required=False)
    # user_company_logo = serializers.FileField(
    #     'user_company_logo', required=False)
    # text_resume = serializers.CharField(max_length=255, required=False)

    class Meta:
        model = Profile
        fields = ['id', 'owner', 'resume', 'user_company_logo', 'text_resume']
