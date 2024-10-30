from pyarr import RadarrAPI
from kpapi import *


class MyRadarr(RadarrAPI):

    last_found_movies = 0
    kpapi = None

    def __init__(self, host_url: str, api_key: str, kp_api_key):
        super().__init__(host_url, api_key)
        self.kpapi = KPApi(api_key=kp_api_key)

    def find_movies(self, movie_name, no_poster_image_policy='ignore', limit=5):
        movies = self.lookup_movie(movie_name)

        movies_array = []

        for m in movies:
            movie = dict()
            movie['title'] = f"{m['title']} ({m['year']})"
            movie['year'] = m['year']
            # TODO: Make image placeholder for no image movies or just not include this
            try:
                movie['image_url'] = m['images'][0]['remoteUrl']
            except (KeyError, IndexError):
                if no_poster_image_policy == 'ignore':
                    continue
                else:
                    pass
            movie['overview'] = m['overview']
            movie['scores'] = ""
            if 'imdb' in m['ratings']:
                movie['scores'] += f"IMDB: {m['ratings']['imdb']['value']}"
            if 'tmdb' in m['ratings']:
                if len(movie['scores']) != 0:
                    movie['scores'] += " "
                movie['scores'] += f"TMDB: {m['ratings']['tmdb']['value']}"
            if len(movie['scores']) == 0:
                del movie['scores']
            movie['tmdbId'] = m['tmdbId']
            movie['imdbId'] = m['imdbId']
            movies_array.append(movie)

        movies_array = self._sort_movie_list(movies_array)
        # Limit movies list to 'limit' var
        movies_array = movies_array[:limit]

        self.last_found_movies = len(movies_array)

        movies_array = self.populate_kinopoisk_data(movies_array)

        return movies_array

    def populate_kinopoisk_data(self, movies_array):
        imdbs = []
        for m in movies_array:
            imdbs.append(m['imdbId'])

        # TODO: Maybe should do using original movie name + year

        kp_info = self.kpapi.find_movies_by_imdb_id(imdbs)

        new_movies_array = []
        for m in movies_array:
            try:
                kp_info_id = self.kpapi.get_kp_index_from_kinopoisk_data(kp_info, m['imdbId'])
            except KPIndexNotFoundExc:
                new_movies_array.append(m)
                continue

            m['scores'] += f"\nKinopoisk: {kp_info[kp_info_id]['rating']}"
            try:
                m['trailer'] = kp_info[kp_info_id]['trailer']
            except KeyError:
                pass
            m['kpId'] = kp_info[kp_info_id]['id']

            new_movies_array.append(m)

        return new_movies_array

    @staticmethod
    def _sort_movie_list(movies):
        sorted_movies = sorted(movies, key=lambda x: x['year'], reverse=True)
        return sorted_movies
