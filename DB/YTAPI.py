from googleapiclient.discovery import build

api_key = '' # Insert Your own Google API Key
youtube = build('youtube', 'v3', developerKey=api_key)

def get_movie_trailer(movie_title):
    try:
        search_response = youtube.search().list(
            q=f'{movie_title} official trailer',
            part='id',
            type='video'
        ).execute()

        if 'items' in search_response and search_response['items']:
            video_id = search_response['items'][0]['id']['videoId']
            trailer_link = f'https://www.youtube.com/watch?v={video_id}'
            return trailer_link

    except Exception as e:
        print(f'Error getting trailer link: {e}')

    return None

