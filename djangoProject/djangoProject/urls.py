"""djangoProject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from Coffee_night import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('route/', include('Coffee_night.urls')),
    # path('event/all', views.all_events, name='all_events'),
    path('event/<event_id>', views.event_handler, name='event_handler'),
    path('event/<event_id>/add_me', views.add_me_to_event, name='add_me_to_event'),
    path('event/<event_id>/accept_user', views.event_accept_user, name='accept_user'),
    path('login', views.user_login),
    path('logout', views.user_logout),
    path('registration', views.user_registration)
]
