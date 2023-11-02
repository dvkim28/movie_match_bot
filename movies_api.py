import requests

current_page = 1
movies_per_page = 20
movies_count = 0

def get_movie_data():
    global current_page
    global movies_count
    url = "https://api.themoviedb.org/3/discover/movie"
    params = {
        "include_adult": "false",
        "include_video": "false",
        "language": "ru-RU",
        "page": current_page,
        "sort_by": "popularity.desc",
    }
    headers = {
        "Accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJmNWZjNDNiMDdjYjllMzFmYWEwMWFmOWNiZjUwODQyZiIsInN1YiI6IjY1MWViZDhjYTA5N2RjMDExZDAzOWFhYiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.AqCC7OJRVyOBXY1MJf4JfKzhL9a_UOgvOcuQsrpWoks"
    }

    response = requests.get(url, params=params, headers=headers)
    movies_game = []
    if response.status_code == 200:
        data = response.json()
        movies = data.get("results", [])
        if movies:
            for movie in movies:
                # Ваш код для обработки фильмов
                movies_game.append(movie)
                movies_count += 1

            if movies_count >= movies_per_page:
                current_page += 1
                movies_count = 0
        else:
            current_page += 1
            movies_count = 0

    else:
        print("Failed to retrieve data. Status code:", response.status_code)
    return movies_game

# Вызов функции для получения фильмов
get_movie_data()
