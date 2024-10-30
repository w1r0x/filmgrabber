import requests
import json
import math


class KPMovieNotFoundExc(BaseException):
    pass


class KPIndexNotFoundExc(BaseException):
    pass


class KPApi():

    api_key = None
    kinopoisk_dev_url = "https://api.kinopoisk.dev/v1.4"

    def __init__(self, api_key):
        self.api_key = api_key

    @staticmethod
    def _get_movie_object(kp_api_response):
        movie = dict()
        movie["id"] = kp_api_response["id"]
        movie["rating"] = math.ceil(float(kp_api_response["rating"]["kp"])*10)/10
        try:
            movie["imdbId"] = kp_api_response['externalId']['imdb']
        except KeyError:
            movie["imdbId"] = 0
        try:
            movie["trailer"] = kp_api_response["videos"]["trailers"][0]["url"]
        except (KeyError, IndexError):
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

    def find_movies_by_imdb_id(self, imdb_id: str | list):
        request = f"/movie?page=1&selectFields=id&selectFields=rating&selectFields=videos&selectFields=externalId"

        if type(imdb_id) is list:
            for i in imdb_id:
                request += f"&externalId.imdb={i}"
        elif type(imdb_id) is str:
            request += f"&externalId.imdb={imdb_id}"
        else:
            raise TypeError('Only str and list are supported for \'imdb_id\'')

        response = self._send(request)

        movies = None

        if type(imdb_id) is list:
            movies = response["docs"]
            new_movies = []
            for m in movies:
                new_movies.append(self._get_movie_object(m))
            return new_movies
        elif type(imdb_id) is str:
            try:
                movies = response["docs"][0]
            except (KeyError, IndexError):
                raise KPMovieNotFoundExc

            return self._get_movie_object(movies)

    @staticmethod
    def get_kp_index_from_kinopoisk_data(kp_data, imdb_id):
        index = 0
        for m in kp_data:
            if m['imdbId'] == imdb_id:
                return index
            index += 1
        raise KPIndexNotFoundExc

