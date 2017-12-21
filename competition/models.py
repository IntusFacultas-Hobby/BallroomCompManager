from datetime import date
from django.db import models
from django.contrib import admin
from competitor.models import Dancer, Studio


class Competition(models.Model):
    name = models.CharField("Name", max_length=256)
    date_of_start = models.DateField("Date of Competition")
    end_date_of_registration = models.DateField("Registration Deadline")
    host = models.ForeignKey(Studio, on_delete=models.CASCADE,
                             related_name="competitions")
    completed = models.BooleanField("Completed", default=False)

    @property
    def past_registration(self):
        return date.today() > self.end_date_of_registration

    def __str__(self):              # __unicode__ on Python 2
        return "%s %s" % (self.date_of_start, self.name)


class Staff(models.Model):
    ROLE_CHOICES = (
        (0, "Logistic"),
        (1, "Judge")
    )
    role = models.IntegerField("Role", choices=ROLE_CHOICES)
    dancer = models.ForeignKey(Dancer, on_delete=models.CASCADE,
                               related_name="roles")
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE,
                                    related_name="staff")

    def __str__(self):
        return self.ROLE_CHOICES[self.role][1] + " " + self.dancer.name + \
            " at " + self.competition.name + " " + \
            self.competition.date_of_start.strftime('%Y')

    def as_dict(self):
        return {
            "person": {
                "judging_pin": '"' + str(self.dancer.judging_pin) + '"',
                "name": '"' + self.dancer.name
            },
            "role": str(self.role)
        }


class Event(models.Model):
    skill_group = models.CharField("Skill Group", max_length=256)
    name = models.CharField("Name", max_length=256)
    time = models.TimeField("Time", auto_now=False, blank=True, null=True)
    competition = models.ForeignKey(
        Competition, on_delete=models.CASCADE, related_name="events")
    max_per_heat = models.IntegerField("Max Couples per Heat", default=0)

    def __str__(self):
        return self.name


class Round(models.Model):
    round_number = models.IntegerField("Round Number")
    event = models.ForeignKey(Event, on_delete=models.CASCADE,
                              related_name="heats")


class Couple(models.Model):
    lead = models.ForeignKey(Dancer, on_delete=models.CASCADE,
                             related_name="is_lead")
    follow = models.ForeignKey(Dancer, on_delete=models.CASCADE,
                               related_name="is_follow")
    events = models.ManyToManyField(Event)
    rounds = models.ManyToManyField(Round)
    totalMarks = models.IntegerField("Marks")


class Place(models.Model):
    '''
    Place is my solution to potential multiple couples being placed at the same
    position. An event can have many Places, and the place of each Place will
    be automatically calculated based on scores.
    '''
    place = models.IntegerField("Place")
    event = models.ForeignKey(Event, on_delete=models.CASCADE,
                              related_name="places")
    couple = models.ForeignKey(Couple, on_delete=models.CASCADE,
                               related_name="placements")
