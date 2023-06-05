from django import forms
from bushido.models import Unit, List


class FilterForm(forms.Form):
    factions = list(Unit.objects.values_list("faction", flat=True).distinct())
    choices = []
    for faction in factions:
        choices.append((faction, faction))
    faction = forms.ChoiceField(choices=choices)


class EditUnit(forms.ModelForm):
    class Meta:
        model = Unit
        exclude = ["kiFeats", "traits"]
        # fields = '__all__'  # ["name", "meleePool", "meleeBoost", "rangedPool"]


class CreateListForm(forms.ModelForm):
    class Meta:
        model = List
        fields = ["name", "theme", "privacy"]


"""class EditUnit(forms.Form):
    name = forms.CharField(max_length=30)
    meleePool = forms.CharField(max_length=3)
    meleeBoost = forms.CharField(max_length=3)
    rangedPool = forms.CharField(max_length=3)
    rangedBoost = forms.CharField(max_length=3)
    movePool = forms.CharField(max_length=3)
    moveBoost = forms.CharField(max_length=3)
    kiStat = forms.CharField(max_length=3)
    kiBoost = forms.CharField(max_length=3)
    kiMax = forms.CharField(max_length=3)
    wounds = forms.CharField(max_length=3)
    size = forms.CharField(max_length=10)
    cost = forms.CharField(max_length=10)
    faction = forms.CharField(max_length=15)"""
