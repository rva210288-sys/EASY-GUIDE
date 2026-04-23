from rest_framework.permissions import BasePermission

from core import models


class ClientPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in ('GET', 'POST'):
            return True
        if request.method in ('PUT', 'PATCH', 'DELETE'):
            return request.user.is_authenticated
        return False

    def has_object_permission(self, request, view, obj):
        if request.method in ('PUT', 'PATCH', 'DELETE'):
            return request.user.id == obj.user.id
        return True


class ClientPicturePermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in ('GET',):
            return True
        if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            return request.user.is_authenticated
        return False

    def has_object_permission(self, request, view, obj):
        if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            return request.user.id == obj.client.user.id
        return True


class GuideProfilePermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user.id == obj.client.user.id


class AccountPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in ('GET',):
            return request.user.is_authenticated
        return False

    def has_object_permission(self, request, view, obj):
        return request.user.id == obj.account.client.user.id


class AccountReplenishmentPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in ('GET', 'POST'):
            return request.user.is_authenticated
        return False

    def has_object_permission(self, request, view, obj):
        return request.user.id == obj.account.client.user.id


class AccountWithdrawalPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in ('GET', 'POST'):
            return request.user.is_authenticated
        return False

    def has_object_permission(self, request, view, obj):
        return request.user.id == obj.account.client.user.id


class AccountTransferPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in ('GET',):
            return request.user.is_authenticated
        return False

    def has_object_permission(self, request, view, obj):
        return request.user.id == obj.account_from.client.user.id or \
               request.user.id == obj.account_to.client.user.id


class ChatPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in ('GET', 'POST'):
            return request.user.is_authenticated
        return False

    def has_object_permission(self, request, view, obj):
        return models.ChatToClient.objects.filter(chat=obj, client_id=request.user.id).exists()


class ChatMessagePermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return models.ChatToClient.objects.filter(chat=obj.chat, client_id=request.user.id).exists()


class TripRoutePermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in ('GET',):
            return True
        if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            return request.user.is_authenticated
        return False

    def has_object_permission(self, request, view, obj):
        if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            return request.user.id == obj.guide_profile.client.user.id
        return True


class TripRoutePointPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in ('GET',):
            return True
        if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            return request.user.is_authenticated
        return False

    def has_object_permission(self, request, view, obj):
        if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            return request.user.id == obj.trip_route.guide_profile.client.user.id
        return True


class TripRoutePicturePermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in ('GET',):
            return True
        if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            return request.user.is_authenticated
        return False

    def has_object_permission(self, request, view, obj):
        if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            return request.user.id == obj.trip_route.guide_profile.client.user.id
        return True


class TripPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in ('GET',):
            return True
        if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            return request.user.is_authenticated
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.id == obj.trip_route.guide_profile.client.user.id:
            return request.method in ('GET', 'POST', 'PUT', 'PATCH', 'DELETE')
        else:
            return request.method in ('GET',) and obj.is_active


class TripRequestPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in ('GET', 'POST'):
            return request.user.is_authenticated
        return False

    def has_object_permission(self, request, view, obj):
        return request.user.id == obj.trip.trip_route.guide_profile.client.user.id or \
               request.user.id == obj.client.user.id


class TripDepositPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in ('GET',):
            return request.user.is_authenticated
        return False

    def has_object_permission(self, request, view, obj):
        return request.user.id == obj.trip_request.trip.trip_route.guide_profile.client.user.id or \
               request.user.id == obj.trip_request.client.user.id
