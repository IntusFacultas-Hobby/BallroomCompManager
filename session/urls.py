from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from session import views


app_name = "session"
urlpatterns = [
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^account/$', views.ProfileView.as_view(), name='account'),
    url(r'^studio/$', views.StudioView.as_view(), name="studio"),
    url(r'^admin/', admin.site.urls),
    url(r'^dancers/delete/$', views.DeleteDancer.as_view(),
        name="delete_dancer"),
    url(r'^requests/confirm/$', views.RequestConfirm.as_view(),
        name="request_confirm"),
    url(r'^requests/delete/$', views.RequestDelete.as_view(),
        name="request_deny"),

]
