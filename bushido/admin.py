from django.contrib import admin
from django.forms import TextInput, Textarea
from django.db import models
from simple_history.admin import SimpleHistoryAdmin

from bushido.models import *


class ThemeAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 4, 'cols': 40})},
    }


class UnitAdmin(SimpleHistoryAdmin):
    filter_horizontal = ["kiFeats"]


admin.site.register(Unit, UnitAdmin)
admin.site.register(KiFeat)
admin.site.register(Trait)
admin.site.register(UnitTrait)
admin.site.register(Event)
admin.site.register(Theme, ThemeAdmin)
admin.site.register(Faction, ThemeAdmin)
admin.site.register(UnitType)
admin.site.register(List)
admin.site.register(ListUnit)
admin.site.register(Special)
admin.site.register(Weapon)
admin.site.register(WeaponTrait)
admin.site.register(WeaponSpecial)
admin.site.register(Enhancement)
admin.site.register(UserProfile)
admin.site.register(State, ThemeAdmin)
admin.site.register(Term, ThemeAdmin)
admin.site.register(Terrain, ThemeAdmin)
