from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.views.generic import ListView
from bushido.models import Unit, KiFeat, UnitTrait, Trait, Theme, Event, List, ListUnit, Weapon, UserProfile,\
    WeaponTrait, WeaponSpecial, Faction, Special, Enhancement
from django.db.models import Q, Prefetch
from django.db import models
from django.contrib import auth, messages
from .forms import *
from django.contrib.auth.decorators import permission_required
from django.contrib.auth import login
from rest_framework import viewsets
from bushido.serializers import *
from bushido.utils import queryset_from_string, get_card
import jellyfish


MESSAGE_TAGS = {
    messages.DEBUG: "primary",
    messages.ERROR: "danger",
}


class ModelViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieve model information
    """
    queryset = Unit.objects.prefetch_related('kiFeats', 'traits', 'ronin_factions', 'unittrait_set__trait', 'types',
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
    Retrieve trait information
    """
    queryset = Trait.objects.all()
    serializer_class = TraitSerializer
    permission_classes = []
    filterset_fields = "__all__"


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieve event information
    """
    queryset = Event.objects.prefetch_related("faction")
    serializer_class = EventSerializer
    permission_classes = []
    filterset_fields = "__all__"


class EnhancementViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieve enhancement information
    """
    queryset = Enhancement.objects.prefetch_related("faction")
    serializer_class = EnhancementSerializer
    permission_classes = []
    filterset_fields = "__all__"


class ThemeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieve theme information
    """
    queryset = Theme.objects.prefetch_related("faction")
    serializer_class = ThemeSerializer
    permission_classes = []
    filterset_fields = "__all__"


class SpecialViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieve special ability information
    """
    queryset = Special.objects.all()
    serializer_class = SpecialSerializer
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
    return render(request, 'bushido/detail_views/feat_details.html', {'feat': feat})


@permission_required("bushido.change_ki_feat")
def editFeat(request, featid):
    feat = get_object_or_404(KiFeat, pk=featid)
    if request.method == "POST":
        form = EditFeat(request.POST, instance=feat)
        if form.is_valid():
            form.save()
            return redirect(reverse('bushido:featDetails', kwargs={'featid': featid}))
    else:
        form = EditFeat(instance=feat)
    return render(request, 'bushido/edit_views/edit_feat.html', {'feat': feat, "form": form})


def unitDetails(request, unitid):
    unit = get_object_or_404(
        Unit.objects.prefetch_related(
            Prefetch('unittrait_set', queryset=UnitTrait.objects.select_related('trait')),
            Prefetch('weapons', queryset=Weapon.objects.prefetch_related('weaponspecials__special', 'weapontraits__trait')),
        ),
        pk=unitid
    )
    cardUnits = Unit.objects.filter(cardName=unit.cardName)
    cardFront = get_card(request.user, unit, " Front")
    cardBack = get_card(request.user, unit, " Reverse")

    return render(request, 'bushido/detail_views/unit_details.html',
                  {'unit': unit, 'cardUnits': cardUnits, 'cardFront': cardFront, 'cardBack': cardBack})


@permission_required("bushido.change_unit")
def editUnit(request, unitid):
    unit = get_object_or_404(Unit, pk=unitid)
    cardFront = get_card(request.user, unit, " Front")
    cardBack = get_card(request.user, unit, " Reverse")

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
    return render(request, 'bushido/edit_views/edit_unit.html',
                  {'unit': unit, 'cardFront': cardFront, 'cardBack': cardBack,
                   "form": unitForm, 'weapon_formset': weapon_formset, 'trait_form': traitForm, 'type_form': typeForm})


def themeDetails(request, themeid):
    theme = get_object_or_404(Theme, pk=themeid)
    card = get_card(request.user, theme)
    return render(request, 'bushido/detail_views/theme_details.html', {'theme': theme, 'card': card})


@permission_required("bushido.change_theme")
def editTheme(request, themeid):
    theme = get_object_or_404(Theme, pk=themeid)
    card = get_card(request.user, theme)
    if request.method == "POST":
        form = EditTheme(request.POST, instance=theme)
        if form.is_valid():
            form.save()
            return redirect(reverse('bushido:themeDetails', kwargs={'themeid': themeid}))
    else:
        form = EditTheme(instance=theme)
    return render(request, 'bushido/edit_views/edit_theme.html', {'theme': theme, 'card': card, "form": form})


def eventDetails(request, eventid):
    event = get_object_or_404(Event, pk=eventid)
    card = get_card(request.user, event)
    return render(request, 'bushido/detail_views/event_details.html', {'event': event, 'card': card})


@permission_required("bushido.change_event")
def editEvent(request, eventid):
    event = get_object_or_404(Event, pk=eventid)
    card = get_card(request.user, event)
    if request.method == "POST":
        form = EditEvent(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect(reverse('bushido:eventDetails', kwargs={'eventid': eventid}))
    else:
        form = EditEvent(instance=event)
    return render(request, 'bushido/edit_views/edit_event.html', {'event': event, 'card': card, "form": form})


def enhancementDetails(request, enhancementid):
    enhancement = get_object_or_404(Enhancement, pk=enhancementid)
    card = get_card(request.user, enhancement)
    return render(request, 'bushido/detail_views/enhancement_details.html', {'enhancement': enhancement, 'card': card})


@permission_required("bushido.change_enhancement")
def editEnhancement(request, enhancementid):
    enhancement = get_object_or_404(Enhancement, pk=enhancementid)
    card = get_card(request.user, enhancement)
    if request.method == "POST":
        form = EditEnhancement(request.POST, instance=enhancement)
        if form.is_valid():
            form.save()
            return redirect(reverse('bushido:enhancementDetails', kwargs={'enhancementid': enhancementid}))
    else:
        form = EditEnhancement(instance=enhancement)
    return render(request, 'bushido/edit_views/edit_enhancement.html', {'enhancement': enhancement, 'card': card, "form": form})


def faction_details(request, factionid):
    faction = get_object_or_404(Faction, pk=factionid)
    return render(request, 'bushido/detail_views/faction_details.html', {'faction': faction})


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
    cost = 0
    for unit in unitList.listunit_set.all():
        try:
            cost += int(unit.unit.cost)
        except ValueError:
            print(f"error in {unit.name}")
        if unit.equipment:
            cost += int(unit.equipment.cost)
        for enhancement in unit.enhancements.all():
            cost += int(enhancement.cost)

    return render(request, 'bushido/view_list.html', {'list': unitList, "cost": cost})


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
    template_name = "bushido/list_views/unit_list.html"

    def get_queryset(self):
        return Unit.objects.get_unique_card_names().prefetch_related("faction")


class FactionListView(ListView):
    model = Faction
    template_name = "bushido/list_views/faction_list.html"


class FeatListView(ListView):
    model = KiFeat
    template_name = "bushido/list_views/kifeat_list.html"


class SpecialListView(ListView):
    model = Special
    template_name = "bushido/list_views/special_list.html"


class TermListView(ListView):
    model = Term
    template_name = "bushido/list_views/term_list.html"


class StateListView(ListView):
    model = State
    template_name = "bushido/list_views/state_list.html"


class TraitListView(ListView):
    model = Trait
    template_name = "bushido/list_views/trait_list.html"