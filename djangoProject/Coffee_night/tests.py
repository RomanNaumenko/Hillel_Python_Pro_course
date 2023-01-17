from django.contrib.auth.models import User
from django.test import TestCase, Client, RequestFactory
from Coffee_night.models import Review, Route, Event, Places
from Coffee_night.views import add_event, route_add, route_reviews, route_details
from unittest.mock import patch


class mockCollection():

    def find_one(self, *args, **kwargs):
        return {}


class MongoClientMock():

    def __init__(self, *args, **kwargs):
        pass

    def close(self):
        pass

    def __getitem__(self, item):
        return {'stop_points': mockCollection()}


class TestRoute(TestCase):

    def setUp(self):
        self.route = Route(start_point=1, stop_point='[{"name": "test", "lat": 1, "lon": 1}]',
                           destination_point=2, country='test', loc='test', desc='test',
                           route_type='Hiking', duration=3)
        self.review = Review(id_route=1, text='test', rating=5)
        self.event = Event(id_route=1, event_admin=1, event_users='[{"id": 1, "name": "test"}]',
                           start_data='2022-11-15',
                           price=100)
        self.places = Places(name='Kiev')
        self.places.save()
        self.places = Places(name='Lviv')
        self.places.save()
        self.review.save()
        self.route.save()
        self.event.save()

        self.factory = RequestFactory()

        class UserMock:
            def has_perm(self, *args, **kwargs):
                return True

        self.user = UserMock()

    def test_get_reviews(self):
        client = Client()
        response = client.get('/route/1/reviews')
        self.assertEqual(200, response.status_code)

    def test_get_route_filter(self):
        client = Client()
        response = client.get('/route/Hiking/test/test')
        self.assertEqual(200, response.status_code)

    def test_get_add_route(self):
        client = Client()
        response = client.get('/route/add_route')
        self.assertEqual(401, response.status_code)

    def test_post_add_route(self):
        client_1 = Client()
        no_perm_response = client_1.post('/route/add_route', {"start_point": "Kiev", "destination_point": "Lviv",
                                                              "stop_points": [
                                                                  {"name": "19e6f971-c1d4-4d96-b86a-60002436f413",
                                                                   "lat": 0.030466168438307517,
                                                                   "lon": 0.8171442672723339},
                                                                  {"name": "ce7ddb39-748b-4d9f-afcc-923afab528ed",
                                                                   "lat": 0.024848575173332166,
                                                                   "lon": 0.9296349572111213}],
                                                              "country": "test_country",
                                                              "loc": "test_loc", "desc": "test_desc",
                                                              "route_type": "CAMPING",
                                                              "duration": 3})
        print(no_perm_response.content)
        self.assertEqual(401, no_perm_response.status_code)

        request = self.factory.post('/route/add_route', {"start_point": "Kiev", "destination_point": "Lviv",
                                                         "stop_points": [
                                                             {"name": "19e6f971-c1d4-4d96-b86a-60002436f413",
                                                              "lat": 0.030466168438307517,
                                                              "lon": 0.8171442672723339},
                                                             {"name": "ce7ddb39-748b-4d9f-afcc-923afab528ed",
                                                              "lat": 0.024848575173332166,
                                                              "lon": 0.9296349572111213}],
                                                         "country": "test_country",
                                                         "loc": "test_loc", "desc": "test_desc",
                                                         "route_type": "CAMPING",
                                                         "duration": 3})
        request.user = self.user
        yes_perm_response = route_add(request)  # [{}] - stop_points
        print(yes_perm_response.content)
        self.assertEqual(200, yes_perm_response.status_code)


class TestEvent(TestCase):

    def test_anonymous_user(self):
        client = Client()
        response = client.get('/route/1/add_event')
        self.assertEqual(401, response.status_code)

        response = client.post('/route/1/add_event')
        self.assertEqual(401, response.status_code)

    def setUp(self):
        self.factory = RequestFactory()

        class UserMock:
            def has_perm(self, *args, **kwargs):
                return True

        self.user = UserMock()
        # self.user = User.objects.create_user(username='test', email='test123@gmail.com', password='test')

    def test_with_user(self):
        request = self.factory.post('/route/2/add_event', {"event_date": "2022-11-14", "price": 1000})
        request.user = self.user
        response = add_event(request, route_id=2)
        self.assertEqual(200, response.status_code)


class TestRouteReviewWithFixtures(TestCase):
    fixtures = ["reviews.json"]  # Створення тестових даних для тестування функції route_reviews

    def test_data_receiving(self):  # Тестування функції route_reviews
        resp = self.client.post('/route/3/reviews')
        parsed_resp = resp.json()
        self.assertEqual("Could be better", parsed_resp[1]["Text"])
        print(parsed_resp)


class RouteDetailsTest(TestCase):
    fixtures = ["route.json"]

    def setUp(self) -> None:
        self.factory = RequestFactory()

    @patch("mongo_utils.MongoClient", MongoClientMock)
    def test_route_details_post(self):
        request = self.factory.post('/route/1', data={"id": 1})
        response = route_details(request, id=1)

