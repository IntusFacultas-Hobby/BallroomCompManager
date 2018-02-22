from django import forms
from django.forms import ValidationError
from competition.models import Competition, Event, Dance
from bootstrap3_datetime.widgets import DateTimePicker
from django_select2.forms import (
    HeavySelect2MultipleWidget, HeavySelect2Widget, ModelSelect2MultipleWidget,
    ModelSelect2TagWidget, ModelSelect2Widget, Select2MultipleWidget,
    Select2Widget
)


class CompetitionForm(forms.ModelForm):
    class Meta:
        model = Competition
        fields = ['name', 'date_of_start', 'end_date_of_registration']
        widgets = {
            'date_of_start': DateTimePicker(
                options={"format": "YYYY-MM-DD"}),
            'end_date_of_registration': DateTimePicker(
                options={"format": "YYYY-MM-DD", }),
        }


class DanceForm(forms.ModelForm):
    class Meta:
        model = Dance
        fields = ['name']


class EventCreationForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['skill_group', 'name', 'time', 'max_per_heat']
        widgets = {
            'time': DateTimePicker(options={
                "format": "HH:mm",
                "icons": {
                    "date": "glyphicon glyphicon-time",
                    "up": "fa fa-arrow-up",
                    "down": "fa fa-arrow-down"
                }
            })
        }


class EventForm(forms.ModelForm):
    def __init__(self, user=None, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        event = kwargs.pop('instance', '')
        if isinstance(event, Event):
            self.fields['dances'] = forms.ModelMultipleChoiceField(
                queryset=event.competition.dances.all(),
                initial=event.dances.all())
            self.fields['dances'].required = False
        else:
            self.fields['dances'] = forms.ModelMultipleChoiceField(
                queryset=Event.objects.none())
            self.fields['dances'].required = False

    class Meta:
        model = Event
        fields = ['skill_group', 'name', 'time', 'max_per_heat']
        widgets = {
            'time': DateTimePicker(options={
                "format": "HH:mm",
                "icons": {
                    "date": "glyphicon glyphicon-time",
                    "up": "fa fa-arrow-up",
                    "down": "fa fa-arrow-down"
                }
            })
        }


DanceFormSet = forms.inlineformset_factory(Competition, Dance, extra=1,
                                           form=DanceForm, can_delete=True)
EventFormSet = forms.inlineformset_factory(
    Competition, Event, extra=1, form=EventForm, can_delete=True)

# this near duplicate exists because the select dropdown is created with JQUERY
# doesn't require a django version.
EventCreationFormSet = forms.inlineformset_factory(
    Competition, Event, extra=1, form=EventCreationForm, can_delete=True)
