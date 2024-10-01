from django.db import models
from django.db.models import OuterRef, Subquery, Case, When, Value, Q
from django.conf import settings
from simple_history.models import HistoricalRecords
from ordered_model.models import OrderedModel
from bushido.utils import queryset_from_string, q_object_from_string, get_properties
import shortuuid
import re
import datetime

CycleChoices = [
        ("Risen Sun", "Risen Sun"),
        ("Weeping Sky", "Weeping Sky"),
    ]


class UnitManager(models.Manager):
    def get_unique_card_names(self):
        # Fetch distinct card names along with all fields
        subquery = self.filter(cardName=OuterRef('cardName')).order_by('cardName')
        return self.filter(pk=Subquery(subquery.values('pk')[:1]))


class SpecialManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().annotate(
            type=Case(
                When(name__endswith='Attack', then=Value(1)),
                When(name__endswith='Defense', then=Value(2)),
                default=Value(3),
                output_field=models.CharField(),
            )
        ).order_by('type', 'name')


class UserProfile(models.Model):
    def __str__(self):
        return self.user.username

    ColourChoices = [
        ("light", "Light"),
        ("dark", "Dark"),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    website_theme = models.CharField(max_length=10, choices=ColourChoices, default="light")
    use_unofficial_cards = models.BooleanField(default=True)
    hide_unofficial_card_message = models.BooleanField(default=False)


class Faction(OrderedModel):
    def __str__(self):
        return self.name
    shortName = models.CharField(max_length=20)
    name = models.CharField(max_length=50)
    description = models.TextField()

    @property
    def all_units(self):
        return self.unit_set.all() | self.ronin_units.all()


class Unit(models.Model):

    def __str__(self):
        return self.name
    # game stuff
    name = models.CharField(max_length=50)
    cardName = models.CharField(max_length=50, default="")
    meleePool = models.CharField(max_length=3, default="0")
    meleeBoost = models.CharField(max_length=3, blank=True)
    rangedPool = models.CharField(max_length=3, default="0")
    rangedBoost = models.CharField(max_length=3, blank=True)
    movePool = models.CharField(max_length=3, default="0")
    moveBoost = models.CharField(max_length=3, blank=True)
    kiStat = models.CharField(max_length=3, default="0")
    kiBoost = models.CharField(max_length=3, blank=True)
    kiMax = models.CharField(max_length=3, default="0")
    wounds = models.CharField(max_length=3, default="5", blank=True)
    size = models.CharField(max_length=10, default="Small")
    baseSize = models.CharField(max_length=3, default="30")
    cost = models.CharField(max_length=10, default="0")
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE)
    uniqueEffects = models.CharField(max_length=1500, blank=True)
    unique = models.BooleanField(default=True)
    max = models.CharField(max_length=8, default="1")

    ronin_factions = models.ManyToManyField("Faction", related_name="ronin_units", blank=True)
    kiFeats = models.ManyToManyField('KiFeat', blank=True)
    traits = models.ManyToManyField('Trait', through='UnitTrait', blank=True)

    wave = models.CharField(max_length=3, default="0")

    # internal stuff
    properties = models.CharField(max_length=1000, blank=True)

    objects = UnitManager()
    history = HistoricalRecords()

    @property
    def rulings(self):
        tags = [self.name]
        return Ruling.objects.filter(tags__tag__in=tags)

    class Meta:
        unique_together = ["faction", "name"]
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
        ("Personal", "Personal"),
        ("Target", "Target"),
        ("Pulse", "Pulse"),
        ("Aura", "Aura"),
        ("Special", "Special"),
    ]

    RestrictionChoices = [
        ("OPT", "Once per Turn"),
        ("OPG", "Once per Game"),
    ]

    name = models.CharField(max_length=50)
    cost = models.CharField(max_length=6)
    timing = models.CharField(max_length=8, choices=TimingChoices, default="Active")
    featType = models.CharField(max_length=8, choices=TypeChoices, default="Personal")
    featRange = models.CharField(max_length=5, default="", blank=True)
    isOpposed = models.BooleanField(default=False)
    noMove = models.BooleanField(default=False)
    noBTB = models.BooleanField(default=False)
    limit = models.CharField(max_length=8, choices=RestrictionChoices, default="", blank=True)
    description = models.CharField(max_length=600)

    @property
    def rulings(self):
        tags = [self.name]
        return Ruling.objects.filter(tags__tag__in=tags)

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

    objects = SpecialManager()


