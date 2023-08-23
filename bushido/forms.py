from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from bushido.models import Unit, List, UserProfile, KiFeat
from django.contrib.admin.widgets import FilteredSelectMultiple
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from django.forms.widgets import CheckboxSelectMultiple


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']


class EditUnit(forms.ModelForm):
    uniqueEffects = forms.CharField(label="Unique Effects", widget=forms.Textarea, required=False)
    # kiFeats = forms.ModelMultipleChoiceField(queryset=KiFeat.objects.all(),
                                             #widget=FilteredSelectMultiple(
                                                 #verbose_name=KiFeat._meta.verbose_name_plural, is_stacked=False))
    kiFeats = forms.ModelMultipleChoiceField(queryset=KiFeat.objects.all(), widget=CheckboxSelectMultiple, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.fields['name'].widget.attrs['class'] = 'form-control-lg'
        self.fields['baseSize'].widget.attrs['class'] = 'form-control'

    class Meta:
        model = Unit
        exclude = ["traits", "faction"]


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

