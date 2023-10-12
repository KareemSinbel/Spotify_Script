import customtkinter as CTK
import spotipy
import os
from spotipy import SpotifyPKCE
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from subprocess import CREATE_NO_WINDOW
import Spotify_Commands
import threading
import YoutubeAPI

try:
  client_id = os.environ['SPOTIPY_CLIENT_ID']
  redirect_uri = os.environ['SPOTIPY_REDIRECT_URI']
except:
  client_id = os.environ['SPOTIPY_CLIENT_ID'] = 'SPOTIFY_CLIENT_ID'
  redirect_uri = os.environ['SPOTIPY_REDIRECT_URI'] = 'https://www.google.com/'

spotify_oauth = SpotifyPKCE(client_id=client_id, redirect_uri=redirect_uri, scope="user-library-read",open_browser=True)
spotify = spotipy.Spotify(oauth_manager=spotify_oauth)

#TO LOCK THREADS FROM EXECUTING THE SAME FUCNTION ......... preventing creatings many threads from running the same function
lock = threading.Lock()


class gui:


    def __init__(self, master):

        self.GUI = master
        YoutubeAPI.set_GUI_object(self)

        font = CTK.CTkFont(family='Cascadia Mono',size=26,weight='bold')
        self.frame = CTK.CTkFrame(master= self.GUI,fg_color=window_color)

        self.user_name_text = CTK.StringVar()
        self.user_name_text.set("Welcome")
        self.user_name_label = CTK.CTkLabel(master= self.frame, textvariable= self.user_name_text,font = font)
        self.user_name_label.pack()
        self.frame.place(relx=0.5, rely=0.5, relwidth=0.5, relheight=0.5, anchor="c")

        #Function Logics
        self.check_validation()



    #check if the user signed in before or not (CACHED FILE) .. if not it will ask for login!
    def check_validation(self):

        if not spotify_oauth.validate_token(spotify_oauth.get_cached_token()):
            auth_url = spotify_oauth.get_authorize_url()
            self.login_page(auth_url,False)
        else:
            self.login_page("",True)
            self.user_name_text.set(spotify.current_user()['display_name'])
            access_token = spotify_oauth.validate_token(spotify_oauth.get_cached_token())['access_token']
            self.download_page(access_token)
            self.signout_page()



    def login_page(self,auth_url,destroy=False):

        login_button = CTK.CTkButton(master= self.frame, text='Login', command = lambda: threading.Thread(daemon=True,name= 'loginThread',target= self.open_web_browser,args=(auth_url,)).start())
        login_button.pack(after=self.user_name_label,pady=50)
        # if destroy:
        #     login_button.destroy()


    def open_web_browser(self,url):

        global driver
        if threading.active_count() > 2:
            pass

        else:

            lock.acquire()

            #Disable the button for no more clicks which leads to create many THREADS!
            #event = threading.Event()
            #login_button.configure(state='disabled')

            options = webdriver.ChromeOptions()
            options.add_argument('--log-level=3')
            #options.add_argument("start-maximized")
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            options.add_experimental_option("useAutomationExtension", False)
            options.add_experimental_option("excludeSwitches",["enable-automation"])
            #chrome_service = ChromeService(executable_path ='.\driver\chromedriver.exe')
            #chrome_service.creation_flags = CREATE_NO_WINDOW
            #driver = webdriver.Chrome(service=chrome_service,options=options)
            driver = webdriver.Chrome(options=options)
            driver.get(url)

            try :
                while True:

                    get_url = driver.current_url

                    if 'https://www.google.com/?code=' in get_url:

                        code = spotify_oauth.parse_response_code(get_url)
                        spotify_oauth.get_access_token(code)

                        self.check_validation()

                        driver.close()

                        break
            except:
                self.check_validation()

            lock.release()  


    def download_page(self,access_token):
        global download_button
        download_button = CTK.CTkButton(master= self.frame, text='Download', command = lambda : threading.Thread(name= 'downloadThread',target=self.download_liked,args=(access_token,)).start())
        download_button.pack(after=self.user_name_label,pady=50)


    def download_liked(self,access_token):

        
        #self.percentage_bar()

        #disabling the signout button while the download under process , disabling download button to not spamm on downloading
        self.signout_btn.configure(state="disabled")
        download_button.configure(state="disabled")


        data = Spotify_Commands.liked_musics(access_token)

        #still_running = threading.Thread(name= 'percent',target= Spotify_Commands.download_playlist,args=(data,)).start()

        #print(len(data))
        self.still_running =  Spotify_Commands.download_playlist(data)

        download_button.configure(state="normal")
        self.signout_btn.configure(state="normal")
        #destroying the label and the bar after the download finished ... EVEN IF IT IS A LIST
        try:
            self.progress_bar.destroy()
            self.percentage_label.destroy()
        except:
            pass





    def percentage_bar(self):

        try:
            #Checks if the widgets are exist or not
            if self.percentage_label.winfo_exists() == True:
                pass
            # else:
            #     self.percentage_label.destroy()
            #     self.progress_bar.destroy()

        except:

            self.percentage_label = CTK.CTkLabel(self.GUI,text="0%")
            self.percentage_label.pack(after = download_button)

            self.progress_bar = CTK.CTkProgressBar(self.GUI,width=400)
            self.progress_bar.set(0)
            self.progress_bar.pack(after = self.percentage_label,pady= 20)




    def update_progress_bar(self,percentage = "0%",progress = 0):

        try:
            if self.percentage_label.winfo_exists() == True:

                # self.percentage_label = CTK.CTkLabel(self.GUI,text=percentage)

                # self.progress_bar = CTK.CTkProgressBar(self.GUI,width=400)
                # self.progress_bar.set(float(progress)/100)

                # self.percentage_label.pack(after = download_button)
                # self.progress_bar.pack(after = self.percentage_label,pady= 20)

                self.percentage_label.configure(text=percentage)
                self.progress_bar.set(float(progress)/100)
            # else:
            #     self.percentage_label.destroy()
            #     self.progress_bar.destroy()
        
        except:

            self.percentage_bar()

  


    def hook(self,hook_data):

        if hook_data['status'] == 'downloading':
            #print(hook_data)
            total_file_size = hook_data['total_bytes']
            bytes_downloaded = hook_data['downloaded_bytes']
            percentage_now = (bytes_downloaded / total_file_size) * 100
            per = str(int(percentage_now))
            self.update_progress_bar(percentage = per + "%", progress= percentage_now)

        if hook_data['status'] == 'finished':

            self.update_progress_bar()
            filename=hook_data['info_dict']['title']


    def signout_page(self):

        self.signout_btn = CTK.CTkButton(master= self.GUI, text='Sign Out',command= self.signout)
        self.signout_btn.pack(side="bottom",pady=15)


    def signout(self):

        if os.path.exists(spotify_oauth.cache_handler.cache_path):
            os.remove(spotify_oauth.cache_handler.cache_path)

        self.signout_btn.destroy()
        self.check_validation()
        self.user_name_text.set("Welcome")

        
                




#if closed the main program closes the BROWSER ALSO
def close_main_win():
    
    try:
        driver.close()
    except:
        pass

    root.destroy()




if __name__ == "__main__":

    root = CTK.CTk()
    root.title("EyeOT")
    root._set_appearance_mode("System")

    #Get the resolution of the PC and customize it to build GUI window
    window_width = root.winfo_screenwidth()*0.45
    window_height = root.winfo_screenheight()*0.42
    window_color = root._fg_color

    root.update_idletasks()
    root.geometry(str(int(window_width)) + "x" + str(int(window_height)))
    root.resizable(False,False)

    #frame.place(x= (window_width*0.5) - (frame.winfo_reqwidth()/2), y= (window_height*0.45) - (frame.winfo_reqheight()/2),)

    #BEING CALLED WHEN MAIN WINDOW IS GETTING CLOSED, For cloing the browser
    root.wm_protocol("WM_DELETE_WINDOW",close_main_win)

    gui(master=  root)
    root.mainloop()