class UnitTrait(models.Model):

    def __str__(self):
        return self.unit.name + " - " + self.trait.name

    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    trait = models.ForeignKey(Trait, on_delete=models.CASCADE)
    X = models.CharField(max_length=3, blank=True)
    Y = models.CharField(max_length=3, blank=True)
    descriptor = models.CharField(max_length=50, blank=True)

    @property
    def formatted(self):
        extra = self.trait.full.split(self.trait.name)[1]
        text = self.trait.name + extra\
            .replace("X", self.X)\
            .replace("Y", self.Y)\
            .replace("Descriptor", self.descriptor)\
            .replace("Bonus", self.descriptor)
        if "Descriptor" not in extra and "Bonus" not in extra and self.descriptor != "":
            text += f" [{self.descriptor}]"
        return text

    def save(self, *args, **kwargs):
        if "X" in self.trait.full and self.X == "":
            self.X = "1"
        if "Y" in self.trait.full and self.Y == "":
            self.Y = "1"
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["trait__name"]


class UnitType(models.Model):

    def __str__(self):
        return self.unit.name + " - " + self.type

    unit = models.ForeignKey(Unit, related_name="types", on_delete=models.CASCADE)
    type = models.CharField(max_length=30)

    class Meta:
        ordering = ["type"]


class Event(models.Model):
    def __str__(self):
        return self.name
    name = models.CharField(max_length=50, default="")
    cycle = models.CharField(max_length=30, choices=CycleChoices, blank=True)
    cost = models.CharField(max_length=5, default="0")
    max = models.CharField(max_length=100, default="1", blank=True)
    # faction = models.CharField(max_length=15, default="")
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE)
    description = models.CharField(max_length=2000, default="")
    restriction = models.CharField(max_length=300, blank=True)


class Theme(models.Model):
    def __str__(self):
        return self.faction.name + " - " + self.name
    name = models.CharField(max_length=40, default="")
    cycle = models.CharField(max_length=30, choices=CycleChoices, blank=True)
    # faction = models.CharField(max_length=15, default="")
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE)
    validation = models.CharField(max_length=500, blank=True)
    description = models.CharField(max_length=1000, default="No description")
    restriction = models.CharField(max_length=300, blank=True)

    @property
    def permitted_units(self):
        permitted = Unit.objects.all()
        properties = get_properties(self)
        for filter_string in properties["FILTER"]:
            permitted = permitted.filter(q_object_from_string(filter_string))
        permitted |= Unit.objects.filter(properties__contains="ANYTHEME " + self.faction.shortName)
        # TODO models that can go in any theme that allows x model (eg niseru)
        for filter_string in properties["EXCLUDE"]:
            permitted = permitted.exclude(q_object_from_string(filter_string))
        permitted = permitted.exclude(Q(properties__contains="ONLYTHEME") & ~Q(properties__contains="ONLYTHEME " + self.name))
        return permitted.distinct()

    def save(self, *args, **kwargs):
        if len(self.validation) == 0 and len(self.restriction) != 0:
            permitted = re.search(r"Permitted \[(.*)\]", self.restriction)
            exclusion = re.search(r"Exclusion \[(.*)\]", self.restriction)
            if exclusion:
                exclusionList = exclusion.group(1).split(", ")
            if permitted:
                permittedList = permitted.group(1).split(", ")
            if permitted:
                result = "faction__shortName=\"" + self.faction.shortName + "\" AND types__type__in=["
                ronin = []
                for item in permittedList:
                    if item.find("Ronin") == -1:
                        result += "\"" + item + "\", "
                    else:
                        ronin.append(item)
                result = result[:-1] + "]"
                if len(ronin) != 0:
                    result = "(" + result + ") OR (ronin_factions__shortName=\"" + self.faction.shortName + "\" AND types__type__in=["
                    for item in ronin:
                        result += "\"" + item.replace("Ronin ", "") + "\", "
                    result = result[:-2] + "])"
            else:
                result = "faction__shortName=\"" + self.faction.shortName + "\""
            if exclusion:
                result += "; EXCLUDE types__type__in=["
                for item in exclusionList:
                    result += "\"" + item + "\", "
                result = result[:-2] + "]"
            try:
                test = queryset_from_string(result)
                if len(test) == 0:
                    result = "faction__shortName=\"" + self.faction.shortName + "\""
            except:
                result = "faction__shortName=\"" + self.faction.shortName + "\""
            self.validation = result
        super().save(*args, **kwargs)


class Enhancement(models.Model):
    def __str__(self):
        return self.name
    name = models.CharField(max_length=50, default="")
    cost = models.CharField(max_length=5, default="")
    max = models.CharField(max_length=5, default="")
    cycle = models.CharField(max_length=30, choices=CycleChoices, blank=True)
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE)
    isEquipment = models.BooleanField(default=False)
    description = models.CharField(max_length=2000, default="")
    restriction = models.CharField(max_length=300, blank=True)

    class Meta:
        ordering = ["faction", "name"]


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
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE)

    def is_list_valid(self):
        permitted = self.theme.permitted_units  # TODO ronin themes
        for listunit in self.listunit_set.all():
            properties = get_properties(listunit.unit)
            if listunit.unit not in permitted:
                return False
            if "Insignificant" in listunit.unit.traits.values_list("name", flat=True) or "Animal" in listunit.unit.types.values_list("type", flat=True):
                if "ALLOWENHANCEMENTS" not in properties:
                    if listunit.equipment or len(listunit.enhancements.all()) != 0:
                        return False
        return True


