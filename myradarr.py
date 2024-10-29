from pyarr import RadarrAPI

class MyRadarr(RadarrAPI):

    last_found_movies = 0

    def __init__(self, host_url: str, api_key: str):
        super().__init__(host_url, api_key)

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
            movie['overview'] = m['overview']
            movie['scores'] = ""
            if 'imdb' in m['ratings']:
                movie['scores'] += f"IMDB: {m['ratings']['imdb']['value']}"
            else:
                # Skip movie if no IMDB rating
                continue
            if 'tmdb' in m['ratings']:
                if len(movie['scores']) != 0:
                    movie['scores'] += " "
                movie['scores'] += f"TMDB: {m['ratings']['tmdb']['value']}"
            else:
                # Skip movie if no TMDB rating
                continue
            if len(movie['scores']) == 0:
                del movie['scores']
            movie['tmdbId'] = m['tmdbId']
            movies_array.append(movie)

        movies_array = self._sort_movie_list(movies_array)

        self.last_found_movies = len(movies_array)

        movies_array = movies_array[:limit]

        return movies_array

    @staticmethod
    def _sort_movie_list(movies):
        sorted_movies = sorted(movies, key=lambda x: x['year'], reverse=True)
        return sorted_movies
