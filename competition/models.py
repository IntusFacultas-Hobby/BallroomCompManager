from django.db import models
from competitor.models import Dancer


class Competition(models.Model):
    name = models.CharField("Name", max_length=256)
    date = models.DateField("Date of Competition")

    def __str__(self):              # __unicode__ on Python 2
        return "%s %s" % (self.date, self.name)


class Event(models.Model):
    skill_group = models.CharField("Name", max_length=256)
    name = models.CharField("Name", max_length=256)
    time = models.TimeField("Time", auto_now=False)
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
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