class ListUnit(models.Model):
    def __str__(self):
        return self.list.owner.username + " - " + self.list.name + " - " + self.unit.name

    list = models.ForeignKey(List, on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    enhancements = models.ManyToManyField('Enhancement', blank=True, related_name="used_enhancements", limit_choices_to={"isEquipment": False})
    equipment = models.ForeignKey(Enhancement, blank=True, null=True, on_delete=models.CASCADE, limit_choices_to={"isEquipment": True})

    class Meta:
        ordering = ["unit__name"]


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
    X = models.CharField(max_length=3, blank=True)
    Y = models.CharField(max_length=3, blank=True)
    descriptor = models.CharField(max_length=50, blank=True)

    @property
    def formatted(self):
        extra = self.trait.full.split(self.trait.name)[1]
        text = self.trait.name + extra \
            .replace("X", self.X) \
            .replace("Y", self.Y) \
            .replace("Descriptor", self.descriptor) \
            .replace("Bonus", self.descriptor)
        if "Descriptor" not in extra and "Bonus" not in extra and self.descriptor != "":
            text += f" [{self.descriptor}]"
        return text

    def save(self, *args, **kwargs):
        if "X" in self.trait.full and self.X == "":
            self.X = "1"
        if "Y" in self.trait.full and self.Y == "":
            self.Y = "1"
        super().save(*args, **kwargs)


class WeaponSpecial(models.Model):
    def __str__(self):
        return self.weapon.unit.name + " - " + self.weapon.name + " - " + self.special.name

    weapon = models.ForeignKey(Weapon, related_name="weaponspecials", on_delete=models.CASCADE)
    special = models.ForeignKey(Special, on_delete=models.CASCADE)
    cost = models.CharField(max_length=3, default="0")


class State(models.Model):
    def __str__(self):
        return self.name

    name = models.CharField(max_length=50)
    marker = models.CharField(max_length=50)
    description = models.CharField(max_length=5000)


class Term(models.Model):
    def __str__(self):
        return self.name

    name = models.CharField(max_length=50)
    description = models.CharField(max_length=5000)


class Action(models.Model):
    def __str__(self):
        return self.name

    ActionTypeChoices = [
        ("Simple", "Simple"),
        ("Complex", "Complex"),
    ]

    name = models.CharField(max_length=30)
    action_type = models.CharField(max_length=15, choices=ActionTypeChoices, default="Simple")
    description = models.CharField(max_length=1000)
    standard_action = models.BooleanField(default=True)
    no_move = models.BooleanField(default=False)
    no_btb = models.BooleanField(default=False)


class Terrain(models.Model):
    def __str__(self):
        return self.name

    PassageChoices = [
        ("Normal", "Normal"),
        ("Difficult", "Difficult"),
        ("Impassable", "Impassable"),
        ("Ideal", "Ideal"),
    ]
    VisibilityChoices = [
        ("Clear", "Clear"),
        ("Obscuring", "Obscuring"),
        ("Blocking", "Blocking"),
        ("Enhancing", "Enhancing"),
    ]
    SizeChoices = [
        ("Zero", "Zero"),
        ("Tiny", "Tiny"),
        ("Small", "Small"),
        ("Medium", "Medium"),
        ("Large", "Large"),
        ("Huge", "Huge"),
    ]

    name = models.CharField(max_length=50)
    cycle = models.CharField(max_length=30, choices=CycleChoices, blank=True)
    cost = models.CharField(max_length=20)
    max = models.CharField(max_length=20, default="1", blank=True)
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE)
    description = models.CharField(max_length=2000)
    restriction = models.CharField(max_length=300, blank=True)
    destructible = models.BooleanField(default=False)
    passage = models.CharField(max_length=15, choices=PassageChoices)
    visibility = models.CharField(max_length=15, choices=VisibilityChoices)
    size = models.CharField(max_length=10, choices=SizeChoices)
    properties = models.CharField(max_length=1000, blank=True)
    base_size = models.CharField(max_length=50, blank=True)


class Ruling(models.Model):
    def __str__(self):
        return self.ruling if len(self.ruling) < 50 else self.ruling[:47] + "..."

    ruling = models.CharField(max_length=500)
    date = models.DateField(default=datetime.date.today)


class RulingTag(models.Model):
    def __str__(self):
        return self.tag + " - " + self.ruling.ruling[:12]

    ruling = models.ForeignKey(Ruling, related_name="tags", on_delete=models.CASCADE)
    tag = models.CharField(max_length=100)

    class Meta:
        ordering = ["tag"]
