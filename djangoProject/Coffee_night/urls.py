from django.urls import path
from . import views

app_name = 'Coffee_night_route'
urlpatterns = [
    path('', views.route_filter, name='all_route'),
    path('add_route', views.route_add, name='add_route'),
    path('<int:id>', views.route_details, name='route_details'),
    path('<int:route_id>/reviews', views.route_reviews, name='route_reviews'),
    path('<int:route_id>/add_event', views.add_event, name='add_event'),
    path('<str:route_type>', views.route_filter, name='route_type'),
    path('<str:route_type>/<str:country>', views.route_filter, name='route_country'),
    path('<str:route_type>/<str:country>/<str:location>', views.route_filter, name='route_location'),



]