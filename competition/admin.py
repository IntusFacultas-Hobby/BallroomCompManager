from django.contrib import admin
from .models import Competition, Event, Staff
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


admin.site.register(Competition, CompetitionAdmin)
# admin.site.register(Event)
# admin.site.register(Staff)
