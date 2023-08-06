from django.contrib import admin

from .models import Unit, KiFeat, Trait, UnitTrait, Event, Theme, UnitType, List, ListUnit, Special, Weapon, WeaponTrait, WeaponSpecial, Enhancement, UserProfile

admin.site.register(Unit)
admin.site.register(KiFeat)
admin.site.register(Trait)
admin.site.register(UnitTrait)
admin.site.register(Event)
admin.site.register(Theme)
admin.site.register(UnitType)
admin.site.register(List)
admin.site.register(ListUnit)
admin.site.register(Special)
admin.site.register(Weapon)
admin.site.register(WeaponTrait)
admin.site.register(WeaponSpecial)
admin.site.register(Enhancement)
admin.site.register(UserProfile)
