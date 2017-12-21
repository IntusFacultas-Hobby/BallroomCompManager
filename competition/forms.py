from django import forms
from competition.models import Competition, Event
from bootstrap3_datetime.widgets import DateTimePicker


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


class EventForm(forms.ModelForm):
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


EventFormSet = forms.inlineformset_factory(
    Competition, Event, form=EventForm, extra=1)
