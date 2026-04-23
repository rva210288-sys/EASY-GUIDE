from django.urls import path

from .views import VueComponentView


urlpatterns = [
    path('', VueComponentView.as_view(vue_component='index'), name='index'),

    path('settings', VueComponentView.as_view(vue_component='settings'), name='settings'),
    path('account', VueComponentView.as_view(vue_component='account'), name='account'),
    path('guide', VueComponentView.as_view(vue_component='guide'), name='guide'),

    path('profile/<int:id>', VueComponentView.as_view(vue_component='profile'), name='profile'),
    path('chat', VueComponentView.as_view(vue_component='chat'), name='chat'),
    path('trip-route-search', VueComponentView.as_view(vue_component='trip-route-search'), name='trip-route-search'),
    path('trip-route/<int:id>', VueComponentView.as_view(vue_component='trip-route'), name='trip-route'),
    path('trips-active', VueComponentView.as_view(vue_component='trips-active'), name='trips-active'),
    path('trips-archive', VueComponentView.as_view(vue_component='trips-archive'), name='trips-archive'),

    path('team', VueComponentView.as_view(vue_component='team'), name='team'),
    path('contacts', VueComponentView.as_view(vue_component='contacts'), name='contacts'),
    path('support', VueComponentView.as_view(vue_component='support'), name='support'),
    path('terms-and-conditions', VueComponentView.as_view(vue_component='terms-and-conditions'), name='terms-and-conditions'),
    path('password-restore', VueComponentView.as_view(vue_component='password-restore'), name='password-restore'),
    path('storybook', VueComponentView.as_view(vue_component='storybook'), name='storybook'),
]
