from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()

router.register('client-sexes', views.ClientSexesViewSet, basename='client-sexes')
router.register('account-replenishment-statuses', views.AccountReplenishmentStatusesViewSet, basename='account-replenishment-statuses')
router.register('account-withdrawal-statuses', views.AccountWithdrawalStatusesViewSet, basename='account-withdrawal-statuses')
router.register('account-transfer-statuses', views.AccountTransferStatusesViewSet, basename='account-transfer-statuses')
router.register('trip-route-types', views.TripRouteTypesViewSet, basename='trip-route-types')
router.register('trip-statuses', views.TripStatusesViewSet, basename='trip-statuses')
router.register('trip-request-statuses', views.TripRequestStatusesViewSet, basename='trip-request-statuses')

router.register('languages', views.LanguageViewSet)

router.register('clients', views.ClientViewSet)
router.register('client-pictures', views.ClientPictureViewSet)
router.register('guide-profiles', views.GuideProfileViewSet)

router.register('accounts', views.AccountViewSet)
router.register('account-replenishments', views.AccountReplenishmentViewSet)
router.register('account-withdrawals', views.AccountWithdrawalViewSet)
router.register('account-transfers', views.AccountTransferViewSet)

router.register('chats', views.ChatViewSet)
router.register('chat-messages', views.ChatMessageViewSet)

router.register('trip-routes', views.TripRouteViewSet)
router.register('trip-route-points', views.TripRoutePointViewSet)
router.register('trip-route-pictures', views.TripRoutePictureViewSet)
router.register('trips', views.TripViewSet)
router.register('trip-requests', views.TripRequestViewSet)
router.register('trip-deposits', views.TripDepositViewSet)

urlpatterns = router.urls
