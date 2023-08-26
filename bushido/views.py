from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.views.generic import ListView
from bushido.models import Unit, KiFeat, UnitTrait, Trait, Theme, Event, List, ListUnit, Weapon, UserProfile,\
    WeaponTrait, WeaponSpecial, Faction, Special, Enhancement
from django.db.models import Q, Prefetch
from django.db import models
from django.contrib import auth, messages
from django.contrib.staticfiles import finders
from .forms import *
from django.contrib.auth.decorators import permission_required
from django.contrib.auth import login
from rest_framework import routers, serializers, viewsets, permissions
from drf_dynamic_fields import DynamicFieldsMixin
import jellyfish


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
    faction = serializers.ReadOnlyField(source='faction.name')
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
                                             "weapons__weaponspecials__special", "weapons__weapontraits__trait").select_related('faction')
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


def register(request):
    form = RegisterForm()

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/bushido/')
        else:
            return render(request, 'registration/register.html', {'registerForm': form})
    return render(request, 'registration/register.html', {"registerForm": form})


def search(request):
    search_query = request.GET["search"]
    search_models = [Unit, KiFeat, Trait, Theme, Special, Faction, Event, Enhancement]
    search_results = []
    for model in search_models:
        fields = [x for x in model._meta.fields if isinstance(x, models.CharField)]
        search_queries = [Q(**{x.name + "__icontains" : search_query}) for x in fields]
        q_object = Q()
        for query in search_queries:
            q_object = q_object | query

        results = model.objects.filter(q_object)
        if hasattr(model, "faction"):
            results = results.select_related("faction")
        search_results.append(results)
    fullResult = [x for x in search_results if x]
    result = [item for model in fullResult for item in model]
    rankedResults = []
    for item in result:
        rankedResults.append([item, jellyfish.jaro_winkler_similarity(item.name.lower(), search_query.lower())])
    rankedResults = sorted(rankedResults, key=lambda x: x[1], reverse=True)
    result = [x[0] for x in rankedResults]
    if len(result) == 1:
        if result[0].name.lower() == search_query.lower():
            model = result[0]
            classNames = {
                "Unit": "Model",
                "KiFeat": "Feat"
            }
            return redirect('/bushido/info/{}s/{}'.format(
                classNames.get(model.__class__.__name__, model.__class__.__name__).lower(), model.pk))
    return render(request, 'bushido/search.html', {"search_results": result})


def featDetails(request, featid):
    feat = get_object_or_404(KiFeat, pk=featid)
    return render(request, 'bushido/feat_details.html', {'feat': feat})


def unitDetails(request, unitid):
    unit = get_object_or_404(
        Unit.objects.prefetch_related(
            Prefetch('unittrait_set', queryset=UnitTrait.objects.select_related('trait')),
            Prefetch('weapons', queryset=Weapon.objects.prefetch_related('weaponspecials__special', 'weapontraits__trait')),

        ),
        pk=unitid
    )
    cardUnits = Unit.objects.filter(cardName=unit.cardName)
    cardFront = 'bushido/' + unit.faction.shortName + "/" + unit.cardName + " Front.jpg"
    cardBack = 'bushido/' + unit.faction.shortName + "/" + unit.cardName + " Reverse.jpg"
    if finders.find("bushido/unofficial/" + unit.faction.shortName + "/" + unit.cardName + " Front.png"):
        cardFront = "bushido/unofficial/" + unit.faction.shortName + "/" + unit.cardName + " Front.png"
    if finders.find("bushido/unofficial/" + unit.faction.shortName + "/" + unit.cardName + " Reverse.png"):
        cardBack = "bushido/unofficial/" + unit.faction.shortName + "/" + unit.cardName + " Reverse.png"
    if request.user.is_authenticated:
        if not request.user.userprofile.use_unofficial_cards:
            cardFront = 'bushido/' + unit.faction.shortName + "/" + unit.cardName + " Front.jpg"
            cardBack = 'bushido/' + unit.faction.shortName + "/" + unit.cardName + " Reverse.jpg"

    return render(request, 'bushido/unit_details.html',
                  {'unit': unit, 'cardUnits': cardUnits, 'cardFront': cardFront, 'cardBack': cardBack})


