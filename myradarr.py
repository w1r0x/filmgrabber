def find_movies(radarr, movie_name):
    movies = radarr.lookup_movie(movie_name)

    movies_array = []

    for m in movies:
        movie = {}
        movie['title'] = f"{m['title']} ({m['year']})"
        try:
          movie['image_url'] = m['images'][0]['remoteUrl']
        except KeyError:
            pass
        movie['overview'] = m['overview']
        movie['scores'] = ""
        if 'imdb' in m['ratings']:
            movie['scores'] += f"IMDB: {m['ratings']['imdb']['value']}"
        if 'tmdb' in m['ratings']:
            if len(movie['scores']) != 0: movie['scores'] += " "
            movie['scores'] += f"TMDB: {m['ratings']['tmdb']['value']}"
        if len(movie['scores']) == 0: del movie['scores']
        movie['tmdbId'] = m['tmdbId']
        movies_array.append(movie)

    return movies_array
