class MapConstructor:

    def construct_map(self, points):
        url = "https://static-maps.yandex.ru/1.x/?"
        params = {
            "ll": '37.620070,55.753630',
            "size": "650,350",
            "l": "map",
            "z": "9",
            "pt": "~".join([f"{points[i][1]},{points[i][0]},pm2dgm{i+1}" for i in range(len(points))])
        }
        url += "&".join([f"{key}={value}"for key, value in params.items()])
        return url
