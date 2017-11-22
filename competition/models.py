from django.db import models

# Create your models here.

class Competition(models.Model):
    name = models.CharField("Name", max_length=256)
    date = models.DateField("Date of Competition")

    def __str__(self):              # __unicode__ on Python 2
        return "%s %s" % (self.date, self.name)

class Event(models.Model):
    name = models.CharField("Name", max_length=256)
    time = models.TimeField("Time", auto_now=False)
    competition = models.ForeignField(Competition, on_delete=models.CASCADE)

    def __str__(self):
        return self.name