import requests as r


class GeocodingError(BaseException):
    pass


class Geocoder:

    def get_coords(self, address):
        resp = r.get("https://geocode-maps.yandex.ru/1.x",
                     {"format": "json",
                      "apikey": "31f3f104-ed92-4851-905a-59a0ca77d0fe",
                      "geocode": address})
        if resp.status_code == 200:
            resp = resp.json()
            if resp['response']:
                position = resp['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
                position = [float(coord) for coord in position.split()[::-1]]
                return position
        else:
            raise GeocodingError("Can't geocode this address")
