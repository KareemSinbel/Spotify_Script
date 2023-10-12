import spotipy
import YoutubeAPI

def search(sp,search_song):
    spotify = spotipy.Spotify(auth= sp)
    if 'open.spotify.com' in search_song:


            results = spotify.track(search_song)   

            artist_names_list = results['album']['artists']
            song_name = results['name']

            full_song_name = song_name

            if len(artist_names_list) > 0:
                x = 0
                for names in artist_names_list:
                    if x == 0:
                        full_song_name += ' ' + 'by '+ names['name']

                    elif x == len(artist_names_list):
                         full_song_name += names['name']
                    else:
                         full_song_name += ', '+ names['name']
                    x = x + 1


            YoutubeAPI.main(full_song_name)

        
    elif 'youtube' in search_song:
        YoutubeAPI.play_The_Song(search_song)

    else:
        
        YoutubeAPI.main(search_song)



def liked_musics(token):

    offset = 0

    #limit = 20                        MAXIMUM LIMIT ..... REMOVE Y AND MAKE LIMIT = 20 TO RETREIVE ALL THE SONGS IN THE LIBRARY
    limit = 1
    total_liked_songs = []
    spotify = spotipy.Spotify(auth= token)
    results = spotify.current_user_saved_tracks(limit,offset)

    #DEBUG
    y = 0
    
    while len(results['items']) > 0:

        for idx, item in enumerate(results['items']):

            track = item['track']
            song_name = track['name']
            artist_names_list = track['album']['artists']
            full_song_name = song_name
            if len(artist_names_list) > 0:
                x = 0
                for names in artist_names_list:
                    if x == 0:
                        full_song_name += ' ' + 'by '+ names['name']

                    elif x == len(artist_names_list):
                        full_song_name += names['name']
                    else:
                        full_song_name += ', '+ names['name']
                    x = x + 1

            total_liked_songs.append(full_song_name)
        
        offset += limit
        results = spotify.current_user_saved_tracks(limit,offset)

        y = y + 1

        if y == 5:
            break
        
    return total_liked_songs


def download_playlist(total_liked_songs):

    if YoutubeAPI.download_playlist(total_liked_songs):
        return True
    else:
        return False