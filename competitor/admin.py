from django.contrib import admin

# Register your models here.
from .models import Studio, Dancer, StudioRequest, Request


def approve(modeladmin, request, queryset):
    for query in queryset:
        studio = Studio.objects.create(
            name=query.name,
            address=query.address,
            city=query.city,
            state=query.state,
            country=query.country,
            zip_code=query.zip_code,
        )
        query.user.dancer.owned_studio = studio
        query.user.dancer.save()
        studio.save()
        query.user.save()
    queryset.delete()


approve.short_description = "Approve selected requests"


class StudioRequestAdmin(admin.ModelAdmin):
    list_display = ['name', 'user']
    ordering = ['name']
    actions = [approve]


admin.site.register(Studio)
admin.site.register(Dancer)
admin.site.register(StudioRequest, StudioRequestAdmin)
admin.site.register(Request)
