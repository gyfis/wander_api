import requests

_API_URL = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?rankby=distance&location={},{}&type={}&key={}'
_PHOTO_API_URL = 'https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photoreference={}&key={}'
_API_KEY = 'AIzaSyDLMTMXziGlVNonM5qY2G8Ntwd0YTaqqcE'

_GOOD_WEATHER_PLACE_TYPES = 'art_gallery, bar, cafe, church, events, library, museum, park, restaurant, zoo'.split(', ')
_BAD_WEATHER_PLACE_TYPES = 'art_gallery, bar, cafe, church, events, library, museum, restaurant'.split(', ')

_AVERAGE_TIMES = {
    'art_gallery': 1,
    'bar': 0.75,
    'cafe': 0.5,
    'church': 0.35,
    'events': 1.0,
    'library': 0.5,
    'museum': 1.5,
    'park': 0.75,
    'restaurant': 1.5,
    'zoo': 2.0
}

_AVERAGE_TIMES = {k: h for (k, h) in _AVERAGE_TIMES.items()}


def fetch_photo_url(place):
    if not place.get('photos', None):
        return None

    return _PHOTO_API_URL.format(place['photos'][0]['photo_reference'], _API_KEY)


class Places(object):
    def __init__(self, lat, lon, bad_weather):
        self.bad_weather = bad_weather

        nearby_search = {}

        place_types = _BAD_WEATHER_PLACE_TYPES if bad_weather else _GOOD_WEATHER_PLACE_TYPES

        # TODO paralelize the requests
        for place_type in place_types:
            data = requests.get(_API_URL.format(lat, lon, place_type, _API_KEY)).json()
            places = data['results']

            # Filter for open places only
            filtered_places = []
            for place in places:
                if not place.get('opening_hours', None) or place['opening_hours']['open_now']:
                    filtered_places.append({**place, 'place_type': place_type})

            nearby_search[place_type] = filtered_places

        self.results = nearby_search

    def data(self):
        places_data = self.results.items()
        place_durations = [_AVERAGE_TIMES[p[0]] for p in places_data for _ in p[1]]
        places = [pi for p in places_data for pi in p[1]]

        return places, place_durations, [(result['geometry']['location']['lng'], result['geometry']['location']['lat']) for result in places]

    def filter(self, type_filter):
        place_types = _BAD_WEATHER_PLACE_TYPES if self.bad_weather else _GOOD_WEATHER_PLACE_TYPES

        for filtered_type in place_types:
            if filtered_type not in type_filter:
                self.results.pop(filtered_type, None)
