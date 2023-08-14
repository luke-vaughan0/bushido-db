from django.contrib import admin
from django.forms import TextInput, Textarea
from django.db import models
from simple_history.admin import SimpleHistoryAdmin

from .models import Unit, KiFeat, Trait, UnitTrait, Event, Theme, UnitType, List, ListUnit, Special, Weapon, WeaponTrait, WeaponSpecial, Enhancement, UserProfile


class ThemeAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 4, 'cols': 40})},
    }


admin.site.register(Unit, SimpleHistoryAdmin)
admin.site.register(KiFeat)
admin.site.register(Trait)
admin.site.register(UnitTrait)
admin.site.register(Event)
admin.site.register(Theme, ThemeAdmin)
admin.site.register(UnitType)
admin.site.register(List)
admin.site.register(ListUnit)
admin.site.register(Special)
admin.site.register(Weapon)
admin.site.register(WeaponTrait)
admin.site.register(WeaponSpecial)
admin.site.register(Enhancement)
admin.site.register(UserProfile)
