def find_movies(radarr, movie_name, no_poster_image_policy='ignore'):
    movies = radarr.lookup_movie(movie_name)

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
        if 'tmdb' in m['ratings']:
            if len(movie['scores']) != 0: movie['scores'] += " "
            movie['scores'] += f"TMDB: {m['ratings']['tmdb']['value']}"
        if len(movie['scores']) == 0:
            del movie['scores']
        movie['tmdbId'] = m['tmdbId']
        movies_array.append(movie)

    movies_array = sort_movie_list(movies_array)

    return movies_array


def sort_movie_list(movies):
    sorted_movies = sorted(movies, key=lambda x: x['year'], reverse=True)
    return sorted_movies
