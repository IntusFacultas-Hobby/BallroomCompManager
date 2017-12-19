from django import forms
from django.core.exceptions import ObjectDoesNotExist

from django_select2.forms import (
    HeavySelect2MultipleWidget, HeavySelect2Widget, ModelSelect2MultipleWidget,
    ModelSelect2TagWidget, ModelSelect2Widget, Select2MultipleWidget,
    Select2Widget
)
from .models import Studio, Request, Dancer, StudioRequest


class DancerForm(forms.ModelForm):
    class Meta:
        model = Dancer
        fields = ['name', 'email']


class StudioRequestForm(forms.ModelForm):
    # for requesting a new studio
    class Meta:
        model = StudioRequest
        fields = ["name", "address", "city", "state", "country", "zip_code"]
        widgets = {
            'state': Select2Widget,
            'country': Select2Widget,
        }


class AssociationForm(forms.Form):
    association_pin = forms.IntegerField(
        min_value=0,
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(AssociationForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(AssociationForm, self).clean()
        try:
            Studio.objects.get(association_pin=cleaned_data['association_pin'])
        except ObjectDoesNotExist:
            raise forms.ValidationError(
                "No studio exists with that pin."
            )

    def save(self, commit=True):
        # delete all other requests. Only one may exist at a time
        Request.objects.filter(dancer=self.user.dancer).delete()
        studio = Studio.objects.get(
            association_pin=self.cleaned_data['association_pin'])
        request = Request.objects.create(dancer=self.user.dancer,
                                         studio=studio)
        return request


class StudioForm(forms.ModelForm):
    # for modifying an existing studio
    class Meta:
        model = Studio
        fields = ['name', 'address', 'city', 'state', 'country', 'zip_code']
        widgets = {
            'state': Select2Widget,
            'country': Select2Widget,
        }
