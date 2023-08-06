from django import template
import django

register = template.Library()


@register.filter
def formatTrait(trait):
    return trait.trait.full.replace("X", trait.X).replace("Y", trait.Y).replace("Descriptor", trait.descriptor).replace("Bonus", trait.descriptor)


@register.filter
def formatWeapon(weapon):
    from bushido.models import WeaponSpecial, WeaponTrait
    text = "<b>" + weapon.name + "</b> | " + weapon.strength
    if weapon.isRanged:
        text += " | Ranged ({}/{}/{})".format(weapon.shortRange, weapon.mediumRange, weapon.longRange)
    else:
        text += " | Melee"
    for trait in weapon.traits.all():
        traitObject = WeaponTrait.objects.get(weapon=weapon, trait=trait)
        text += "<br>" + traitObject.trait.full.replace("X", traitObject.X).replace("Y", traitObject.Y).replace("Descriptor", traitObject.descriptor).replace("Bonus", traitObject.descriptor)
    for special in weapon.specials.all():
        specialObject = WeaponSpecial.objects.get(weapon=weapon, special=special)
        text += "<br>{} ({})".format(specialObject.special.name, specialObject.cost)
    return text+"<br>"


@register.filter
def addBrackets(text):
    if len(text) == 0:
        return ""
    return "("+text+")"
