import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()

from competition.models import Competition, Couple
from competitor.models import Dancer


c = Competition.objects.all()[0]

for x in range(0, 86):
    x2 = x + 86
    d1 = Dancer.objects.all()[x]
    d2 = Dancer.objects.all()[x2]
    couple = Couple.objects.create(
        competition=c, lead=d1, follow=d2, couple_number=x)
    events = c.events.all()
    for event in events:
        event.couples.add(couple)
