from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from Coffee_night import models
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.db import connection
from mongo_utils import MongoDBConnection
from bson import ObjectId
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
import json
import datetime


# Create your views here.
def route_filter(request, route_type=None, country=None, location=None):
    query_filter = []
    if route_type is not None:
        query_filter.append(f"route_type='{route_type}'")
    if country is not None:
        query_filter.append(f"country='{country}'")
    if location is not None:
        query_filter.append(f"loc='{location}'")

    cursor = connection.cursor()
    filter_str = ' AND '.join(query_filter)
    join_result = f"""SELECT Coffee_night_route.id, 
                             Coffee_night_route.country, 
                             Coffee_night_route.desc, 
                             Coffee_night_route.duration, 
                             Coffee_night_route.stop_point,
                             Coffee_night_route.loc, 
                             Coffee_night_route.route_type, 
                             start_point.name, destination_point.name FROM Coffee_night_route 
                             
                     JOIN Coffee_night_places as start_point
                     ON start_point.id = Coffee_night_route.start_point
                     
                     JOIN Coffee_night_places as destination_point
                     ON destination_point.id = Coffee_night_route.destination_point
                     
                     WHERE """ + filter_str

    cursor.execute(join_result)
    result = cursor.fetchall()
    cursor.close()

    # new_result = []
    # for itm in result:
    #     new_id = itm[0]
    #     new_country = itm[1]
    #     new_desc = itm[2]
    #     new_duration = itm[3]
    #     new_stop_point = itm[4]
    #     new_loc = itm[5]
    #     new_route_type = itm[6]
    #     new_start_point = itm[7]
    #     new_destination_point = itm[8]
    #
    #     buffer = {'id':new_id, 'country': new_country, 'desc': new_desc, 'duration': new_duration,
    #               'stop_point': new_stop_point, 'loc': new_loc, 'route_type': new_route_type,
    #               'start_point': new_start_point, 'destination_point': new_destination_point}

    new_result = [{'id': itm[0], 'country': itm[1], 'desc': itm[2], 'duration': itm[3], 'stop_point': itm[4],
                   'loc': itm[5], 'route_type': itm[6], 'start_point': itm[7], 'destination_point': itm[8]}
                  for itm in result]

    p = Paginator(new_result, 2)
    num_page = request.GET.get('page', default=1)
    if p.num_pages < int(num_page):
        num_page = 1
    select_page = p.get_page(num_page)

    # result = models.Route.objects.raw(join_result + filter_str)
    # result = models.Route.objects.all().filter(**query_filter)
    # return HttpResponse(select_page.object_list)

    return render(request, 'route_filter.html', {'result': select_page.object_list})


def route_details(request: object, id: object) -> object:
    route_result = models.Route.objects.all().filter(id=id)
    event_result = models.Event.objects.all().filter(id_route=id)
    event_result_list = [{'id': itm.id, 'id_route': itm.id_route, 'event_admin': itm.event_admin,
                          'event_users': itm.event_users, 'start_data': itm.start_data,
                          'price': itm.price} for itm in event_result]

    with MongoDBConnection('admin', 'admin', '127.0.0.1') as db:
        collec = db['stop_points']
        stop_points = collec.find_one({"_id": ObjectId(route_result[0].stop_point)})

    # Було закоментовано з метою тестування
    # return render(request, 'route_details.html', {'start_point': route_result[0].start_point,
    #                                               'stop_point': stop_points['_id'],
    #                                               'destination_point': route_result[0].destination_point,
    #                                               'country': route_result[0].country, 'loc': route_result[0].loc,
    #                                               'route_type': route_result[0].route_type,
    #                                               'desc': route_result[0].desc,
    #                                               'duration': route_result[0].duration, 'event': event_result_list})

    return HttpResponse(({"start_point": itm.start_point, "stop_point": itm.stop_point,
                          "destination_point": itm.destination_point, "country": itm.country, "loc": itm.loc,
                          "route_type": itm.route_type, "desc": itm.desc, "duration": itm.duration,
                          "event": event_result_list} for itm in route_result), content_type="application/json")


