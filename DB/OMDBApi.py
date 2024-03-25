import requests
from PIL import Image
from io import BytesIO
from datetime import datetime, date

key = ''  # Insert Your OMDB API key


def get_movie_info(title):
    base_url = "http://www.omdbapi.com/"
    params = {
        "apikey": key,  
        "t": title,
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        if data["Response"] == "True":

            poster_url = data.get("Poster", "")
            if poster_url.lower() == "n/a":
                print("Error: Poster not available.")
                return None

            time = data.get("Released", "")
            if time.lower()  != "n/a":
                time = datetime.strptime(data.get("Released", ""), "%d %b %Y")
            else:
                time = date.today()

            movie_info = [
                data.get("imdbID", ""),
                data.get("Title", ""),
                transform_duration_to_mysql_time(data.get("Runtime", "")),
                time,
                data.get("Genre", ""),
                ", ".join(data.get("Actors", "").split(",")[:2]),
                poster_url,
                data.get("imdbRating", ""),
                data.get("Plot", ""),
                data.get("Rated", "")
            ]
            return movie_info
        else:
            print(f"Error: {data['Error']}")
    else:
        print(f"Error: {response.status_code}")


def get_movie_info_by_imdb_id(imdb_id):
    base_url = "http://www.omdbapi.com/"
    params = {
        "apikey": key, 
        "i": imdb_id,
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        if data["Response"] == "True":

            poster_url = data.get("Poster", "")
            if poster_url.lower() == "n/a":
                print("Error: Poster not available.")
                return None
            time = data.get("Released", "")
            if time.lower()  != "n/a":
                time = datetime.strptime(data.get("Released", ""), "%d %b %Y")
            else:
                time = date.today()

            movie_info = [
                data.get("imdbID", ""),
                data.get("Title", ""),
                transform_duration_to_mysql_time(data.get("Runtime", "")),
                time,
                data.get("Genre", ""),
                ", ".join(data.get("Actors", "").split(",")[:2]),
                poster_url,
                data.get("imdbRating", ""),
                data.get("Plot", ""),
                data.get("Rated", "")
            ]
            return movie_info
        else:
            print(f"Error: {data['Error']}")
    else:
        print(f"Error: {response.status_code}")


def save_movie_poster(poster_url, file_name):
    response = requests.get(poster_url)
    if response.status_code == 200:
        with open(file_name, 'wb') as file:
            file.write(response.content)
        print(f"Poster saved as {file_name}")
    else:
        print(f"Error retrieving poster: {response.status_code}")


def display_movie_poster(poster_url):
    response = requests.get(poster_url)
    if response.status_code == 200:
        img = Image.open(BytesIO(response.content))
        img.show()
    else:
        print(f"Error retrieving poster: {response.status_code}")


def transform_duration_to_mysql_time(duration):
    # Extract numeric part (the minutes)
    try:
        minutes = int(''.join(filter(str.isdigit, duration)))
    except ValueError:
        print(
            f"Error: Unable to extract numeric part from duration: {duration}")
        return None

    # Convert total minutes to hours and minutes
    hours_part = minutes // 60
    minutes_part = minutes % 60

    # Format the result as a string in the format hh:mm:ss
    result = f"{hours_part:02d}:{minutes_part:02d}:00"

    return result



