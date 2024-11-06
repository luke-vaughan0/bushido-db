from bushido.models import *
from rest_framework import serializers
from drf_dynamic_fields import DynamicFieldsMixin
from urllib import parse


class ReadOnlyModelSerializer(serializers.ModelSerializer):
    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)
        for field in fields:
            fields[field].read_only = True
        return fields


class KiFeatSerializer(ReadOnlyModelSerializer):
    class Meta:
        model = KiFeat
        fields = "__all__"


class UnitTraitSerializer(ReadOnlyModelSerializer):
    id = serializers.ReadOnlyField(source='trait.id')
    name = serializers.ReadOnlyField(source='trait.name')
    full = serializers.ReadOnlyField(source='trait.full')
    formatted = serializers.SerializerMethodField()

    class Meta:
        model = UnitTrait
        exclude = ["unit", "trait"]

    def get_formatted(self, obj):
        return obj.trait.full.replace("X", obj.X).replace("Y", obj.Y).replace("Descriptor", obj.descriptor).replace("Bonus", obj.descriptor)


class WeaponTraitSerializer(ReadOnlyModelSerializer):
    id = serializers.ReadOnlyField(source='trait.id')
    name = serializers.ReadOnlyField(source='trait.name')
    full = serializers.ReadOnlyField(source='trait.full')
    formatted = serializers.SerializerMethodField()

    class Meta:
        model = WeaponTrait
        exclude = ["weapon", "trait"]

    def get_formatted(self, obj):
        return obj.trait.full.replace("X", obj.X).replace("Y", obj.Y).replace("Descriptor", obj.descriptor).replace("Bonus", obj.descriptor)


class WeaponSpecialSerializer(ReadOnlyModelSerializer):
    id = serializers.ReadOnlyField(source='special.id')
    name = serializers.ReadOnlyField(source='special.name')

    class Meta:
        model = WeaponSpecial
        exclude = ["weapon", "special"]


class WeaponSerializer(ReadOnlyModelSerializer):
    traits = UnitTraitSerializer(source="weapontraits", many=True)
    specials = WeaponSpecialSerializer(source="weaponspecials", many=True)

    class Meta:
        model = Weapon
        exclude = ["unit", "id"]


# Serializers define the API representation.
class UnitSerializer(DynamicFieldsMixin, ReadOnlyModelSerializer):
    kiFeats = KiFeatSerializer(many=True)
    traits = UnitTraitSerializer(source="unittrait_set", many=True)
    types = serializers.SlugRelatedField(many=True, read_only=True, slug_field="type")
    faction = serializers.ReadOnlyField(source='faction.name')
    weapons = WeaponSerializer(source="weapons.all", many=True)
    card_front = serializers.SerializerMethodField()
    card_reverse = serializers.SerializerMethodField()

    class Meta:
        model = Unit
        exclude = ['properties']

    def get_card_front(self, obj):
        return f"https://bushidodb.ddns.net/static/bushido/{obj.faction.shortName}/models/{parse.quote(obj.cardName)}%20Front.jpg"

    def get_card_reverse(self, obj):
        return f"https://bushidodb.ddns.net/static/bushido/{obj.faction.shortName}/models/{parse.quote(obj.cardName)}%20Reverse.jpg"


class TraitSerializer(ReadOnlyModelSerializer):
    class Meta:
        model = Trait
        fields = "__all__"


class EventSerializer(ReadOnlyModelSerializer):
    faction = serializers.ReadOnlyField(source='faction.name')

    class Meta:
        model = Event
        fields = "__all__"


class EnhancementSerializer(ReadOnlyModelSerializer):
    faction = serializers.ReadOnlyField(source='faction.name')

    class Meta:
        model = Enhancement
        fields = "__all__"


class ThemeSerializer(ReadOnlyModelSerializer):
    faction = serializers.ReadOnlyField(source='faction.name')

    class Meta:
        model = Theme
        exclude = ["validation"]


class SpecialSerializer(ReadOnlyModelSerializer):
    class Meta:
        model = Special
        fields = "__all__"
