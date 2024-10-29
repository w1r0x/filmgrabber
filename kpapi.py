import requests
import json

class KPMovieNotFoundExc:
    pass

class KPApi:

    api_key = None
    kinopoisk_dev_url = "https://api.kinopoisk.dev/v1.4"

    def __init__(self, api_key):
        self.api_key = api_key

    @staticmethod
    def _get_movie_object(kp_api_response):
        movie = dict()
        movie["id"] = kp_api_response["id"]
        movie["rating"] = kp_api_response["rating"]["kp"]
        try:
            movie["trailer"] = kp_api_response["videos"]["trailers"][0]["url"]
        except KeyError:
            pass

        return movie

    def _send(self, request):
        req = self.kinopoisk_dev_url
        req += request

        headers = {
            "accept": "application/json",
            "X-API-KEY": self.api_key
        }

        response = requests.get(req, headers=headers)

        # TODO: make exception on invalid API key and other errors
        return json.loads(response.text)

    def find_movie_by_imdb_id(self, imdb_id):
        request = f"/movie?page=1&limit=1&selectFields=id&selectFields=rating&selectFields=videos&externalId.imdb={imdb_id}"

        response = self._send(request)

        try:
            movie = response["docs"][0]
        except KeyError:
            raise KPMovieNotFoundExc

        return self._get_movie_object(movie)
