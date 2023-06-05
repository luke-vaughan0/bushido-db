from django.db import models
from django.conf import settings
import shortuuid


class Unit(models.Model):

    def __str__(self):
        return self.name

    name = models.CharField(max_length=30)
    meleePool = models.CharField(max_length=3, default="0")
    meleeBoost = models.CharField(max_length=3, default="0", blank=True)
    rangedPool = models.CharField(max_length=3, default="0")
    rangedBoost = models.CharField(max_length=3, default="0", blank=True)
    movePool = models.CharField(max_length=3, default="0")
    moveBoost = models.CharField(max_length=3, default="0", blank=True)
    kiStat = models.CharField(max_length=3, default="0")
    kiBoost = models.CharField(max_length=3, default="0", blank=True)
    kiMax = models.CharField(max_length=3, default="0")
    wounds = models.CharField(max_length=3, default="0", blank=True)
    size = models.CharField(max_length=10, default="0")
    cost = models.CharField(max_length=10, default="0")
    faction = models.CharField(max_length=15, default="0")

    kiFeats = models.ManyToManyField('KiFeat')
    traits = models.ManyToManyField('Trait', through='UnitTrait')


class KiFeat(models.Model):

    def __str__(self):
        return self.name

    TimingChoices = [
        ("Active", "Active"),
        ("Instant", "Instant"),
        ("Simple", "Simple"),
        ("Complex", "Complex"),
    ]

    TypeChoices = [
        ("Pe", "Personal"),
        ("Ta", "Target"),
        ("Pu", "Pulse"),
        ("Au", "Aura"),
        ("Sp", "Special"),
    ]

    name = models.CharField(max_length=30)
    cost = models.CharField(max_length=5)
    timing = models.CharField(max_length=8, choices=TimingChoices, default="A")
    featType = models.CharField(max_length=8, choices=TypeChoices, default="Pe")
    featRange = models.CharField(max_length=5, default="0")
    description = models.CharField(max_length=300)


class Trait(models.Model):

    def __str__(self):
        return self.name

    name = models.CharField(max_length=30)
    full = models.CharField(max_length=40)
    description = models.CharField(max_length=300)


class Special(models.Model):
    def __str__(self):
        return self.name

    name = models.CharField(max_length=50)
    description = models.CharField(max_length=300)


class UnitTrait(models.Model):

    def __str__(self):
        return self.unit.name + " - " + self.trait.name

    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    trait = models.ForeignKey(Trait, on_delete=models.CASCADE)
    X = models.CharField(max_length=3, default="0", blank=True)
    Y = models.CharField(max_length=3, default="0", blank=True)
    descriptor = models.CharField(max_length=10, default="", blank=True)


class UnitType(models.Model):

    def __str__(self):
        return self.unit.name + " - " + self.type

    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    type = models.CharField(max_length=30)


#class UnitFeat(models.Model):
#    def __str__(self):
#        return self.unit.name + " - " + self.feat.name
#    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
#    feat = models.ForeignKey(KiFeat, on_delete=models.CASCADE)


class Faction(models.Model):
    def __str__(self):
        return self.name
    name = models.CharField(max_length=20)
    fullName = models.CharField(max_length=20)
    description = models.CharField(max_length=1000)


class Event(models.Model):
    def __str__(self):
        return self.name
    name = models.CharField(max_length=30, default="")
    cycle = models.CharField(max_length=30, default="None")
    cost = models.CharField(max_length=5, default="0")
    max = models.CharField(max_length=5, default="1", blank=True)
    faction = models.CharField(max_length=15, default="")
    description = models.CharField(max_length=1000, default="")


class Theme(models.Model):
    def __str__(self):
        return self.faction + " - " + self.name
    name = models.CharField(max_length=40, default="")
    cycle = models.CharField(max_length=30, default="None")
    faction = models.CharField(max_length=15, default="")
    validation = models.CharField(max_length=500, default="Unit.objects.all()")
    description = models.CharField(max_length=1000, default="")


class Enhancement(models.Model):
    def __str__(self):
        return self.name
    name = models.CharField(max_length=30, default="")
    cost = models.CharField(max_length=5, default="")
    max = models.CharField(max_length=5, default="")
    faction = models.CharField(max_length=15, default="")
    isEquipment = models.BooleanField(default=False)
    description = models.CharField(max_length=1000, default="")


class List(models.Model):
    def __str__(self):
        return self.owner.username + " - " + self.name

    PrivacyChoices = [
        ("Public", "Public"),
        ("Unlisted", "Unlisted"),
        ("Private", "Private"),
    ]

    name = models.CharField(max_length=30, default="")
    id = models.CharField(max_length=20, primary_key=True, unique=True, default=shortuuid.uuid, editable=False)
    units = models.ManyToManyField('Unit', through='ListUnit')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=0)
    privacy = models.CharField(max_length=8, choices=PrivacyChoices, default="Public")
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, default=0)


class ListUnit(models.Model):
    def __str__(self):
        return self.list.owner.username + " - " + self.list.name + " - " + self.unit.name

    list = models.ForeignKey(List, on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    enhancements = models.ManyToManyField('Enhancement', blank=True)
    equipment = models.CharField(max_length=30, blank=True)


class Weapon(models.Model):
    def __str__(self):
        return self.unit.name + " - " + self.name
    name = models.CharField(max_length=30, default="")
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    strength = models.CharField(max_length=5, default="+0")
    isRanged = models.BooleanField(default=False)
    shortRange = models.CharField(max_length=5, default="", blank=True)
    mediumRange = models.CharField(max_length=5, default="", blank=True)
    longRange = models.CharField(max_length=5, default="", blank=True)
    traits = models.ManyToManyField('Trait', blank=True, through='WeaponTrait')
    specials = models.ManyToManyField('Special', blank=True, through='WeaponSpecial')


class WeaponTrait(models.Model):
    def __str__(self):
        return self.weapon.unit.name + " - " + self.weapon.name + " - " + self.trait.name

    weapon = models.ForeignKey(Weapon, on_delete=models.CASCADE)
    trait = models.ForeignKey(Trait, on_delete=models.CASCADE)
    X = models.CharField(max_length=3, default="0", blank=True)
    Y = models.CharField(max_length=3, default="0", blank=True)
    descriptor = models.CharField(max_length=10, default="", blank=True)


class WeaponSpecial(models.Model):
    def __str__(self):
        return self.weapon.unit.name + " - " + self.weapon.name + " - " + self.special.name

    weapon = models.ForeignKey(Weapon, on_delete=models.CASCADE)
    special = models.ForeignKey(Special, on_delete=models.CASCADE)
    cost = models.CharField(max_length=3, default="0", blank=True)
