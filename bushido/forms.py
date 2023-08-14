from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from bushido.models import Unit, List, UserProfile


#class FilterForm(forms.Form):
#    factions = list(Unit.objects.values_list("faction", flat=True).distinct())
#    choices = []
#    for faction in factions:
#        choices.append((faction, faction))
#    faction = forms.ChoiceField(choices=choices)

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']


class EditUnit(forms.ModelForm):
    uniqueEffects = forms.CharField(label="Unique Effects", widget=forms.Textarea, required=False)

    class Meta:
        model = Unit
        exclude = ["kiFeats", "traits", "faction"]


class EditUnitFeats(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ["kiFeats"]


class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ["user"]


class CreateListForm(forms.ModelForm):
    class Meta:
        model = List
        fields = ["name", "theme", "privacy"]

