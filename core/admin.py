from django.contrib import admin

from . import models


""" client """

@admin.register(models.Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'first_name', 'last_name',
                    'account', 'is_guide',
                    'sex', 'dob', 'phone', 'language', 'country', 'city',
                    'has_driving_license', 'driving_experience')

    def email(self, obj):
        return obj.user.email

    def first_name(self, obj):
        return obj.user.first_name

    def last_name(self, obj):
        return obj.user.last_name


@admin.register(models.ClientPicture)
class ClientPictureAdmin(admin.ModelAdmin):
    pass


@admin.register(models.GuideProfile)
class GuideProfileAdmin(admin.ModelAdmin):
    pass


""" trip """

@admin.register(models.TripRoute)
class TripRouteAdmin(admin.ModelAdmin):
    pass


@admin.register(models.TripRoutePoint)
class TripRoutePointAdmin(admin.ModelAdmin):
    pass


@admin.register(models.TripRoutePicture)
class TripRoutePictureAdmin(admin.ModelAdmin):
    pass


@admin.register(models.TripRouteComment)
class TripRouteCommentAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Trip)
class TripAdmin(admin.ModelAdmin):
    pass


@admin.register(models.TripRequest)
class TripRequestAdmin(admin.ModelAdmin):
    pass


@admin.register(models.TripDeposit)
class TripDepositAdmin(admin.ModelAdmin):
    pass


""" account """

@admin.register(models.Account)
class AccountAdmin(admin.ModelAdmin):
    pass


@admin.register(models.AccountReplenishment)
class AccountReplenishmentAdmin(admin.ModelAdmin):
    pass


@admin.register(models.AccountWithdrawal)
class AccountWithdrawalAdmin(admin.ModelAdmin):
    pass


@admin.register(models.AccountTransfer)
class AccountTransferAdmin(admin.ModelAdmin):
    pass


""" chat """

@admin.register(models.Chat)
class ChatAdmin(admin.ModelAdmin):
    pass


@admin.register(models.ChatToClient)
class ChatToClientAdmin(admin.ModelAdmin):
    pass


@admin.register(models.ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    pass
