from django.conf.urls import url
from competitor import views
app_name = "competitor"

urlpatterns = [
    url(r'^$', views.index, name="index"),
]