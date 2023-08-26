from django.urls import include, path
from . import views
from bushido.views import BushidoListView, BushidoUnitListView, FeatListView, TraitListView, FactionListView, SpecialListView
from django.contrib.auth import views as auth_views
from rest_framework import routers, serializers, viewsets

app_name = 'bushido'


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'models', views.ModelViewSet)
router.register(r'kifeats', views.KiFeatViewSet)
router.register(r'traits', views.TraitViewSet)

urlpatterns = [
    path('', views.index, name='index'),
    path('api/', include(router.urls)),
    path('list/<str:listid>/', views.viewList),
    path('list/', views.createList),
    path('info/models/', BushidoListView.as_view(), name='allModels'),
    path('search/', views.search, name='search'),
    path('info/feats/', FeatListView.as_view(), name='allFeats'),
    path('info/traits/', TraitListView.as_view(), name='allTraits'),
    path('info/factions/', FactionListView.as_view(), name='allFactions'),
    path('info/specials/', SpecialListView.as_view(), name='allSpecials'),
    path('info/feats/<int:featid>/', views.featDetails, name='featDetails'),
    path('info/themes/<int:themeid>/', views.themeDetails, name='themeDetails'),
    path('info/models/<int:unitid>/', views.unitDetails, name='modelDetails'),
    path('info/models/<int:unitid>/edit/', views.editUnit, name='editModel'),
    path('info/factions/<int:factionid>/', views.factionPage, name='factionDetails'),
    path('info/events/<int:eventid>/', views.eventDetails, name='eventDetails'),
    path('info/enhancements/<int:enhancementid>/', views.enhancementDetails, name='enhancementDetails'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', views.register, name='register'),
    path('accounts/profile/', views.userProfile, name='userProfile'),
    #path('accounts/profile/<str:username>/', views.userProfile, name='userProfile'),
]