@permission_required("bushido.change_unit")
def editUnit(request, unitid):
    unit = get_object_or_404(Unit, pk=unitid)
    cardFront = 'bushido/' + unit.faction.shortName + "/" + unit.cardName + " Front.jpg"
    cardBack = 'bushido/' + unit.faction.shortName + "/" + unit.cardName + " Reverse.jpg"
    if finders.find("bushido/unofficial/" + unit.faction.shortName + "/" + unit.cardName + " Front.png"):
        cardFront = "bushido/unofficial/" + unit.faction.shortName + "/" + unit.cardName + " Front.png"
    if finders.find("bushido/unofficial/" + unit.faction.shortName + "/" + unit.cardName + " Reverse.png"):
        cardBack = "bushido/unofficial/" + unit.faction.shortName + "/" + unit.cardName + " Reverse.png"
    if request.user.is_authenticated:
        if not request.user.userprofile.use_unofficial_cards:
            cardFront = 'bushido/' + unit.faction.shortName + "/" + unit.cardName + " Front.jpg"
            cardBack = 'bushido/' + unit.faction.shortName + "/" + unit.cardName + " Reverse.jpg"

    if request.method == "POST":
        unitForm = EditUnit(request.POST, instance=unit)
        typeForm = TypeFormSet(request.POST, instance=unit, prefix="types")
        traitForm = TraitFormSet(request.POST, instance=unit, prefix="traits")
        weapon_formset = WeaponFormSet(request.POST, instance=unit, queryset=Weapon.objects.filter(unit=unit))
        if unitForm.is_valid() and weapon_formset.is_valid() and traitForm.is_valid() and typeForm.is_valid():
            unitForm.save()
            weapon_formset.save()
            traitForm.save()
            typeForm.save()
            return redirect(reverse('bushido:modelDetails', kwargs={'unitid': unitid}))

    else:
        unitForm = EditUnit(instance=unit)
        typeForm = TypeFormSet(instance=unit, prefix="types")
        traitForm = TraitFormSet(instance=unit, prefix="traits")
        weapon_formset = WeaponFormSet(instance=unit, queryset=Weapon.objects.filter(unit=unit), prefix="weapons")
    return render(request, 'bushido/edit_unit.html',
                  {'unit': unit, 'cardFront': cardFront, 'cardBack': cardBack,
                   "form": unitForm, 'weapon_formset': weapon_formset, 'trait_form': traitForm, 'type_form': typeForm})


def themeDetails(request, themeid):
    theme = get_object_or_404(Theme, pk=themeid)
    permitted = eval(theme.validation)
    card = "bushido/themes/" + theme.name + ".jpg"
    return render(request, 'bushido/theme_details.html', {'theme': theme, 'card': card, 'permitted': permitted})


def eventDetails(request, eventid):
    event = get_object_or_404(Event, pk=eventid)
    card = "bushido/themes/" + event.name + ".jpg"
    return render(request, 'bushido/event_details.html', {'event': event, 'card': card})


def enhancementDetails(request, enhancementid):
    enhancement = get_object_or_404(Enhancement, pk=enhancementid)
    card = "bushido/themes/" + enhancement.name + ".jpg"
    return render(request, 'bushido/enhancement_details.html', {'enhancement': enhancement, 'card': card})


def factionPage(request, factionid):
    faction = get_object_or_404(Faction, pk=factionid)
    return render(request, 'bushido/faction.html', {'faction': faction})


def userProfile(request):
    if request.method == 'POST':
        form = UserSettingsForm(request.POST, instance=request.user.userprofile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile is updated successfully')
        else:
            messages.error(request, 'Something went wrong')

    else:
        form = UserSettingsForm(instance=request.user.userprofile)
    return render(request, 'bushido/user_profile.html', {'form': form})


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
    #form_class = FilterForm
    template_name = "bushido/unit_list.html"

    def get_queryset(self):
        return Unit.objects.get_unique_card_names().prefetch_related("faction")


class FactionListView(ListView):
    model = Faction
    template_name = "bushido/faction_list.html"


class FeatListView(ListView):
    model = KiFeat
    template_name = "bushido/kifeat_list.html"


class SpecialListView(ListView):
    model = Special
    template_name = "bushido/special_list.html"


class TraitListView(ListView):
    model = Trait
    template_name = "bushido/trait_list.html"