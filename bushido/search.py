from django.shortcuts import get_object_or_404
from bushido.models import Unit, KiFeat, UnitTrait, Trait, Theme, Event, List, ListUnit, Weapon, UserProfile,\
    WeaponTrait, WeaponSpecial, Faction, Special, Enhancement, Terrain, State
from django.db.models import Q, Prefetch, Max
from django.db import models
import jellyfish
import re


SEARCH_TAGS = {
    "kifeat": ("kiFeats__name", [Unit]),
    "trait": ("traits__name", [Unit]),
    "traitx": ("unittrait__X", [Unit]),
    "traity": ("unittrait__Y", [Unit]),
    "traitd": ("unittrait__descriptor", [Unit]),
    "hasranged": ("weapons__isRanged", [Unit]),
    "faction": ("faction__shortName", [Unit, Event, Theme, Enhancement, Terrain]),
    "type": ("types__type", [Unit]),
}


def search_all(search_query):
    search_models = [Unit, KiFeat, Trait, Theme, Special, Faction, Event, Enhancement, State]
    search_results = []
    extra_queries = [
        [Unit, Q(types__type__icontains=search_query)]
    ]
    filter_pattern = r"(\b\w*):(\w+|\".*\")"
    for match in re.finditer(filter_pattern, search_query):
        extra_queries.append([match.group(1), match.group(2).replace('"', "")])
    search_query = re.sub(filter_pattern, "", search_query).strip()
    for model in search_models:
        should_add = True
        q_object = Q()
        if search_query:
            fields = [x for x in model._meta.fields if isinstance(x, models.CharField)]
            search_queries = [Q(**{x.name + "__icontains": search_query}) for x in fields]
            for query in search_queries:
                q_object = q_object | query
        for extra_query in extra_queries:
            if extra_query[0] == model and search_query:
                q_object = q_object | extra_query[1]
            elif type(extra_query[0]) == str:
                try:
                    thing = SEARCH_TAGS[extra_query[0]]
                    if model in thing[1]:
                        if extra_query[0] == "hasranged":
                            print("hello")
                            q_object = q_object & Q(**{thing[0]: True if extra_query[1].lower() in ["true", "yes"] else False})
                        else:
                            q_object = q_object & Q(**{f"{thing[0]}__icontains": extra_query[1]})
                        continue
                except KeyError:
                    if hasattr(model, extra_query[0]):
                        q_object = q_object & Q(**{f"{extra_query[0]}__icontains": extra_query[1]})
                        continue
                should_add = False
                break
        if not should_add:
            continue
        results = model.objects.filter(q_object)
        if hasattr(model, "faction"):
            results = results.select_related("faction")
        search_results.extend(results)
    result = list({result.pk: result for result in search_results}.values())
    rankedResults = []
    for item in result:
        rankedResults.append([item, jellyfish.jaro_winkler_similarity(item.name.lower(), search_query.lower())])
    rankedResults = sorted(rankedResults, key=lambda x: x[1], reverse=True)
    result = [x[0] for x in rankedResults]
    return result
