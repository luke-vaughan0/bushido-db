from django.shortcuts import render, redirect, get_object_or_404

from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.views.generic import ListView
from bushido.models import Unit, KiFeat, UnitTrait, Trait, Theme, Event, List, ListUnit, Weapon, UserProfile, WeaponTrait, WeaponSpecial
from django.db.models import Q
from django.contrib import auth
from django.contrib.staticfiles import finders
from .forms import *
from django.contrib.auth.decorators import permission_required
from rest_framework import routers, serializers, viewsets, permissions
from drf_dynamic_fields import DynamicFieldsMixin


class ReadOnlyModelSerializer(serializers.ModelSerializer):
    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)
        for field in fields:
            fields[field].read_only = True
        return fields


class KiFeatSerializer(ReadOnlyModelSerializer):
    class Meta:
        model = KiFeat
        fields = "__all__"


class UnitTraitSerializer(ReadOnlyModelSerializer):
    id = serializers.ReadOnlyField(source='trait.id')
    name = serializers.ReadOnlyField(source='trait.name')
    full = serializers.ReadOnlyField(source='trait.full')
    formatted = serializers.SerializerMethodField()

    class Meta:
        model = UnitTrait
        exclude = ["unit", "trait"]

    def get_formatted(self, obj):
        return obj.trait.full.replace("X", obj.X).replace("Y", obj.Y).replace("Descriptor", obj.descriptor).replace("Bonus", obj.descriptor)


class WeaponTraitSerializer(ReadOnlyModelSerializer):
    id = serializers.ReadOnlyField(source='trait.id')
    name = serializers.ReadOnlyField(source='trait.name')
    full = serializers.ReadOnlyField(source='trait.full')
    formatted = serializers.SerializerMethodField()

    class Meta:
        model = WeaponTrait
        exclude = ["weapon", "trait"]

    def get_formatted(self, obj):
        return obj.trait.full.replace("X", obj.X).replace("Y", obj.Y).replace("Descriptor", obj.descriptor).replace("Bonus", obj.descriptor)


class WeaponSpecialSerializer(ReadOnlyModelSerializer):
    id = serializers.ReadOnlyField(source='special.id')
    name = serializers.ReadOnlyField(source='special.name')

    class Meta:
        model = WeaponSpecial
        exclude = ["weapon", "special"]


class WeaponSerializer(ReadOnlyModelSerializer):
    traits = UnitTraitSerializer(source="weapontraits", many=True)
    specials = WeaponSpecialSerializer(source="weaponspecials", many=True)

    class Meta:
        model = Weapon
        exclude = ["unit", "id"]


# Serializers define the API representation.
class UnitSerializer(DynamicFieldsMixin, ReadOnlyModelSerializer):
    kiFeats = KiFeatSerializer(many=True)
    traits = UnitTraitSerializer(source="unittrait_set", many=True)
    types = serializers.SlugRelatedField(many=True, read_only=True, slug_field="type")
    weapons = WeaponSerializer(source="weapons.all", many=True)

    class Meta:
        model = Unit
        #exclude = ['cost']
        fields = "__all__"


class TraitSerializer(ReadOnlyModelSerializer):
    class Meta:
        model = Trait
        fields = "__all__"


class ModelViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieve model information
    """
    queryset = Unit.objects.prefetch_related('kiFeats', 'traits', 'unittrait_set__trait', 'types',
                                             "weapons__weaponspecials__special", "weapons__weapontraits__trait")
    serializer_class = UnitSerializer
    permission_classes = []
    filterset_fields = "__all__"


class KiFeatViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieve ki feat information
    """
    queryset = KiFeat.objects.all()
    serializer_class = KiFeatSerializer
    permission_classes = []
    filterset_fields = "__all__"


class TraitViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieve ki feat information
    """
    queryset = Trait.objects.all()
    serializer_class = TraitSerializer
    permission_classes = []
    filterset_fields = "__all__"


def index(request):
    return render(request, 'bushido/index.html')


def featDetails(request, featid):
    feat = get_object_or_404(KiFeat, pk=featid)
    units = Unit.objects.filter(kiFeats=feat)
    return render(request, 'bushido/feat_details.html', {'feat': feat, 'units': units})


def unitDetails(request, unitid):
    unit = get_object_or_404(Unit, pk=unitid)
    traits = UnitTrait.objects.filter(unit=unit).prefetch_related("trait")
    weapons = Weapon.objects.filter(unit=unit)
    cardFront = 'bushido/' + unit.faction + "/" + unit.name + " Front.jpg"
    cardBack = 'bushido/' + unit.faction + "/" + unit.name + " Reverse.jpg"
    if finders.find("bushido/unofficial/" + unit.faction + "/" + unit.name + " Front.png"):
        cardFront = "bushido/unofficial/" + unit.faction + "/" + unit.name + " Front.png"
    if finders.find("bushido/unofficial/" + unit.faction + "/" + unit.name + " Reverse.png"):
        cardBack = "bushido/unofficial/" + unit.faction + "/" + unit.name + " Reverse.png"
    if request.user.is_authenticated:
        if not UserProfile.objects.get(user=request.user).useUnofficialCards:
            cardFront = 'bushido/' + unit.faction + "/" + unit.name + " Front.jpg"
            cardBack = 'bushido/' + unit.faction + "/" + unit.name + " Reverse.jpg"


    return render(request, 'bushido/unit_details.html', {'unit': unit, 'cardFront': cardFront, 'cardBack': cardBack, 'traits': traits, 'weapons': weapons})


@permission_required("unit.change_unit")
def editUnit(request, unitid):
    unit = get_object_or_404(Unit, pk=unitid)
    traits = UnitTrait.objects.filter(unit=unit)
    cardFront = 'bushido/' + unit.faction + "/" + unit.name + " Front.jpg"
    cardBack = 'bushido/' + unit.faction + "/" + unit.name + " Reverse.jpg"
    if finders.find("bushido/unofficial/" + unit.faction + "/" + unit.name + " Front.png"):
        cardFront = "bushido/unofficial/" + unit.faction + "/" + unit.name + " Front.png"
    if finders.find("bushido/unofficial/" + unit.faction + "/" + unit.name + " Reverse.png"):
        cardBack = "bushido/unofficial/" + unit.faction + "/" + unit.name + " Reverse.png"
    if request.user.is_authenticated:
        if not UserProfile.objects.get(user=request.user).useUnofficialCards:
            cardFront = 'bushido/' + unit.faction + "/" + unit.name + " Front.jpg"
            cardBack = 'bushido/' + unit.faction + "/" + unit.name + " Reverse.jpg"
    if request.method == "POST":
        unitForm = EditUnit(request.POST, instance=unit)
        featForm = EditUnitFeats(request.POST, instance=unit)
        #if unitForm.is_valid() and featForm.is_valid():
        if unitForm.is_valid():
            unitForm.save()
            #featForm.save()
            return HttpResponseRedirect("./")
    else:
        unitForm = EditUnit(instance=unit)
        featForm = EditUnitFeats(instance=unit)
    return render(request, 'bushido/edit_unit.html', {'unit': unit, 'cardFront': cardFront, 'cardBack': cardBack, 'traits': traits, "form": unitForm, "featForm": featForm})


def themeDetails(request, themeid):
    theme = get_object_or_404(Theme, pk=themeid)
    permitted = eval(theme.validation)
    card = "bushido/themes/" + theme.name + ".jpg"
    return render(request, 'bushido/theme_details.html', {'theme': theme, 'card': card, 'permitted': permitted})


def factionPage(request, faction):
    units = Unit.objects.filter(faction=faction)
    if len(units) == 0:
        return HttpResponseNotFound()
    themes = Theme.objects.filter(faction=faction)
    events = Event.objects.filter(faction=faction)
    return render(request, 'bushido/faction.html', {'faction': faction, 'units': units, 'themes': themes, 'events': events})


def userProfile(request, username):
    user = get_object_or_404(auth.get_user_model(), username=username)
    lists = "" #List.objects.filter(owner=user)
    return render(request, 'bushido/user_profile.html', {'user': user, 'lists': lists})


def userLists(request, username):
    user = get_object_or_404(auth.get_user_model(), username=username)
    lists = List.objects.filter(owner=user)
    return render(request, 'bushido/user_profile.html', {'user': user, 'lists': lists})


def createList(request):
    if request.method == "POST":
        form = CreateListForm(request.POST)
        if form.is_valid():
            newList = form.save(commit=False)
            newList.owner = request.user
            newList.save()
            return HttpResponseRedirect("./"+str(newList.pk))
    else:
        form = CreateListForm()
    return render(request, 'bushido/create_list.html', {'form': form})


def viewList(request, listid):
    unitList = get_object_or_404(List, pk=listid)
    units = ListUnit.objects.filter(list=unitList)
    permitted = eval(unitList.theme.validation)
    return render(request, 'bushido/view_list.html', {'list': unitList, "unit_list": units, "permitted": permitted})


class BushidoUnitListView(ListView):
    model = Unit
    template_name = "bushido/unit_list_view.html"
    context_object_name = 'unit_list'

    def get_queryset(self):
        try:
            data = self.kwargs['units']
        except KeyError:
            data = []
        idList = [int(data[i:i+3], 16) for i in range(0, len(data), 3)]
        modelList = []
        for modelId in idList:
            try:
                modelList.append(Unit.objects.get(id=modelId))
            except Unit.DoesNotExist:
                return []
        return modelList


class BushidoListView(ListView):
    model = Unit
    form_class = FilterForm
    template_name = "bushido/unit_list.html"

    def get_queryset(self):
        fields = self.request.GET.dict()
        sort_fields = fields.pop("sort", "").split(",")
        if sort_fields == [""]:
            sort_fields = []
        queryset = Unit.objects.order_by(*[item[1:] if item.startswith("-") else "-" + item for item in sort_fields])
        queryset = queryset.filter(**fields)
        return queryset



class FeatListView(ListView):
    model = KiFeat
    template_name = "bushido/kifeat_list.html"


class TraitListView(ListView):
    model = Trait
    template_name = "bushido/trait_list.html"