def route_reviews(request, route_id):
    result = models.Review.objects.all().filter(id_route=route_id)
    # Було закоментовано з метою тестування
    # return render(request, 'route_reviews.html', {'id_route': result[0].id_route, 'text': result[0].text,
    #                                               'rating': result[0].rating})
    return HttpResponse(
        json.dumps([{'Id route': itm.id_route, 'Text': itm.text, 'Rating': itm.rating} for itm in result]),
        content_type='application/json')


def route_add(request):
    if request.user.has_perm('Coffee_night.add_route'):
        if request.method == 'GET':
            return render(request, 'add_route.html')
        if request.method == 'POST':
            start_point = request.POST.get('start_point')
            destination_point = request.POST.get('destination_point')
            stop_points = request.POST.get('stop_points')
            country = request.POST.get('country')
            location = request.POST.get('loc')
            description = request.POST.get('desc')
            route_type = request.POST.get('route_type')
            duration = request.POST.get('duration')

            stop_points = json.dumps(stop_points)
            stop_list = json.loads(stop_points)
            with MongoDBConnection('admin', 'admin', '127.0.0.1') as db:
                collec = db['stop_points']
                id_stop_points = collec.insert_one({'points': stop_list}).inserted_id

            start_obj = models.Places.objects.get(name=start_point)
            dest_obj = models.Places.objects.get(name=destination_point)

            new_route = models.Route(start_point=start_obj.id, stop_point=id_stop_points, destination_point=dest_obj.id,
                                     country=country, loc=location, desc=description, route_type=route_type,
                                     duration=duration)

            new_route.full_clean()
            new_route.save()
        return HttpResponse('Route added successfully!')
    else:
        return HttpResponse('You have no permissions to add route', status=401)


def add_event(request, route_id):
    today_date = datetime.datetime.today().strftime('%Y-%m-%d')

    if request.user.has_perm('Coffee_night.add_event'):
        if request.method == 'GET':
            return render(request, 'add_event.html', {'start_date': today_date})

        if request.method == 'POST':
            event_date = request.POST.get('event_date')
            price = request.POST.get('price')
            # user = User.objects.get(username=request.user.username)

            new_event = models.Event(id_route=route_id, event_admin=1, event_users={}, start_data=event_date,
                                     price=price)
            try:
                new_event.full_clean()
                new_event.save()
            except ValidationError as e:
                return HttpResponse(f'Date error! {event_date}, {price}, {e}')

            return HttpResponse('Event added successfully!')
    else:
        return HttpResponse('You have no permissions to add event', status=401)


def event_handler(request, event_id):  # Інформація про івент
    # result = models.Event.objects.all().filter(id=event_id)
    cursor = connection.cursor()
    raw_query = f"""SELECT Coffee_night_event.id, start_point.name, destination_point.name,
                                   Coffee_night_route.duration, Coffee_night_event.event_admin, Coffee_night_event.event_users, 
                                   Coffee_night_event.start_data, Coffee_night_event.price
                                FROM Coffee_night_event 

                                JOIN Coffee_night_route ON Coffee_night_event.id_route = Coffee_night_route.id
                                JOIN Coffee_night_places as start_point
                                ON start_point.id = Coffee_night_route.start_point

                                JOIN Coffee_night_places as destination_point
                                ON destination_point.id = Coffee_night_route.destination_point

                                WHERE Coffee_night_event.id = {event_id}"""

    cursor.execute(raw_query)
    result = cursor.fetchone()
    cursor.close()

    with MongoDBConnection('admin', 'admin', '127.0.0.1') as db:
        collec = db['event_users']
        user_collection = collec.find_one({"_id": ObjectId(result[5])})

        user_approved = User.objects.filter(pk__in=user_collection['approved'])
        user_pending = User.objects.filter(pk__in=user_collection['pending'])
        list_approved = [{'id': itm.id, 'username': itm.username} for itm in user_approved]
        list_pending = [{'id': itm.id, 'username': itm.username} for itm in user_pending]

    return render(request, 'event_handler.html',
                  {'event_id': result[0], 'start_point': result[1], 'destination_point': result[2],
                   'duration': result[3], 'event_admin': result[4], 'approved_users': list_approved,
                   'pending_users': list_pending, 'start_data': result[6], 'price': result[7]})

    # return render(request, 'event_handler.html', {'event_id': result[0].id, 'start_point': result[0].start_point,
    #                                               'destination_point': result[0].destination_point,
    #                                               'duration': result[0].duration,
    #                                               'event_admin': result[0].event_admin,
    #                                               'approved_users': result[0].approved_users,
    #                                               'pending_users': result[0].pending_users,
    #                                               'start_data': result[0].start_data,
    #                                               'price': result[0].price})


