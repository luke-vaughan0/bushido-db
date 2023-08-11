from django.urls import include, path
from . import views
from bushido.views import BushidoListView, BushidoUnitListView, FeatListView, TraitListView, FactionListView
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
    path('all/', BushidoListView.as_view(), name='allModels'),
    path('search/', views.search, name='search'),
    path('allfeats/', FeatListView.as_view(), name='allFeats'),
    path('alltraits/', TraitListView.as_view(), name='allTraits'),
    path('allfactions/', FactionListView.as_view(), name='allFactions'),
    path('info/feat/<int:featid>/', views.featDetails, name='featDetails'),
    path('info/theme/<int:themeid>/', views.themeDetails, name='featDetails'),
    path('info/model/<int:unitid>/', views.unitDetails, name='unitDetails'),
    path('info/model/<int:unitid>/edit', views.editUnit, name='editUnit'),
    path('info/faction/<int:factionid>/', views.factionPage, name='factionDetails'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/profile/<str:username>/', views.userProfile, name='userProfile'),
]
