from bushido.models import *
from rest_framework import serializers
from drf_dynamic_fields import DynamicFieldsMixin


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

    class Meta:
        model = Unit
        #exclude = ['cost']
        fields = "__all__"


class TraitSerializer(ReadOnlyModelSerializer):
    class Meta:
        model = Trait
        fields = "__all__"
