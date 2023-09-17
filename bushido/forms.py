from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from bushido.models import Unit, List, UserProfile, KiFeat, Weapon, WeaponTrait, WeaponSpecial, UnitTrait, UnitType, Faction, Theme, Event, Enhancement
from django.contrib.admin.widgets import FilteredSelectMultiple
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from django.forms.widgets import CheckboxSelectMultiple
from django.forms import inlineformset_factory
from django.forms.models import BaseInlineFormSet


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
    ronin_factions = forms.ModelMultipleChoiceField(queryset=Faction.objects.exclude(name="Ronin"), widget=CheckboxSelectMultiple,
                                             required=False)

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


class UnitTraitForm(forms.ModelForm):
    class Meta:
        model = UnitTrait
        fields = ['trait', 'X', 'Y', 'descriptor']


class UnitTypeForm(forms.ModelForm):
    class Meta:
        model = UnitType
        fields = ['type']


class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ["user"]


class CreateListForm(forms.ModelForm):
    class Meta:
        model = List
        fields = ["name", "theme", "privacy"]


class EditFeat(forms.ModelForm):
    description = forms.CharField(label="Description", widget=forms.Textarea, required=True)

    class Meta:
        model = KiFeat
        fields = "__all__"


class EditTheme(forms.ModelForm):
    description = forms.CharField(label="Description", widget=forms.Textarea, required=True)
    restriction = forms.CharField(label="Restriction", widget=forms.Textarea, required=False)

    class Meta:
        model = Theme
        fields = ["name", "cycle", "description", "restriction"]


class EditEvent(forms.ModelForm):
    description = forms.CharField(label="Description", widget=forms.Textarea, required=True)
    restriction = forms.CharField(label="Restriction", widget=forms.Textarea, required=False)

    class Meta:
        model = Event
        fields = ["name", "cycle", "cost", "max", "description", "restriction"]


class EditEnhancement(forms.ModelForm):
    description = forms.CharField(label="Description", widget=forms.Textarea, required=True)
    restriction = forms.CharField(label="Restriction", widget=forms.Textarea, required=False)

    class Meta:
        model = Enhancement
        fields = ["name", "cycle", "cost", "max", "description", "restriction"]


class WeaponTraitForm(forms.ModelForm):
    class Meta:
        model = WeaponTrait
        fields = ['trait', 'X', 'Y', 'descriptor']


class WeaponSpecialForm(forms.ModelForm):
    class Meta:
        model = WeaponSpecial
        fields = ['special', 'cost']


WeaponTraitFormSet = inlineformset_factory(Weapon, WeaponTrait, form=WeaponTraitForm, fk_name="weapon", extra=1)
WeaponSpecialFormSet = inlineformset_factory(Weapon, WeaponSpecial, form=WeaponSpecialForm, fk_name="weapon", extra=1)


class WeaponForm(BaseInlineFormSet):
    class Meta:
        model = Weapon
        fields = ['name', 'strength', 'isRanged', 'shortRange', 'mediumRange', 'longRange']

    def add_fields(self, form, index):
        super().add_fields(form, index)

        # Save the formset for a Book's Images in the nested property.
        form.traits = WeaponTraitFormSet(
            instance=form.instance,
            data=form.data if form.is_bound else None,
            files=form.files if form.is_bound else None,
            prefix="weapon-%s-%s"
                   % (form.prefix, WeaponTraitFormSet.get_default_prefix()),
        )
        form.specials = WeaponSpecialFormSet(
            instance=form.instance,
            data=form.data if form.is_bound else None,
            files=form.files if form.is_bound else None,
            prefix="weapon-%s-%s"
                   % (form.prefix, WeaponSpecialFormSet.get_default_prefix()),
        )

    def is_valid(self):
        """
        Also validate the nested formsets.
        """
        result = super().is_valid()

        if self.is_bound:
            for form in self.forms:
                if hasattr(form, "traits"):
                    result = result and form.traits.is_valid()
                if hasattr(form, "specials"):
                    result = result and form.specials.is_valid()

        return result

    def save(self, commit=True):
        """
        Also save the nested formsets.
        """
        result = super().save(commit=commit)

        for form in self.forms:
            if hasattr(form, "traits"):
                if not self._should_delete_form(form):
                    form.traits.save(commit=commit)
            if hasattr(form, "specials"):
                if not self._should_delete_form(form):
                    form.specials.save(commit=commit)

        return result


TraitFormSet = inlineformset_factory(Unit, UnitTrait, form=UnitTraitForm, fk_name="unit", extra=1)
TypeFormSet = inlineformset_factory(Unit, UnitType, form=UnitTypeForm, extra=1)
WeaponFormSet = inlineformset_factory(Unit, Weapon, formset=WeaponForm, fields=('name', 'strength', 'isRanged', 'shortRange', 'mediumRange', 'longRange'), extra=1)
