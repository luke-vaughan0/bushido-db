from django.contrib import admin

from .models import Unit, KiFeat, Trait, UnitTrait, Event, Theme, UnitType, List, ListUnit

admin.site.register(Unit)
admin.site.register(KiFeat)
admin.site.register(Trait)
admin.site.register(UnitTrait)
admin.site.register(Event)
admin.site.register(Theme)
admin.site.register(UnitType)
admin.site.register(List)
admin.site.register(ListUnit)
