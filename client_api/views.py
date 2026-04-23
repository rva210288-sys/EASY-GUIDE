from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.db import transaction
from django.conf import settings
from django.db.models import Q
from django.utils import timezone

from rest_framework import viewsets, decorators, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED
from rest_framework.serializers import ValidationError

from core import models
from . import serializers
from . import permissions
from libs.choices import ChoicesViewSet


class LanguageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Language.objects.all()
    serializer_class = serializers.LanguageSerializer
    permission_classes = (AllowAny,)


""" choices viewsets """

class ClientSexesViewSet(ChoicesViewSet):
    choices_obj = models.Client.SEXES


class AccountReplenishmentStatusesViewSet(ChoicesViewSet):
    choices_obj = models.AccountReplenishment.STATUSES


class AccountWithdrawalStatusesViewSet(ChoicesViewSet):
    choices_obj = models.AccountWithdrawal.STATUSES


class AccountTransferStatusesViewSet(ChoicesViewSet):
    choices_obj = models.AccountTransfer.STATUSES


class TripRouteTypesViewSet(ChoicesViewSet):
    choices_obj = models.TripRoute.TYPES


class TripStatusesViewSet(ChoicesViewSet):
    choices_obj = models.Trip.STATUSES


class TripRequestStatusesViewSet(ChoicesViewSet):
    choices_obj = models.TripRequest.STATUSES


""" client """

