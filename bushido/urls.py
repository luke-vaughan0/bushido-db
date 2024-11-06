from django.urls import include, path
from . import views
from bushido.views import *
from django.contrib.auth import views as auth_views
from rest_framework import routers, serializers, viewsets

app_name = 'bushido'


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'models', views.ModelViewSet)
router.register(r'kifeats', views.KiFeatViewSet)
router.register(r'traits', views.TraitViewSet)
router.register(r'events', views.EventViewSet)
router.register(r'enhancements', views.EnhancementViewSet)
router.register(r'themes', views.ThemeViewSet)
router.register(r'specials', views.SpecialViewSet)

urlpatterns = [
    path('', views.index, name='index'),
    path('api/', include(router.urls)),
    path('list/<str:listid>/', views.viewList),
    path('list/', views.createList),
    path('search/', views.search, name='search'),
    path('wave/<int:wave_number>/', views.wave_list, name='wave_list'),
    path('wave/latest/', views.wave_list, name='latest_wave'),
    path('info/traits/', TraitListView.as_view(), name='allTraits'),
    path('info/traits/<int:traitid>/', views.trait_details, name='traitDetails'),
    path('info/specials/', SpecialListView.as_view(), name='allSpecials'),
    path('info/states/', StateListView.as_view(), name='allStates'),
    path('info/terms/', TermListView.as_view(), name='allTerms'),

    path('info/actions/', ActionListView.as_view(), name='allActions'),

    path('info/rulings/', RulingListView.as_view(), name='allRulings'),
    path('info/rulings/add/', views.add_ruling, name='add_ruling'),
    path('info/rulings/<int:rulingid>/edit/', views.edit_ruling, name='edit_ruling'),

    path('info/factions/', FactionListView.as_view(), name='allFactions'),
    path('info/factions/<int:factionid>/', views.faction_details, name='factionDetails'),

    path('info/feats/', FeatListView.as_view(), name='allFeats'),
    path('info/feats/add/', views.add_feat, name='add_feat'),
    path('info/feats/<int:featid>/', views.featDetails, name='featDetails'),
    path('info/feats/<int:featid>/edit/', views.editFeat, name='editFeat'),

    path('info/themes/<int:themeid>/', views.themeDetails, name='themeDetails'),
    path('info/themes/<int:themeid>/edit/', views.editTheme, name='editTheme'),

    path('info/models/', BushidoListView.as_view(), name='allModels'),
    path('info/models/add/', views.add_unit, name='add_model'),
    path('info/models/<int:unitid>/', views.unitDetails, name='modelDetails'),
    path('info/models/<int:unitid>/edit/', views.editUnit, name='editModel'),

    path('info/events/<int:eventid>/', views.eventDetails, name='eventDetails'),
    path('info/events/<int:eventid>/edit/', views.editEvent, name='editEvent'),

    path('info/enhancements/<int:enhancementid>/', views.enhancementDetails, name='enhancementDetails'),
    path('info/enhancements/<int:enhancementid>/edit/', views.editEnhancement, name='editEnhancement'),

    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', views.register, name='register'),
    path('accounts/profile/', views.userProfile, name='userProfile'),
    #path('accounts/profile/<str:username>/', views.userProfile, name='userProfile'),
]
