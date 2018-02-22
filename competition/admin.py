from django.contrib import admin
from .models import Competition, Event, Staff, Round, Dance
# Register your models here.


class StaffInline(admin.TabularInline):
    model = Staff


class EventInline(admin.TabularInline):
    model = Event


class DanceInline(admin.TabularInline):
    model = Dance


class DanceThroughInline(admin.TabularInline):
    model = Event.dances.through


class CompetitionAdmin(admin.ModelAdmin):
    model = admin
    inlines = [
        StaffInline,
        EventInline,
        DanceInline
    ]


class CoupleInline(admin.TabularInline):
    model = Event.couples.through


class RoundInline(admin.TabularInline):
    model = Round


class EventAdmin(admin.ModelAdmin):
    model = admin
    inlines = [
        RoundInline,
        CoupleInline,
        DanceThroughInline
    ]


admin.site.register(Competition, CompetitionAdmin)
admin.site.register(Event, EventAdmin)
# admin.site.register(Event)
# admin.site.register(Staff)
