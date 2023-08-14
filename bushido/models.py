from django.db import models
from django.db.models import OuterRef, Subquery
from django.conf import settings
import shortuuid


class UnitManager(models.Manager):
    def get_unique_card_names(self):
        # Fetch distinct card names along with all fields
        subquery = self.filter(cardName=OuterRef('cardName')).order_by('cardName')
        return self.filter(pk=Subquery(subquery.values('pk')[:1]))


class UserProfile(models.Model):
    def __str__(self):
        return self.user.username
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    use_unofficial_cards = models.BooleanField(default=True)


class Faction(models.Model):
    def __str__(self):
        return self.name
    shortName = models.CharField(max_length=20)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=3000)


class Unit(models.Model):

    def __str__(self):
        return self.name

    name = models.CharField(max_length=50)
    cardName = models.CharField(max_length=50, default="")
    meleePool = models.CharField(max_length=3, default="0")
    meleeBoost = models.CharField(max_length=3, default="0", blank=True)
    rangedPool = models.CharField(max_length=3, default="0")
    rangedBoost = models.CharField(max_length=3, default="0", blank=True)
    movePool = models.CharField(max_length=3, default="0")
    moveBoost = models.CharField(max_length=3, default="0", blank=True)
    kiStat = models.CharField(max_length=3, default="0")
    kiBoost = models.CharField(max_length=3, default="0", blank=True)
    kiMax = models.CharField(max_length=3, default="0")
    wounds = models.CharField(max_length=3, default="5", blank=True)
    size = models.CharField(max_length=10, default="Small")
    baseSize = models.CharField(max_length=3, default="30")
    cost = models.CharField(max_length=10, default="0")
    # faction = models.CharField(max_length=15, default="ronin")
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE)
    uniqueEffects = models.CharField(max_length=1500, default="", blank=True)

    kiFeats = models.ManyToManyField('KiFeat')
    traits = models.ManyToManyField('Trait', through='UnitTrait')

    objects = UnitManager()

    class Meta:
        ordering = ["faction", "name"]


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

    RestrictionChoices = [
        ("", ""),
        ("OPT", "Once per Turn"),
        ("OPG", "Once per Game"),
    ]

    name = models.CharField(max_length=30)
    cost = models.CharField(max_length=6)
    timing = models.CharField(max_length=8, choices=TimingChoices, default="Active")
    featType = models.CharField(max_length=8, choices=TypeChoices, default="Pe")
    featRange = models.CharField(max_length=5, default="", blank=True)
    isOpposed = models.BooleanField(default=False)
    noMove = models.BooleanField(default=False)
    noBTB = models.BooleanField(default=False)
    restriction = models.CharField(max_length=8, choices=RestrictionChoices, default="")
    description = models.CharField(max_length=600)

    class Meta:
        ordering = ["name"]


class Trait(models.Model):

    def __str__(self):
        return self.name

    name = models.CharField(max_length=30)
    full = models.CharField(max_length=40)
    description = models.CharField(max_length=1300)

    class Meta:
        ordering = ["name"]


class Special(models.Model):
    def __str__(self):
        return self.name

    name = models.CharField(max_length=50)
    description = models.CharField(max_length=600)
    exceptional = models.BooleanField(default=False)


class UnitTrait(models.Model):

    def __str__(self):
        return self.unit.name + " - " + self.trait.name

    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    trait = models.ForeignKey(Trait, on_delete=models.CASCADE)
    X = models.CharField(max_length=3, default="0", blank=True)
    Y = models.CharField(max_length=3, default="0", blank=True)
    descriptor = models.CharField(max_length=20, default="", blank=True)

    @property
    def formatted(self):
        return self.trait.name + self.trait.full.split(self.trait.name)[1]\
            .replace("X", self.X)\
            .replace("Y", self.Y)\
            .replace("Descriptor", self.descriptor)\
            .replace("Bonus", self.descriptor)

    class Meta:
        ordering = ["trait__name"]


class UnitType(models.Model):

    def __str__(self):
        return self.unit.name + " - " + self.type

    unit = models.ForeignKey(Unit, related_name="types", on_delete=models.CASCADE)
    type = models.CharField(max_length=30)


class Event(models.Model):
    def __str__(self):
        return self.name
    name = models.CharField(max_length=50, default="")
    cycle = models.CharField(max_length=30, default="None")
    cost = models.CharField(max_length=5, default="0")
    max = models.CharField(max_length=100, default="1", blank=True)
    # faction = models.CharField(max_length=15, default="")
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE)
    description = models.CharField(max_length=1000, default="")


class Theme(models.Model):
    def __str__(self):
        return self.faction.name + " - " + self.name
    name = models.CharField(max_length=40, default="")
    cycle = models.CharField(max_length=30, default="None")
    # faction = models.CharField(max_length=15, default="")
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE)
    validation = models.CharField(max_length=500, default="Unit.objects.all()")
    description = models.CharField(max_length=1000, default="")


class Enhancement(models.Model):
    def __str__(self):
        return self.name
    name = models.CharField(max_length=30, default="")
    cost = models.CharField(max_length=5, default="")
    max = models.CharField(max_length=5, default="")
    # faction = models.CharField(max_length=15, default="")
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE)
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
    id = models.CharField(max_length=25, primary_key=True, unique=True, default=shortuuid.uuid, editable=False)
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
    unit = models.ForeignKey(Unit, related_name="weapons", on_delete=models.CASCADE)
    strength = models.CharField(max_length=8, default="+0")
    isRanged = models.BooleanField(default=False)
    shortRange = models.CharField(max_length=5, default="", blank=True)
    mediumRange = models.CharField(max_length=5, default="", blank=True)
    longRange = models.CharField(max_length=5, default="", blank=True)
    traits = models.ManyToManyField('Trait', blank=True, through='WeaponTrait')
    specials = models.ManyToManyField('Special', blank=True, through='WeaponSpecial')


class WeaponTrait(models.Model):
    def __str__(self):
        return self.weapon.unit.name + " - " + self.weapon.name + " - " + self.trait.name

    weapon = models.ForeignKey(Weapon, related_name="weapontraits", on_delete=models.CASCADE)
    trait = models.ForeignKey(Trait, on_delete=models.CASCADE)
    X = models.CharField(max_length=3, default="0", blank=True)
    Y = models.CharField(max_length=3, default="0", blank=True)
    descriptor = models.CharField(max_length=20, default="", blank=True)

    @property
    def formatted(self):
        return self.trait.name + self.trait.full.split(self.trait.name)[1] \
            .replace("X", self.X) \
            .replace("Y", self.Y) \
            .replace("Descriptor", self.descriptor) \
            .replace("Bonus", self.descriptor)


class WeaponSpecial(models.Model):
    def __str__(self):
        return self.weapon.unit.name + " - " + self.weapon.name + " - " + self.special.name

    weapon = models.ForeignKey(Weapon, related_name="weaponspecials", on_delete=models.CASCADE)
    special = models.ForeignKey(Special, on_delete=models.CASCADE)
    cost = models.CharField(max_length=3, default="0")
