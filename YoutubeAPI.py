import os
from ytmusicapi import YTMusic
import yt_dlp
import sys



DONT_ALLOW = {'?','#','!','@','$','%','^','&','*'}


def get_data_folder():
    # path of your data in same folder of main .py or added using --add-data
    if getattr(sys, 'frozen', False):
        try:
            data_folder_path = sys._MEIPASS2
        except:
            data_folder_path = sys._MEIPASS
    else:
        data_folder_path = os.path.dirname(
            os.path.abspath(sys.modules['__main__'].__file__)
        )
    return data_folder_path


def is_downloaded(song_name):

    if not os.path.exists('liked_musics'):
        os.makedirs('liked_musics')
        
    for x in os.listdir('Liked_Musics'):

        if x.endswith(".mp3"):
            if x == song_name + '.mp3':
                return True
            
            else:
                continue

    return False
    

def is_correct_song(song_spotify,song_youtube):

    if song_spotify.rstrip() == song_youtube:
        return True
    else:
        return False
    


def download_playlist(total_songs):

    ydl_opts = youtube_options(True)

    #loop on all the songs
    for song_name in total_songs:

         #we will search for the songs
        link = search(song_name)

        temp_song_name = song_name[:song_name.rfind("by")]
        temp_song_name = temp_song_name.rstrip()
        temp_song_name = ''.join((filter(lambda i: i not in DONT_ALLOW,temp_song_name))) #REMOVE ALL THE UNWANTED CHARACTERS

        #download 1 by 1 
        ydl_opts['outtmpl'] = 'Liked_Musics' + '/' + temp_song_name +'.'+ '%(ext)s'

        #checks the file if already exits or not .. if it does not it will download it .... prevent repetition
        check = is_downloaded(temp_song_name)

        if not check:
            download_the_song(ydl_opts,link)

    #finishes
    return True


def youtube_options(is_playlist,song_name='temp'):

    if not is_playlist:
        ydl_opts = {
            'format': 'bestaudio',
            'outtmpl':  '/' + song_name + '.' + '%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [gui.hook],
            'ffmpeg_location' : get_data_folder()  + '/ffmpeg/',
            'overwrites' : False,
            'continuedl' : True
        }

    else:
        ydl_opts = {
            'format': 'bestaudio',
            'outtmpl':  'Liked_Musics' + '/' + song_name +'.'+ '%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [gui.hook],
            'ffmpeg_location' : get_data_folder()  + '/ffmpeg/',
            'overwrites' : False,
            'continuedl' : True
        }
        
    return ydl_opts



def search(song_name):

    search_results = YTMusic.search(self=YTMusic(),query=song_name, filter= 'songs', limit=1)

    if is_correct_song(song_name[:song_name.rfind("by")],search_results[0]['title']):
        print("Music was found ..")
        link = f"https://music.youtube.com/watch?v={search_results[0]['videoId']}"
        return link
    else:
        print("Sorry but did not find the correct music")


def set_GUI_object(root):
    global gui
    gui = root


def download_the_song(opts,link):

    ydl_opts = opts
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])