from django import forms
from django.core.exceptions import ObjectDoesNotExist
from .models import Studio, Request, Dancer


class DancerForm(forms.ModelForm):
    class Meta:
        model = Dancer
        fields = ['name', 'email']


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
        studio = Studio.objects.get(
            association_pin=self.cleaned_data['association_pin'])
        request = Request.objects.create(user=self.user, studio=studio)
        return request
