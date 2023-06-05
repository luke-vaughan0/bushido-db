from django.shortcuts import render, redirect, get_object_or_404

from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.views.generic import ListView
from bushido.models import Unit, KiFeat, UnitTrait, Trait, Theme, Event, List, ListUnit
from django.db.models import Q
from django.contrib import auth
from .forms import FilterForm, EditUnit, CreateListForm
from django.contrib.auth.decorators import permission_required


def index(request):
    if request.user.is_authenticated:
        text = "Hello " + request.user.username + ". You're at the index page"
    else:
        text = "Hello. You're at the index page"
    return HttpResponse(text)


def featDetails(request, featid):
    feat = get_object_or_404(KiFeat, pk=featid)
    units = Unit.objects.filter(kiFeats=feat)
    return render(request, 'bushido/feat_details.html', {'feat': feat, 'units': units})


def unitDetails(request, unitid):
    unit = get_object_or_404(Unit, pk=unitid)
    traits = UnitTrait.objects.filter(unit=unit)
    cardFront = 'bushido/' + unit.faction + "/" + unit.name + " Front.jpg"
    cardBack = 'bushido/' + unit.faction + "/" + unit.name + " Reverse.jpg"
    return render(request, 'bushido/unit_details.html', {'unit': unit, 'cardFront': cardFront, 'cardBack': cardBack, 'traits': traits})


@permission_required("unit.change_unit")
def editUnit(request, unitid):
    unit = get_object_or_404(Unit, pk=unitid)
    traits = UnitTrait.objects.filter(unit=unit)
    cardFront = 'bushido/' + unit.faction + "/" + unit.name + " Front.jpg"
    cardBack = 'bushido/' + unit.faction + "/" + unit.name + " Reverse.jpg"
    if request.method == "POST":
        form = EditUnit(request.POST, instance=unit)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("./")
    else:
        form = EditUnit(instance=unit)
    return render(request, 'bushido/edit_unit.html', {'unit': unit, 'cardFront': cardFront, 'cardBack': cardBack, 'traits': traits, "form": form})


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
        filters = self.request.GET
        print(filters)
        if len(filters) == 0:
            return Unit.objects.all()
        return []


class FeatListView(ListView):
    model = KiFeat
    template_name = "bushido/kifeat_list.html"


class TraitListView(ListView):
    model = Trait
    template_name = "bushido/trait_list.html"