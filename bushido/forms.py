from django import forms
from bushido.models import Unit, List


#class FilterForm(forms.Form):
#    factions = list(Unit.objects.values_list("faction", flat=True).distinct())
#    choices = []
#    for faction in factions:
#        choices.append((faction, faction))
#    faction = forms.ChoiceField(choices=choices)


class EditUnit(forms.ModelForm):
    uniqueEffects = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = Unit
        exclude = ["kiFeats", "traits", "faction"]


class EditUnitFeats(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ["kiFeats"]


class CreateListForm(forms.ModelForm):
    class Meta:
        model = List
        fields = ["name", "theme", "privacy"]

