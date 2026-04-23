from django.contrib.auth.models import User
from django.contrib.auth import login
from django.db import transaction
from rest_framework import serializers

from core import models


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Language
        fields = ('code', 'name')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')


class GuideProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.GuideProfile
        fields = ('id',)
        read_only_fields = ('id',)


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Account
        fields = ('id', 'balance')
        read_only_fields = ('id', 'balance')


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Client
        fields = ('user_id', 'user', 'account', 'sex', 'dob', 'phone',
                  'country', 'city', 'about', 'additional',
                  'languages_speak', 'language',
                  'has_driving_license', 'driving_experience',
                  'is_guide', 'age', 'avatar', 'avatar_url', 'full_name',
                  'guide_profile', 'email', 'password',
                  'first_name', 'last_name', 'password_old', 'password_new')
        read_only_fields = ('user_id', 'user', 'full_name', 'avatar_url',
                            'account', 'guide_profile', 'is_guide', 'age')

    user = UserSerializer(read_only=True, required=False)
    account = serializers.SerializerMethodField()
    guide_profile = serializers.SerializerMethodField()
    email = serializers.EmailField(write_only=True, required=False)
    first_name = serializers.CharField(read_only=False, required=False)
    last_name = serializers.CharField(read_only=False, required=False)
    password = serializers.CharField(write_only=True, required=False)
    password_old = serializers.CharField(write_only=True, required=False)
    password_new = serializers.CharField(write_only=True, required=False)

    def get_account(self, obj):
        """
        We restrict showing account
        """
        user = self.context['request'].user
        if user.is_authenticated and user.id == obj.pk:
            serializer = AccountSerializer(obj.account)
            return serializer.data
        else:
            return None

    def get_guide_profile(self, obj):
        """
        We restrict showing guide_profile
        """
        user = self.context['request'].user
        if user.is_authenticated and user.id == obj.pk:
            if obj.guide_profile is not None:
                serializer = GuideProfileSerializer(obj.guide_profile)
                return serializer.data
            else:
                return None
        else:
            return None

    def run_validation(self, initial_data):
        # Declining avatar given as string url
        if isinstance(initial_data.get('avatar'), str):
            del initial_data['avatar']

        return super().run_validation(initial_data)

    @transaction.atomic
    def update(self, instance, validated_data):
        email = validated_data.pop('email', None)
        password_old = validated_data.pop('password_old', '')
        password_new = validated_data.pop('password_new', None)

        # Updating email and password
        if email or password_new:
            if instance.user.check_password(password_old):
                if email:
                    instance.user.email = email
                if password_new:
                    instance.user.set_password(password_new)
            else:
                raise serializers.ValidationError(
                    {'password_old': ["invalid password"]}
                )

        # Updating fields in Client model
        instance_updated = super().update(instance, validated_data)

        # Saving user (because user fields could be changed as well)
        instance.user.save()

        # Logging in again with the new password
        if password_new:
            login(self.context['request'], instance.user)

        return instance_updated


class ClientPictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ClientPicture
        fields = ('client', 'image', 'name', 'image_url')
        read_only_fields = ('image_url',)


class AccountReplenishmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AccountReplenishment
        fields = ('account', 'amount', 'created_at', 'status', 'reason')
        read_only_fields = ('created_at', 'status', 'reason')


class AccountWithdrawalSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AccountWithdrawal
        fields = ('account', 'amount', 'created_at', 'status', 'reason')
        read_only_fields = ('created_at', 'status', 'reason')


class AccountTransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AccountTransfer
        fields = ('account_from', 'account_to', 'trip', 'amount',
                  'created_at', 'performed_at', 'status', 'reason')


class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Chat
        fields = ('id', 'created_at', 'is_group')


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ChatMessage
        fields = ('id', 'created_at', 'chat', 'client', 'message')
        read_only_fields = ('id', 'created_at', 'client')

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['client'] = self.context['request'].user.client
        return super().create(validated_data)


class TripRoutePointSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TripRoutePoint
        fields = ('id', 'trip_route', 'cpp', 'location', 'title', 'description')
        read_only_fields = ('id',)


class TripRoutePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TripRoutePicture
        fields = ('id', 'created_at', 'trip_route', 'image', 'is_poster',
                  'image_url')
        read_only_fields = ('id', 'created_at', 'image_url')


class TripRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TripRoute
        fields = ('id', 'type', 'guide_profile', 'title', 'description', 'type',
                  'country', 'city', 'nop', 'created_at',
                  'trip_route_points', 'trip_route_pictures')
        read_only_fields = ('id', 'created_at', 'guide_profile',
                            'trip_route_points', 'trip_route_pictures')

    guide_profile = GuideProfileSerializer(read_only=True, required=False)
    trip_route_points = TripRoutePointSerializer(many=True, read_only=True,
                                                 required=False)
    trip_route_pictures = TripRoutePictureSerializer(many=True, read_only=True,
                                                     required=False)

    @transaction.atomic
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['guide_profile_id'] = self.context['request'].user.client.guide_profile_id
        return super().create(validated_data)


class TripRouteCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TripRouteComment
        fields = ('id', 'trip_route', 'client', 'text', 'created_at')
        read_only_fields = ('id', 'client', 'created_at')

    @transaction.atomic
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['client_id'] = self.context['request'].user.id
        return super().create(validated_data)


class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Trip
        fields = ('id', 'trip_route', 'created_at', 'is_active',
                  'date_from', 'date_to', 'status', 'reason', 'participants')
        read_only_fields = ('id', 'created_at''status', 'reason', 'participants')

    participants = ClientSerializer(many=True, read_only=True, required=False)


class TripRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TripRequest
        fields = ('id', 'trip', 'created_at', 'client', 'status', 'reason')
        read_only_fields = ('id', 'created_at', 'client', 'status', 'reason')

    @transaction.atomic
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['client_id'] = self.context['request'].user.id
        return super().create(validated_data)


class TripDepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TripRequest
        fields = ('id', 'trip_request', 'created_at', 'amount',
                  'is_funded', 'is_hold')
        read_only_fields = ('id', 'trip_request', 'created_at', 'amount',
                            'is_funded', 'is_hold')