class ClientViewSet(viewsets.ModelViewSet):
    queryset = models.Client.objects.all()
    serializer_class = serializers.ClientSerializer
    permission_classes = (permissions.ClientPermission,)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)

        # Setting client language into COOKIE
        client = self.get_object()
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, client.language)

        return response

    @decorators.action(detail=False, methods=['post'])
    def login(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                login(request, user)
                return Response({'success': True})
        except User.DoesNotExist:
            pass

        raise ValidationError("wrong email or password")

    @decorators.action(detail=False, methods=['post'])
    def logout(self, request):
        logout(request)
        return Response({'success': True})


class ClientPictureViewSet(viewsets.ModelViewSet):
    queryset = models.ClientPicture.objects.all()
    serializer_class = serializers.ClientPictureSerializer
    permission_classes = (permissions.ClientPicturePermission,)

    def get_queryset(self):
        queryset = models.ClientPicture.objects.all()
        client_id = self.request.query_params.get('client', None)

        if client_id is not None:
            queryset = queryset.filter(client_id=client_id)

        return queryset


class GuideProfileViewSet(viewsets.ModelViewSet):
    queryset = models.GuideProfile.objects.all()
    serializer_class = serializers.GuideProfileSerializer
    permission_classes = (permissions.GuideProfilePermission,)

    @transaction.atomic
    def perform_create(self, serializer):
        super().perform_create(serializer)
        self.request.user.client.guide_profile_id = serializer.instance.id
        self.request.user.client.save()

    @transaction.atomic
    def perform_destroy(self, instance):
        self.request.user.client.guide_profile_id = None
        self.request.user.client.save()
        super().perform_destroy(instance)


""" account """

class AccountViewSet(viewsets.ModelViewSet):
    queryset = models.Account.objects.all()
    serializer_class = serializers.AccountSerializer
    permission_classes = (permissions.AccountPermission,)

    def get_queryset(self):
        return models.Account.objects.filter(client=self.request.user.client)


class AccountReplenishmentViewSet(viewsets.ModelViewSet):
    queryset = models.AccountReplenishment.objects.all()
    serializer_class = serializers.AccountReplenishmentSerializer
    permission_classes = (permissions.AccountReplenishmentPermission,)

    def get_queryset(self):
        return models.AccountReplenishment.objects.filter(
            account=self.request.user.client.account
        )


class AccountWithdrawalViewSet(viewsets.ModelViewSet):
    queryset = models.AccountWithdrawal.objects.all()
    serializer_class = serializers.AccountWithdrawalSerializer
    permission_classes = (permissions.AccountWithdrawalPermission,)

    def get_queryset(self):
        return models.AccountWithdrawal.objects.filter(
            account=self.request.user.client.account
        )


class AccountTransferViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.AccountTransfer.objects.all()
    serializer_class = serializers.AccountTransferSerializer
    permission_classes = (permissions.AccountTransferPermission,)

    def get_queryset(self):
        return models.AccountTransfer.objects.filter(
            Q(account_from=self.request.user.client.account) |
            Q(account_to=self.request.user.client.account)
        )


""" chat """

class ChatViewSet(viewsets.ModelViewSet):
    queryset = models.Chat.objects.all()
    serializer_class = serializers.ChatSerializer
    permission_classes = (permissions.ChatPermission,)

    def get_queryset(self):
        chat_ids = models.ChatToClient.objects.filter(client_id=self.request.user.id).values_list('chat_id', flat=True)
        return models.Chat.objects.filter(id__in=chat_ids)

    @decorators.action(detail=False, methods=['post'])
    def tetatet(self, request):
        client_id = request.data.get('client')

        chat = models.Chat.get_tetatet(self.request.user.id, client_id)

        if chat is None:
            chat = models.Chat.create_tetatet(self.request.user.id, client_id)
            status = HTTP_201_CREATED
        else:
            status = HTTP_200_OK

        serializer = serializers.ChatSerializer(chat)

        return Response(serializer.data, status=status)

    @decorators.action(detail=True, methods=['post'])
    def view(self, request, pk=None):
        client_id = self.request.user.id
        now = timezone.now()
        models.ChatToClient.objects.filter(chat_id=pk, client_id=client_id).update(last_seen=now)
        return Response({'success': True})

    @decorators.action(detail=True, methods=['get'])
    def state(self, request, pk=None):
        data = models.ChatToClient.objects.filter(chat_id=pk).values('client_id', 'last_seen')
        return Response(data)

    @decorators.action(detail=True, methods=['post'])
    def add(self, request, pk=None):
        client_id = request.data.get('client')
        chat = models.Chat.objects.get(id=pk)
        chat.add_client(client_id)
        return Response({'success': True})

    @decorators.action(detail=True, methods=['post'])
    def remove(self, request, pk=None):
        client_id = request.data.get('client')
        chat = models.Chat.objects.get(id=pk)
        chat.remove_client(client_id)
        return Response({'success': True})


class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = models.ChatMessage.objects.all()
    serializer_class = serializers.ChatMessageSerializer
    permission_classes = (permissions.ChatMessagePermission,)

    def get_queryset(self):
        chat_ids = models.ChatToClient.objects.filter(client_id=request.user.id).values_list('chat_id', flat=True)
        return models.ChatMessage.objects.filter(chat_id__in=chat_ids)

    @decorators.action(detail=False, methods=['get'])
    def last(self, request):
        chat_id = request.data.get('chat')
        limit = request.data.get('limit', 12)
        offset = request.data.get('offset', 0)

        messages = models.ChatMessage.objects.filter(chat_id=chat_id).order_by('-created_at')[offset : offset + limit]

        serializer = serializers.ChatMessageSerializer(messages, many=True)

        return Response(serializer.data)


""" trip """

class TripRouteViewSet(viewsets.ModelViewSet):
    queryset = models.TripRoute.objects.all()
    serializer_class = serializers.TripRouteSerializer
    permission_classes = (permissions.TripRoutePermission,)


class TripRoutePointViewSet(viewsets.ModelViewSet):
    queryset = models.TripRoutePoint.objects.all()
    serializer_class = serializers.TripRoutePointSerializer
    permission_classes = (permissions.TripRoutePointPermission,)


class TripRoutePictureViewSet(viewsets.ModelViewSet):
    queryset = models.TripRoutePicture.objects.all()
    serializer_class = serializers.TripRoutePictureSerializer
    permission_classes = (permissions.TripRoutePicturePermission,)


class TripViewSet(viewsets.ModelViewSet):
    queryset = models.Trip.objects.all()
    serializer_class = serializers.TripSerializer
    permission_classes = (permissions.TripPermission,)


class TripRequestViewSet(viewsets.ModelViewSet):
    queryset = models.TripRequest.objects.all()
    serializer_class = serializers.TripRequestSerializer
    permission_classes = (permissions.TripRequestPermission,)

    def get_queryset(self):
        client = self.request.user.client
        return models.TripRequest.objects.filter(
            Q(trip__trip_route__guide_profile_id=client.guide_profile_id) |
            Q(client_id=client.user.id)
        )


class TripDepositViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.TripDeposit.objects.all()
    serializer_class = serializers.TripDepositSerializer
    permission_classes = (permissions.TripDepositPermission,)

    def get_queryset(self):
        client = self.request.user.client
        return models.TripRequest.objects.filter(
            Q(trip_request__trip__trip_route__guide_profile_id=client.guide_profile_id) |
            Q(trip_request__client_id=client.user.id)
        )