def add_me_to_event(request, event_id):
    user = request.user.id
    event = models.Event.objects.filter(id=event_id).first()
    with MongoDBConnection('admin', 'admin', '127.0.0.1') as db:
        collec = db['event_users']
        all_event_users = collec.find_one({"_id": ObjectId(event.event_users)})
        if user in all_event_users['approved'] or user in all_event_users['pending']:
            return HttpResponse('You are already in this event')
        else:
            all_event_users['pending'].append(user)
            collec.update_one({"_id": ObjectId(event.event_users)}, {"$set": all_event_users})

    return redirect(f'http://127.0.0.1:8000/event/{event_id}')


def event_accept_user(request, event_id):
    event = models.Event.objects.filter(id=event_id).first()

    if request.user.has_perm('Coffee_night.change_event'):
        with MongoDBConnection('admin', 'admin', '127.0.0.1') as db:
            collec = db['event_users']
            user_collection = collec.find_one({"_id": ObjectId(event.event_users)})

            user_approved = User.objects.filter(pk__in=user_collection['approved'])
            user_pending = User.objects.filter(pk__in=user_collection['pending'])
            list_approved = [{'id': itm.id, 'username': itm.username} for itm in user_approved]
            list_pending = [{'id': itm.id, 'username': itm.username} for itm in user_pending]

        if request.method == 'GET':
            return render(request, 'event_accept_user.html', {'approved_users': list_approved,
                                                              'pending_users': list_pending})

        if request.method == 'POST':
            ac_user = int(request.POST.get('accepting_user'))
            with MongoDBConnection('admin', 'admin', '127.0.0.1') as db:
                collec = db['event_users']
                record = collec.find_one({"_id": ObjectId(event.event_users)})
                record['pending'].remove(ac_user)
                record['approved'].append(ac_user)
                collec.update_one({"_id": ObjectId(event.event_users)}, {"$set": record})
                return HttpResponse('User was accepted successfully!')
    return HttpResponse('You have no permissions to accept user')


def user_login(request):
    if not request.user.is_authenticated:
        if request.method == 'GET':
            return render(request, 'login.html')
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponse('User is logged in!')
            else:
                return HttpResponse('No user')
    else:
        return HttpResponse('<a href="logout">logout</a>')


def user_registration(request):
    if not request.user.is_authenticated:
        if request.method == 'GET':
            return render(request, 'registration.html')
        if request.method == 'POST':
            user = User.objects.create_user(username=request.POST.get('username'),
                                            password=request.POST.get('password'),
                                            email=request.POST.get('email'),
                                            first_name=request.POST.get('first_name'),
                                            last_name=request.POST.get('last_name'))
            user.save()
            return HttpResponse('User created successfully!')
    else:
        return HttpResponse('<a href="logout">logout</a>')


def user_logout(request):
    logout(request)
    return redirect('/login')
