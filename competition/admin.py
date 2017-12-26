from django.contrib import admin
from .models import Competition, Event, Staff, Round
# Register your models here.


class StaffInline(admin.TabularInline):
    model = Staff


class EventInline(admin.TabularInline):
    model = Event


class CompetitionAdmin(admin.ModelAdmin):
    model = admin
    inlines = [
        StaffInline,
        EventInline
    ]


class CoupleInline(admin.TabularInline):
    model = Event.couples.through


class RoundInline(admin.TabularInline):
    model = Round


class EventAdmin(admin.ModelAdmin):
    model = admin
    inlines = [
        RoundInline,
        CoupleInline
    ]


admin.site.register(Competition, CompetitionAdmin)
admin.site.register(Event, EventAdmin)
# admin.site.register(Event)
# admin.site.register(Staff)
