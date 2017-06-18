import requests


_API_URL = 'http://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&APPID={}&units=metric'
_API_KEY = '54cc9216a94b82abc47203cbad41137f'
_BAD_WEATHER = ['Thunderstorm', 'Drizzle', 'Rain', 'Snow', 'Extreme']


class Weather(object):
    def __init__(self, lat, lon):
        self.data = requests.get(_API_URL .format(lat, lon, _API_KEY)).json()

        self.bad_weather = any(w['main'] in _BAD_WEATHER for w in self.data['weather'])
