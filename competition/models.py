from datetime import date
from django.db import models
from competitor.models import Dancer, Studio
from django.db.models import Q, Max


class Competition(models.Model):
    name = models.CharField("Name", max_length=256)
    date_of_start = models.DateField("Date of Competition")
    end_date_of_registration = models.DateField("Registration Deadline")
    host = models.ForeignKey(Studio, on_delete=models.CASCADE,
                             related_name="competitions")
    completed = models.BooleanField("Completed", default=False)
    begun = models.BooleanField("Begun", default=False)
    # stores a stringified JSON of the heatlist
    heat_list = models.CharField("Heat List", max_length=1000000,
                                 blank=True, null=True)
    event_limit = models.IntegerField("Event Limit", blank=True, null=True)
    # contains a hash summarizing it's current state
    status = models.CharField("Heat List", max_length=1000000,
                                 blank=True, null=True)
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
    active = models.BooleanField("Current", default=False)

    def as_dict(self):
        rounds = Round.objects.filter(event=self)
        rounds_dict = [obj.as_dict() for obj in rounds]
        act = ""
        if (self.active):
            act = "true"
        else:
            act = "false"
        return {
            "id": self.pk,
            "skill_group": self.skill_group,
            "name": self.name,
            "time": self.time.strftime("%H:%m"),
            "max_per_heat": self.max_per_heat,
            "active": act,
            "rounds": rounds_dict
        }

    def __str__(self):
        return self.name


class Round(models.Model):
    round_number = models.IntegerField("Round Number")
    event = models.ForeignKey(Event, on_delete=models.CASCADE,
                              related_name="heats")
    active = models.BooleanField("Current", default=False)
    completed = models.BooleanField("Completed", default=False)

    @property
    def name(self):
        max = self.event.heats.all().aggregate(Max('round_number'))
        max = max["round_number__max"]
        if max == 1 or self.round_number == max:
            return self.event.name + " Final"
        elif max == 2:
            if self.round_number == 1:
                return self.event.name + " Semi-Final"
            else:
                return self.event.name + " Final"
        else:
            if (self.round_number == (max - 2)):
                return self.event.name + " Quarter-Final"
            elif (self.round_number == (max - 1)):
                return self.event.name + " Semi-Final"
            else:
                fraction = max - self.round_number
                fraction = 2**fraction
                fraction = " 1 / " + str(fraction)
                sibling_rounds = self.event.heats.filter(
                    round_number=self.round_number
                )
                count = 0
                for sibling in sibling_rounds:
                    count += 1
                    if sibling.pk == self.pk:
                        break
                return self.event.name + fraction + " Heat " + str(count)

    def __str__(self):
        return self.name

    def as_dict(self):
        dancers = Couple.objects.filter(rounds__in=[self])
        dancers_dict = [obj.as_dict() for obj in dancers]
        act = ""
        if self.active:
            act = "true"
        else:
            act = "false"
        return {
            "id": self.pk,
            "round_number": self.round_number,
            "active": act,
            "dancers": dancers_dict,
            "name": self.name,
        }


class Couple(models.Model):
    lead = models.ForeignKey(Dancer, on_delete=models.CASCADE,
                             related_name="is_lead")
    follow = models.ForeignKey(Dancer, on_delete=models.CASCADE,
                               related_name="is_follow")
    events = models.ManyToManyField(Event, related_name="couples")
    rounds = models.ManyToManyField(Round, blank=True,
                                    related_name="couples")
    competition = models.ForeignKey(Competition, related_name="couples")
    couple_number = models.IntegerField("Competition Number")
    totalMarks = models.IntegerField("Marks", blank=True, null=True)

    def as_dict(self):
        return {
            "lead": self.lead.as_dict(),
            "follow": self.follow.as_dict(),
            "number": self.couple_number,
        }

    def __str__(self):  
        return self.lead.name + " and " + self.follow.name


class Performance(models.Model):
    round = models.ForeignKey(
        Round,
        on_delete=models.CASCADE,
        related_name="results"
    )
    couple = models.ForeignKey(
        Couple,
        on_delete=models.CASCADE,
        related_name="results"
    )

    def as_dict(self):
        marks = Mark.objects.filter(performance=self)
        marks_dict = [obj.as_dict() for obj in marks]
        return {
            "round": self.round.as_dict(),
            "couple": self.couple.as_dict(),
            "marks": marks_dict
        }


class Mark(models.Model):
    judge = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE,
        related_name="judge"
    )
    performance = models.ForeignKey(
        Performance,
        on_delete=models.CASCADE,
        related_name="performance"
    )

    def as_dict(self):
        return {
            "judge": self.judge.as_dict()
        }


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
