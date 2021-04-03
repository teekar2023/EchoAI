#  Copyright © 2021 <Sreekar Palla>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
#  documentation files (the “Software”), to deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
#  permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
#  Software.
#
#  THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
#  WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
#  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
import ctypes
import json
import logging
import pickle
import random
import re
import subprocess
import time
import urllib
import webbrowser
from datetime import date
from threading import Thread
from tkinter.filedialog import *
from tkinter.messagebox import *
from tkinter.simpledialog import *

import nltk
import numpy as np
import pyautogui as gui
import pyttsx3
import requests
import speech_recognition as sr
import wikipedia
import wolframalpha
from keras.models import load_model
from nltk import WordNetLemmatizer

lemmatizer = WordNetLemmatizer()
model = load_model('EchoAI_model.h5')
intents = json.loads(open('intents.json').read())
words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))


def setup():
    logging.info("Setup Started")
    setup_window = Toplevel(root)
    setup_window.title("Setup")
    setup_window.geometry("500x250")
    setup_window.resizable(width=False, height=False)
    setup_text = Label(setup_window,
                       text="Please Fill Out The Following Fields To Use EchoAI! All This Data Stays On Your Device!")
    setup_text.pack(pady=10)
    name_input = Entry(setup_window, width=450)
    name_input.pack()
    name_input.insert(0, "NAME")
    nickname_input = Entry(setup_window, width=450)
    nickname_input.pack()
    nickname_input.insert(0, "NICKNAME")
    phone_number_input = Entry(setup_window, width=450)
    phone_number_input.pack()
    phone_number_input.insert(0, "PHONE NUMBER")
    email_address_input = Entry(setup_window, width=450)
    email_address_input.pack()
    email_address_input.insert(0, "EMAIL ADDRESS")
    home_address_input = Entry(setup_window, width=450)
    home_address_input.pack()
    home_address_input.insert(0, "HOME ADDRESS")
    weather_city_input = Entry(setup_window, width=450)
    weather_city_input.pack()
    weather_city_input.insert(0, "CITY FOR WEATHER FORECAST")
    variable = StringVar(setup_window)
    variable.set("Select Voice Gender")
    voice_gender_input = OptionMenu(setup_window, variable, "Select Voice Gender", "Male", "Female")
    voice_gender_input.config(width=450)
    voice_gender_input.pack()
    variable_two = StringVar(setup_window)
    variable_two.set("Select Measurement Units")
    units_input = OptionMenu(setup_window, variable_two, "Select Measurement Units", "Imperial", "Metric")
    units_input.config(width=450)
    units_input.pack()
    var = IntVar()
    submit_button = Button(setup_window,
                           command=lambda: var.set(1),
                           font=("TrebuchetMS", 10, 'bold'),
                           text="Click Here To Submit And Continue!", width="400", height="5",
                           bd=0, bg="#32de97", activebackground="#3c9d9b", fg='#ffffff')
    submit_button.pack()
    submit_button.wait_variable(var)
    data_file = open(f"{current_directory}\\Data\\UserData.json", "w")
    settings_file = open(f"{current_directory}\\Data\\settings.json", "w")
    name = name_input.get()
    nickname = nickname_input.get()
    phone_number = phone_number_input.get()
    email_address = email_address_input.get()
    home_address = home_address_input.get()
    weather_city = weather_city_input.get()
    voice_gender = variable.get()
    units = variable_two.get()
    if not ((not ((name == "") or (nickname == "") or (phone_number == "") or (
            email_address == "") or (home_address == "") or (weather_city == "") or (
                          voice_gender == "Select Voice Gender") or name.isspace() or nickname.isspace() or phone_number.isspace()) and not
             email_address.isspace()) and not home_address.isspace() and not weather_city.isspace()) or variable_two == "Select Measurement Units":
        showerror(title="Setup",
                  message="You Have Not Filled Everything Out Properly! Setup Will Now Exit And You Will Have To Restart!")
        setup_window.destroy()
        setup()
    else:
        if voice_gender.upper() == "MALE":
            gender = 0
        else:
            gender = 1
        logging.info("Saving Settings Data in Setup")
        settings = {
            "weather_city": f"{weather_city}",
            "units": f"{units}",
            "voice_gender": f"{str(gender)}",
            "volume": "1.0"
        }
        settings_object = json.dumps(settings, indent=4)
        with settings_file as outfile:
            outfile.write(settings_object)
        logging.info("Saved Settings Data In Setup")
        logging.info("Saving User Data In Setup")
        data = {
            "name": f"{name}",
            "nickname": f"{nickname}",
            "phone_number": f"{phone_number}",
            "email_address": f"{email_address}",
            "home_address": f"{home_address}",
        }
        data_object = json.dumps(data, indent=4)
        with data_file as outfile:
            outfile.write(data_object)
        logging.info("Saved User Data In Setup")
        settings_file.close()
        data_file.close()
        showinfo(title="Setup", message="Setup Completed! Please Restart!")
        restart_echo()


def reset_echo():
    reset_confirmation = askyesno(title="Reset", message="Are You Sure You Want To Reset EchoAI?")
    if reset_confirmation:
        logging.warning("Resetting EchoAI")
        setting_file = open(f"{current_directory}\\Data\\settings.json", "r+")
        setting_file.truncate()
        setting_file.close()
        user_data_file = open(f"{current_directory}\\Data\\UserData.json", "r+")
        user_data_file.truncate()
        user_data_file.close()
        logging.warning("Reset Finished")
        showinfo(title="Reset",
                 message=f"Reset Successfully Completed! Restart EchoAI To Setup And Use Again!")
        restart_echo()
    else:
        showinfo(title="Reset", message="Reset Aborted!")
        echo_input()


def open_website():
    logging.info("Opening Github Page")
    webbrowser.open("https://github.com/teekar2023/EchoAI")


def bug_report():
    logging.info("Bug Report Process Starting")
    showinfo(title="Bug Report",
             message="This Might Require A GitHub Account! If You Do not Have One And Don't Want To Make One, You Can "
                     "Email Me At sree23palla@outlook.com")
    showinfo(title="Bug Report",
             message=f"Please Attach The Following Log File Into The Bug Report! Path To Log File: {current_directory}\\app.log")
    webbrowser.open("https://github.com/teekar2023/EchoAI/issues/new")


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def update_echo():  # TODO Use Threading
    url = "http://github.com/teekar2023/EchoAI/releases/latest/"
    r = requests.get(url, allow_redirects=True)
    redirected_url = r.url
    if redirected_url != "https://github.com/teekar2023/EchoAI/releases/tag/v1.6.0":
        logging.warning("Newer Version Available! Current Version: 1.6.0")
        new_url = str(redirected_url) + "/EchoAI.Setup.exe"
        download_url = new_url.replace("tag", "download")
        update_window = Toplevel(root)
        update_window.title("Update EchoAI")
        update_window.geometry("500x500")
        update_window.resizable(width=False, height=False)
        update_text = Label(update_window,
                            text="There Is A New Update Available! Click The Button Below If You Wish To Download It!")
        update_text.pack()
        int_var = IntVar(update_window)
        update_button = Button(update_window, command=lambda: int_var.set(1), font=("TrebuchetMS", 12, 'bold'),
                               text="Download Update", width="500", height="10",
                               bd=0, bg="#32de97", activebackground="#3c9d9b", fg='#ffffff')
        update_button.pack()
        changelog_text = Label(update_window, text="Changelog Will Soon Show Up Here!")
        changelog_text.pack()
        update_button.wait_variable(int_var)
        if is_admin():
            f = asksaveasfile(mode='wb')
            if f is None:
                return
            else:
                ChatLog.insert(END, "DOWNLOADING UPDATE INSTALLER...\n")
                ChatLog.insert(END, "PLEASE DO NOT CLOSE ECHOAI AT THIS TIME...\n")
                ChatLog.insert(END, "ECHOAI WILL ALERT YOU ONCE DOWNLOADED...\n")
                ChatLog.insert(END, "PLEASE BE PATIENT...\n")
                ChatLog.insert(END, "ECHOAI WILL BE UNUSABLE AT THIS TIME...\n")
                ChatLog.insert(END, "PLEASE SUBMIT A BUG REPORT IF ANYTHING GOES WRONG...")
                showwarning(title="Update",
                            message="EchoAI Will Alert You Once The Update Is Downloaded And Will Not Respond During "
                                    "The Download! Please Do Not Interrupt The Download Process!")
                logging.info("Downloading Update Installer")
                root.title("ECHOAI - DOWNLOADING UPDATE")
                f2 = urllib.request.urlopen(download_url)
                while True:
                    data = f2.read()
                    if not data:
                        break
                    else:
                        pass
                    f.write(data)
                logging.info("Finished Downloading Update Installer")
                root.title("EchoAI")
                install_confirmation = askyesno(title="Update", message=f"Update Completed! Would You Like To Install?")
                if install_confirmation:
                    file_string = str(f)
                    installed_file1 = file_string.replace("<_io.BufferedWriter name='", "")
                    installed_file2 = installed_file1.replace("'>", "")
                    f.close()
                    subprocess.call(f"{installed_file2}")
                    exit()
                else:
                    return
        else:
            ask_admin = askyesno(title="Update", message="Escalated Privileges Are Required To Download Files! Click "
                                                         "'YES' To Restart As Admin Or 'NO' To Download From Web "
                                                         "Browser!")
            if ask_admin:
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
                exit_echo_no_confirm()
            else:
                webbrowser.open(download_url)
                exit_echo()
    else:
        showinfo(title="Update", message="There Is No New Update Available!")
        logging.info("No New Update Available")
        echo_input()


def save_conversation():
    conversation = ChatLog.get("1.0", 'end-1c')
    logging.info("Saving Current Conversation")
    file = asksaveasfile(mode="w", defaultextension=".txt")
    file.write(conversation)
    file.close()


def contact_developer():
    showinfo(title="Contact Developer",
             message="You Can Contact The Developer At Any Time By Email:\n sree23palla@outlook.com")
    echo_input()


def changelog():
    changelog_window = Toplevel(root)
    changelog_window.title("EchoAI - Changelog")
    changelog_window.geometry("500x500")
    changelog_window.resizable(width=False, height=False)
    changelog_text = Label(changelog_window, text="New In EchoAI v1.6.0:\n"
                                                  "New README Window!\n"
                                                  "New LICENSE Window!\n"
                                                  "Added New 'Other' Menu Cascade!\n"
                                                  "Added 'README' Button In New 'Other' Cascade!\n"
                                                  "Added 'LICENSE' Button In New 'Other' Cascade!\n"
                                                  "Removed Website Button From About Window!\n"
                                                  "Removed Changelog Button From About Window!\n"
                                                  "Added README Button To About Window!\n"
                                                  "Added LICENSE Button To About Window!\n"
                                                  "Added A Coin Flip Command!\n"
                                                  "Added A Dice Roller Command!\n"
                                                  "Re-Added Auto Update Check On Startup!\n"
                                                  "Improved Response With Some Commands!\n"
                                                  "Fixed Some Bugs With Files!\n"
                                                  "A Few Other Minor Changes And Fixes!\n"
                                                  "Please Report Any Bugs On The Github Page Or Email Me At "
                                                  "sree23palla@outlook.com\n "
                                                  "Thanks For Using EchoAI!\n"
                                                  "Click The Button Below To Check For Updates!")
    update_button = Button(changelog_window, command=update_echo, font=("TrebuchetMS", 12, 'bold'),
                           text="Click Here To Check For Updates!", width="500", height="50",
                           bd=0, bg="#32de97", activebackground="#3c9d9b", fg='#ffffff')
    changelog_text.pack(pady=10)
    update_button.pack()


def about_echo():
    about_window = Toplevel(root)
    about_window.title("EchoAI - About")
    about_window.geometry("400x400")
    about_window.resizable(width=False, height=False)
    about_text = Label(about_window,
                       text="EchoAI v1.6.0\n"
                            "EchoAI Is A FOSS Simple AI Personal Assistant!\n"
                            "Developed By: Sreekar Palla\n"
                            "Icon Designed By: Vijay Kesevan\n"
                            "Built Using Python Version: 3.8.8\n"
                            "OS: Windows 10\n"
                            "Tested On: Windows 10 x64 Systems\n"
                            "Feel Free To Contact Me Anytime "
                            "For Help, Bug Reports, Or Suggestions!\n"
                            "sree23palla@outlook.com\n"
                            "Thanks For Using EchoAI!")
    readme_button = Button(about_window, command=echo_readme, font=("TrebuchetMS", 12, 'bold'),
                           text="README", width="400", height="5",
                           bd=0, bg="#32de97", activebackground="#3c9d9b", fg='#ffffff')
    license_button = Button(about_window, command=echo_license, font=("TrebuchetMS", 12, 'bold'),
                            text="LICENSE", width="400", height="5",
                            bd=0, bg="#32de97", activebackground="#3c9d9b", fg='#ffffff')
    about_text.pack(pady=10)
    readme_button.pack()
    license_button.pack()


def echo_readme():
    readme_window = Toplevel(root)
    readme_window.title("EchoAI - README")
    readme_window.geometry("500x500")
    readme_window.resizable(width=False, height=False)
    readme_text = Text(readme_window, bd=0, bg="white", height="8", width="50", font="TrebuchetMS")
    readme_text.place(x=0, y=0, height=500, width=480)
    readme_scroll = Scrollbar(readme_window, command=readme_text.yview)
    readme_scroll.place(x=480, y=0, height=500, width=20)
    readme_text.config(state=NORMAL)
    try:
        readme_content = open(f"{current_directory}\\README.txt", mode="r", encoding="utf8").read()
        pass
    except Exception:
        showerror(title="README",
                  message="There Was An Error Accessing/Reading The README File! Please Try Again Later Or "
                          "Submit A Bug Report!")
        readme_content = "There Was An Error Accessing/Reading The README File! Please Try Again Later Or " \
                         "Submit A Bug Report!"
        pass
    readme_text.insert(END, readme_content)
    readme_text.config(state=DISABLED)


def echo_license():
    license_window = Toplevel(root)
    license_window.title("EchoAI - LICENSE")
    license_window.geometry("500x500")
    license_window.resizable(width=False, height=False)
    license_text = Text(license_window, bd=0, bg="white", height="8", width="50", font="TrebuchetMS")
    license_text.place(x=0, y=0, height=500, width=500)
    license_text.config(state=NORMAL)
    try:
        license_content = open(f"{current_directory}\\LICENSE.txt", mode="r", encoding="utf8").read()
        pass
    except Exception:
        showerror(title="LICENSE",
                  message="There Was An Error Accessing/Reading The LICENSE File! Please Try Again Later Or "
                          "Submit A Bug Report!")
        license_content = "There Was An Error Accessing/Reading The LICENSE File! Please Try Again Later Or " \
                          "Submit A Bug Report!"
        pass
    license_text.insert(END, license_content)
    license_text.config(state=DISABLED)


def echo_settings():
    settings_window = Toplevel(root)
    settings_window.title("EchoAI - Settings")
    settings_window.geometry("500x500")
    settings_window.resizable(width=False, height=False)
    user_data_file = open(f"{current_directory}\\Data\\UserData.json", "r+")
    user_data_file_json = json.load(open(f"{current_directory}\\Data\\UserData.json", "r+"))
    name = user_data_file_json["name"]
    nickname = user_data_file_json["nickname"]
    phone_number = user_data_file_json["phone_number"]
    email_address = user_data_file_json["email_address"]
    home_address = user_data_file_json["home_address"]
    settings_text = Label(settings_window,
                          text="Change Whatever You Would Like To And Then Click The Save Button!")
    settings_text.pack()
    name_input_text = Label(settings_window, text="NAME")
    name_input_text.pack()
    name_input = Entry(settings_window, width=450)
    name_input.pack()
    name_input.insert(0, f"{name}")
    nickname_input_text = Label(settings_window, text="NICKNAME")
    nickname_input_text.pack()
    nickname_input = Entry(settings_window, width=450)
    nickname_input.pack()
    nickname_input.insert(0, f"{nickname}")
    phone_number_input_text = Label(settings_window, text="PHONE NUMBER")
    phone_number_input_text.pack()
    phone_number_input = Entry(settings_window, width=450)
    phone_number_input.pack()
    phone_number_input.insert(0, f"{phone_number}")
    email_address_input_text = Label(settings_window, text="EMAIL ADDRESS")
    email_address_input_text.pack()
    email_address_input = Entry(settings_window, width=450)
    email_address_input.pack()
    email_address_input.insert(0, f"{email_address}")
    home_address_input_text = Label(settings_window, text="HOME ADDRESS")
    home_address_input_text.pack()
    home_address_input = Entry(settings_window, width=450)
    home_address_input.pack()
    home_address_input.insert(0, f"{home_address}")
    setting_file = open(f"{current_directory}\\Data\\settings.json", "r+")
    settings_file_json = json.load(open(f"{current_directory}\\Data\\settings.json", "r+"))
    voice_gender_number = settings_file_json["voice_gender"]
    if voice_gender_number == "1":
        voice_gender = "Female"
    else:
        voice_gender = "Male"
    weather_city = settings_file_json["weather_city"]
    units = settings_file["units"]
    volume = settings_file_json["volume"]
    variable = StringVar(settings_window)
    variable.set(f"{voice_gender}")
    voice_gender_input_text = Label(settings_window, text="VOICE GENDER")
    voice_gender_input_text.pack()
    voice_gender_input = OptionMenu(settings_window, variable, "Male", "Female")
    voice_gender_input.config(width=450)
    voice_gender_input.pack()
    variable_two = StringVar(settings_window)
    variable_two.set(f"{units}")
    units_text = Label(settings_window, text="MEASRUEMENT UNITS")
    units_text.pack()
    units_input = OptionMenu(settings_window, variable_two, "Imperial", "Metric")
    units_input.config(width=450)
    units_input.pack()
    weather_city_input_text = Label(settings_window, text="WEATHER CITY")
    weather_city_input_text.pack()
    weather_city_input = Entry(settings_window, width=450)
    weather_city_input.pack()
    weather_city_input.insert(0, f"{weather_city}")
    volume_slider_text = Label(settings_window, text="VOLUME")
    volume_slider_text.pack()
    double_variable = DoubleVar()
    double_variable.set(float(volume))
    volume_slider = Scale(settings_window, from_=0, to=1, orient=HORIZONTAL, resolution=.1,
                          variable=double_variable)
    volume_slider.pack()
    var = IntVar()
    submit_button = Button(settings_window,
                           command=lambda: var.set(1),
                           font=("TrebuchetMS", 10, 'bold'),
                           text="Click Here To Save And Continue!", width="400", height="5",
                           bd=0, bg="#32de97", activebackground="#3c9d9b", fg='#ffffff')
    submit_button.pack()
    submit_button.wait_variable(var)
    new_name = name_input.get()
    new_nickname = nickname_input.get()
    new_phone_number = phone_number_input.get()
    new_email_address = email_address_input.get()
    new_home_address = home_address_input.get()
    if new_name == "" or new_nickname == "" or new_phone_number == "" or new_email_address == "" or new_home_address == "" or \
            new_name.isspace() or new_nickname.isspace() or new_phone_number.isspace() or new_email_address.isspace() or \
            new_home_address.isspace():
        showerror(title="EchoAI - Settings",
                  message="You Have Not Filled Everything Out Properly! Settings Will Now Exit!!")
        settings_window.destroy()
        echo_input()
    else:
        logging.warning("Deleting Old User Data")
        user_data_file.truncate()
        logging.warning("Writing New User Data")
        data = {
            "name": f"{new_name}",
            "nickname": f"{new_nickname}",
            "phone_number": f"{new_phone_number}",
            "email_address": f"{new_email_address}",
            "home_address": f"{new_home_address}"
        }
        data_object = json.dumps(data, indent=4)
        with user_data_file as outfile:
            outfile.write(data_object)
        user_data_file.close()
        logging.info("New User Data Saved")
    new_voice_gender = variable.get()
    new_units = variable_two.get()
    new_weather_city = weather_city_input.get()
    new_volume = volume_slider.get()
    if new_weather_city == "" or new_weather_city.isspace():
        showerror(title="EchoAI - Settings",
                  message="You Have Not Filled Everything Out Properly! Settings Will Now Exit!")
        settings_window.destroy()
        echo_input()
    else:
        logging.warning("Deleting Old Settings Data")
        setting_file.truncate()
        if new_voice_gender.upper() == "MALE":
            gender = 0
        else:
            gender = 1
        logging.warning("Writing New Settings Data")
        settings = {
            "weather_city": f"{new_weather_city}",
            "units": f"{new_units}",
            "voice_gender": f"{str(gender)}",
            "volume": f"{str(new_volume)}"
        }
        settings_object = json.dumps(settings, indent=4)
        with setting_file as outfile:
            outfile.write(settings_object)
        setting_file.close()
        logging.info("New Settings Data Saved")
        showinfo(title="Settings",
                 message="Finished Saving New Settings! Please Restart For Changes To Take Effect!")
        restart_echo()


def echo_help():
    logging.info("Displaying Help Window")
    list_of_modules = ["Ask What Time It Is!", "Ask What Date It Is!", "Ask About A Famous Person!",
                       "Ask A Mathematical Question!", "Ask About The Weather Today!", "Ask For A Joke!",
                       "Ask For A Fun Fact!",
                       "Ask A Geographical Question!"]
    list_of_tips = [
        "Find Out What Your Device Is Doing By Clicking On The Task Manager Button In The DEVICE Dropdown At The Top Of The Main Window!",
        "View Information About Your Device By Clicking The System Information Button In The DEVICE Dropdown At The Top Of The Main Window!",
        "Run Any Terminal Command By Clicking The Terminal Command Button In The DEVICE Dropdown At The Top Of The Main Window!",
        "Check For The Latest Update By Clicking The Update Button In the 1.6.0 Dropdown At The Top Of The Main Window!",
        "Quickly Press <Esc> And <Enter> To Exit EchoAI!",
        "Check Out EchoAI's Source Code And More By Clicking The Website Button In The 1.6.0 Dropdown At The Top Of The Main Window!",
        "Reach Out To The Developer By Clicking The Contact Developer Button In The ECHO Dropdown At The Top Of The Main Window!",
        "Submit A Bug Report By Clicking The Report Problem Button In The ECHO Dropdown At The Top Of The Main Window!"]
    random.shuffle(list_of_modules)
    random.shuffle(list_of_tips)
    item_one = list_of_modules[0]
    item_two = list_of_modules[1]
    item_three = list_of_modules[2]
    item_four = list_of_modules[3]
    item_five = list_of_modules[4]
    tip = list_of_tips[0]
    help_window = Toplevel(root)
    help_window.title("EchoAI - Help")
    help_window.geometry("800x200")
    help_window.resizable(width=FALSE, height=FALSE)
    help_window_text = Label(help_window, text="Try Doing These:\n"
                                               f"{item_one}\n"
                                               f"{item_two}\n"
                                               f"{item_three}\n"
                                               f"{item_four}\n"
                                               f"{item_five}\n"
                                               f"Tip: {tip}")
    help_window_text.pack()


def restart_echo():
    restart_confirmation = askyesno(title="Restart", message="Are You Sure You Want To Restart EchoAI?")
    if restart_confirmation:
        logging.warning("Restarting EchoAI")
        os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)
    else:
        echo_input()


def exit_echo():
    exit_confirmation = askyesno(title="Exit", message="Are You Sure You Want To Exit EchoAI?")
    if exit_confirmation:
        logging.warning("Exiting EchoAI")
        root.destroy()
        exit()
    else:
        echo_input()


def exit_echo_param(event):
    exit_confirmation = askyesno(title="Exit", message="Are You Sure You Want To Exit EchoAI?")
    if exit_confirmation:
        logging.warning("Exiting EchoAI")
        root.destroy()
        exit()
    else:
        echo_input()


def exit_echo_no_confirm():
    logging.warning("Exiting EchoAI Without Confirmation!")
    root.destroy()
    exit()


def system_information():
    showinfo(title="System Information", message="Check The Terminal Window That Is About To Open!")
    logging.info("Starting Command Prompt")
    os.system("start cmd")
    time.sleep(2)
    logging.info("Executing Terminal Command: systeminfo")
    gui.typewrite(message="systeminfo\n")


def task_manager():
    showinfo(title="Task Manager",
             message="In Order To Use EchoAI Again, You Might Need To Close Task Manager! This Is "
                     "A Python/Windows Problem And I Cannot Do Anything About It!")
    logging.info("Starting Task Manager")
    os.system("taskmgr")


def terminal_command():
    terminal_input = askstring(title="Command", prompt="Enter A Command To Execute In Terminal!")
    if terminal_input is None or terminal_input == "EchoAI" or terminal_input == "echoai":
        confirmation = askokcancel(title="Command",
                                   message="This Will Launch A New Instance Of The App! Would You Like To Continue?")
        if confirmation:
            logging.warning("Starting New Instance Of EchoAI")
            os.system("start EchoAI")
            echo_input()
        else:
            echo_input()
    else:
        showinfo(title="Terminal Command", message="Check The Terminal Window That Is About To Open!")
        logging.info("Starting Command Prompt")
        os.system("start cmd")
        time.sleep(2)
        logging.info(f"Executing Terminal Command: {terminal_input}")
        gui.typewrite(f"{terminal_input}\n")


def sign_out():
    lock_confirmation = askyesno(title="Sign Out", message="Are You Sure You Want To Sign Out Of Your Device?")
    if lock_confirmation:
        logging.info("Signing Out Of Device")
        os.system("shutdown -l")
    else:
        echo_input()


def shutdown_device():
    shutdown_confirmation = askyesno(title="Shutdown Device", message="Are You Sure You Want To Shut Down Your Device?")
    if shutdown_confirmation:
        logging.info("Shutting Down Device")
        os.system("shutdown /s /t 2")
    else:
        echo_input()


def restart_device():
    restart_confirmation = askyesno(title="Restart Device", message="Are You Sure You Want To Restart Your Device?")
    if restart_confirmation:
        logging.info("Restarting Device")
        os.system("shutdown /r /t 2")
    else:
        echo_input()


def echo_timer():
    timer_window = Toplevel(root)
    timer_window.geometry("300x300")
    timer_window.title("EchoAI - Timer")
    hour = StringVar()
    minute = StringVar()
    second = StringVar()
    hour.set("00")
    minute.set("00")
    second.set("00")
    hours_label = Label(timer_window, text="HOURS")
    hours_label.pack()
    hourEntry = Entry(timer_window, width=3, font=("Arial", 18, ""),
                      textvariable=hour)
    hourEntry.pack()
    minutes_label = Label(timer_window, text="MINUTES")
    minutes_label.pack()
    minuteEntry = Entry(timer_window, width=3, font=("Arial", 18, ""),
                        textvariable=minute)
    minuteEntry.pack()
    seconds_label = Label(timer_window, text="SECONDS")
    seconds_label.pack()
    secondEntry = Entry(timer_window, width=3, font=("Arial", 18, ""),
                        textvariable=second)
    secondEntry.pack()
    var = IntVar()
    submit_button = Button(timer_window,
                           command=lambda: var.set(1),
                           font=("TrebuchetMS", 10, 'bold'),
                           text="Start The Timer", width="400", height="5",
                           bd=0, bg="#32de97", activebackground="#3c9d9b", fg='#ffffff')
    submit_button.pack()
    submit_button.wait_variable(var)
    temp = int(hour.get()) * 3600 + int(minute.get()) * 60 + int(second.get())
    while temp > -1:
        mins, secs = divmod(temp, 60)
        hours = 0
        if mins > 60:
            hours, mins = divmod(mins, 60)
        hour.set("{0:2d}".format(hours))
        minute.set("{0:2d}".format(mins))
        second.set("{0:2d}".format(secs))
        root.update()
        time.sleep(1)
        if (temp == 0):
            timer_window.destroy()
            messagebox.showinfo("EchoAI - Timer", "Timer Ended!")
        temp -= 1


def clean_up_sentence(sentence):
    logging.info("Cleaning Up User Command Sentence")
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words


def bow(sentence, words):
    logging.info(f"Bow() Executed: Sentence={sentence}, Words={words}")
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1
    return np.array(bag)


def predict_class(sentence, model):
    logging.info(f"Predicting Intent Class: Sentence={sentence}, Model={model}")
    p = bow(sentence, words=words)
    res = model.predict(np.array([p]))[0]
    error_threshold = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > error_threshold]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list


def get_response(ints, intents_json, query):
    tag = ints[0]['intent']
    logging.info(f"Predicted Tag: {tag}")
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
            if tag == "greeting":
                data_file = json.load(open(f"{current_directory}\\Data\\UserData.json"))
                nickname = data_file["nickname"]
                result = result + f"{nickname}!"
                return result
            if tag == "time":
                t = time.localtime()
                current_time = time.strftime("%I:%M %p", t)
                result = result + current_time
                return result
            if tag == "date":
                today_date = date.today()
                date_formatted_date = today_date.strftime("%B %d, %Y")
                result = result + date_formatted_date
                return result
            if tag == "math":
                client = wolframalpha.Client('AWUWT5-9LW6U3G4U6')
                res = client.query(query)
                result = next(res.results).text
                return result
            if tag == "wikipedia":
                result = wikipedia.summary(query, sentences=2)
                return result
            if tag == "wolfram":
                client = wolframalpha.Client('AWUWT5-9LW6U3G4U6')
                res = client.query(query)
                result = next(res.results).text
                return result
            if tag == "days until holiday":
                today = date.today()
                today_year = today.year
                if "Christmas" in query:
                    future = date(today_year, 12, 25)
                    diff = future - today
                    diff_days = str(diff.days)
                    if "-" in diff_days:
                        today_year += 1
                        future = date(today_year, 12, 25)
                        diff = future - today
                        diff_days = str(diff.days)
                        result = "It Is " + diff_days + " Days Until Then!"
                    else:
                        result = "It Is " + diff_days + " Days Until Then!"
                    return result
                if "New Year" in query:
                    future = date(today_year, 1, 1)
                    diff = future - today
                    diff_days = str(diff.days)
                    if "-" in diff_days:
                        today_year += 1
                        future = date(today_year, 1, 1)
                        diff = future - today
                        diff_days = str(diff.days)
                        result = "It Is " + diff_days + " Days Until Then!"
                    else:
                        result = "It Is " + diff_days + " Days Until Then!"
                    return result
                if "Memorial Day" in query:
                    future = date(today_year, 5, 25)
                    diff = future - today
                    diff_days = str(diff.days)
                    if "-" in diff_days:
                        today_year += 1
                        future = date(today_year, 5, 25)
                        diff = future - today
                        diff_days = str(diff.days)
                        result = "It Is " + diff_days + " Days Until Then!"
                    else:
                        result = "It Is " + diff_days + " Days Until Then!"
                    return result
                if "Independence Day" in query:
                    future = date(today_year, 7, 3)
                    diff = future - today
                    diff_days = str(diff.days)
                    if "-" in diff_days:
                        today_year += 1
                        future = date(today_year, 7, 3)
                        diff = future - today
                        diff_days = str(diff.days)
                        result = "It Is " + diff_days + " Days Until Then!"
                    else:
                        result = "It Is " + diff_days + " Days Until Then!"
                    return result
                if "Labor Day" in query:
                    future = date(today_year, 9, 7)
                    diff = future - today
                    diff_days = str(diff.days)
                    if "-" in diff_days:
                        today_year += 1
                        future = date(today_year, 9, 7)
                        diff = future - today
                        diff_days = str(diff.days)
                        result = "It Is " + diff_days + " Days Until Then!"
                    else:
                        result = "It Is " + diff_days + " Days Until Then!"
                    return result
                if "Veterans Day" in query:
                    future = date(today_year, 11, 11)
                    diff = future - today
                    diff_days = str(diff.days)
                    if "-" in diff_days:
                        today_year += 1
                        future = date(today_year, 11, 11)
                        diff = future - today
                        diff_days = str(diff.days)
                        result = "It Is " + diff_days + " Days Until Then!"
                    else:
                        result = "It Is " + diff_days + " Days Until Then!"
                    return result
                if "Thanksgiving" in query:
                    future = date(today_year, 11, 26)
                    diff = future - today
                    diff_days = str(diff.days)
                    if "-" in diff_days:
                        today_year += 1
                        future = date(today_year, 11, 26)
                        diff = future - today
                        diff_days = str(diff.days)
                        result = "It Is " + diff_days + " Days Until Then!"
                    else:
                        result = "It Is " + diff_days + " Days Until Then!"
                    return result
                if "Martin Luther" in query or "MLK" in query:
                    future = date(today_year, 1, 20)
                    diff = future - today
                    diff_days = str(diff.days)
                    if "-" in diff_days:
                        today_year += 1
                        future = date(today_year, 1, 20)
                        diff = future - today
                        diff_days = str(diff.days)
                        result = "It Is " + diff_days + " Days Until Then!"
                    else:
                        result = "It Is " + diff_days + " Days Until Then!"
                    return result
                if "Easter" in query:
                    future = date(today_year, 4, 4)
                    diff = future - today
                    diff_days = str(diff.days)
                    if "-" in diff_days:
                        today_year += 1
                        future = date(today_year, 4, 4)
                        diff = future - today
                        diff_days = str(diff.days)
                        result = "It Is " + diff_days + " Days Until Then!"
                    else:
                        result = "It Is " + diff_days + " Days Until Then!"
                    return result
            if tag == "who am i":
                data_file = json.load(open(f"{current_directory}\\Data\\UserData.json"))
                name = data_file['name']
                nickname = data_file['nickname']
                phone_number = data_file['phone_number']
                email_address = data_file['email_address']
                home_address = data_file['home_address']
                ChatLog.insert(END, f"\nYou Are {name} But Since We're Friends, I Get To Call You {nickname}" + '\n' + \
                         f"Phone Number: {phone_number}" + '\n' + f"Email Address: {email_address}" + '\n' + \
                         f"Home Address: {home_address}")
                result = f"\nYou Are {name} But Since We're Friends, I Get To Call You {nickname}"
                return result
            if tag == "weather local":
                units = settings_file["units"]
                BASE_URL = "https://api.openweathermap.org/data/2.5/weather?"
                CITY = settings_file["weather_city"]
                API_KEY = "95955dc71e2c07a73932f9d5ff2b0887"
                URL = BASE_URL + "q=" + CITY + "&appid=" + API_KEY
                response = requests.get(URL)
                if response.status_code == 200:
                    data = response.json()
                    main = data['main']
                    temperature = main['temp']
                    f_temp = (temperature - 273.15) * (9 / 5) + 32
                    c_temp = (f_temp - 32) * (5 / 9)
                    temp_feel_like = main['feels_like']
                    feels_like_f = (temp_feel_like - 273.15) * (9 / 5) + 32
                    feels_like_c = (feels_like_f - 32) * (5 / 9)
                    humidity = main['humidity']
                    pressure = main['pressure']
                    weather_report = data['weather']
                    wind_report = data['wind']
                    if units == "Imperial":
                        ChatLog.insert(END,
                                       f"Here Is The Current Weather In {CITY}" + '\n' + f"Temperature: "
                                                                                         f"{round(f_temp)}°F" + '\n' +
                                       f"Feels Like: {round(feels_like_f)}°F" + '\n' + f"Humidity: {round(humidity)}%"
                                       + '\n' + f"Pressure: {pressure}hPa" + '\n' + f"Weather Type: "
                                                                                    f"{weather_report[0]['description']}"
                                       + '\n' + f"Wind Speed: {round(wind_report['speed'] * 2.237)}mph" + '\n')
                        result = f"It Is {round(f_temp)} Degrees Fahrenheit In {CITY} Right Now!"
                        return result
                    else:
                        ChatLog.insert(END,
                                       f"Here Is The Current Weather In {CITY}" + '\n' + f"Temperature: "
                                                                                         f"{round(c_temp)}°C" + '\n' +
                                       f"Feels Like: {round(feels_like_c)}°C" + '\n' + f"Humidity: {round(humidity)}%"
                                       + '\n' + f"Pressure: {pressure}hPa" + '\n' + f"Weather Type: "
                                                                                    f"{weather_report[0]['description']}"
                                       + '\n' + f"Wind Speed: {round((wind_report['speed'] * 2.237) * 1.609)}kph")
                        result = f"It Is {round(c_temp)} Degrees Celsius In {CITY} Right Now!"
                        return result
                else:
                    logging.warning("Error Connecting To OpenWeatherMap Weather API")
                    result = "ERROR"
                    showerror(title="Weather",
                              message=f"There Was An Error Contacting The Weather API And Retrieving Weather For "
                                      f"'{CITY}'! Please Try Again Later And Make Sure Your City Is Correct In Settings!")
                    return result
            if tag == "dice roll":
                if not re.search(r'\d+', query):
                    min_face = 1
                    max_face = 6
                    rolled_number = random.randint(min_face, max_face)
                    result = "Rolled:" + str(rolled_number)
                    return result
                else:
                    temp = re.findall(r'\d+', query)
                    res = list(map(int, temp))
                    res_new = str(res).replace("[", "").replace("]", "")
                    min_face = 1
                    max_face = int(res_new)
                    rolled_number = random.randint(min_face, max_face)
                    result = "Rolled:" + str(rolled_number)
                    return result
            else:
                return result


def echo_response(cmd):
    logging.info(f"Getting EchoAI Response To Command: {cmd}")
    ints = predict_class(cmd, model)
    res = get_response(ints, intents, cmd)
    return res


def echo_input():
    voice_button = Button(root, font=("TrebuchetMS", 12, 'bold'), text="Click To Use!", width="500", height="50",
                          bd=0, bg="#32de97", activebackground="#ffffff", fg='#ffffff',
                          command=command)
    voice_button.place(y=550, x=0)


def command():
    logging.info("Button Click Detected. Now Executing Function command()")
    rec = sr.Recognizer()
    mic = sr.Microphone()
    try:
        with mic as source:
            logging.info("Listening For Command")
            audio = rec.listen(source, timeout=30, phrase_time_limit=3)
            cmd: str = rec.recognize_google(audio)
            logging.info(f"User Said: {cmd}")
            ChatLog.config(state=NORMAL)
            ChatLog.insert(END, f"{name}: " + cmd + '\n\n')
            response = echo_response(cmd)
            if "Fahrenheit" in response or "Celsius" in response or name in response:
                ChatLog.insert(END, f"{response}" + '\n\n')
            if "Phone Number" in response and "Home Address" in response:
                ChatLog.insert(END, f"{response}" + '\n\n')
            else:
                ChatLog.insert(END, "ECHO: " + response + '\n\n')
            ChatLog.yview(END)
            engine.say(response)
            engine.runAndWait()
            ChatLog.config(state=DISABLED)
    except sr.UnknownValueError:
        logging.error("UnknownValueError Raised In Function command()")
        showerror(title="EchoAI", message="I Could Not Properly Hear What You Said! Please Try Again!")
        echo_input()
    except sr.RequestError as e:
        logging.error(f"RequestError Raised In Function command() Error: {e}")
        showerror(title="EchoAI", message=f"There Was A Problem With Your Request! Please Try Again Later! Error: {e}")
        echo_input()
    except sr.WaitTimeoutError:
        logging.error("WaitTimeoutError Raised In Function command()")
        ChatLog.insert(END, "You Took Too Long To Speak! Press The Green Button Below To Use Again!")
        echo_input()
    except Exception as e:
        logging.error(f"Exception Raised In Function command() Error: {e}")
        showerror(title="EchoAI", message=f"Something Went Wrong! Please Try Again Or Submit A Bug Report! Error: {e}")
        echo_input()


root = Tk()
icon_image = PhotoImage(file="echo.png")
root.title("EchoAI")
root.iconphoto(False, icon_image)
root.geometry("500x600")
root.resizable(width=FALSE, height=FALSE)
current_directory = os.getcwd()
log_file = open("app.log", "r+")
log_bytes = open("app.log", "rb")
logging.basicConfig(filename='app.log', filemode='r+', level="DEBUG",
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
try:
    with log_bytes as f:
        f.seek(-2, os.SEEK_END)
        while f.read(1) != b'\n':
            f.seek(-2, os.SEEK_CUR)
        last_line = f.readline().decode()
    if " - comtypes - DEBUG - CoUnititialize() done." not in last_line and "- root - WARNING - Restarting EchoAI" not in last_line\
            and last_line != "use" and last_line != "" and not last_line.isspace():
        report_bug = askyesno(title="Crash Detected",
                              message="It Appears That EchoAI Ran Into A Problem Last Time It Was Used. Would You Like "
                                      "To Submit A Bug Report?")
        if report_bug:
            bug_report()
except OSError:
    pass
log_file.truncate()
logging.info("Loading Application And GUI")
ChatLog = Text(root, bd=0, bg="white", height="8", width="50", font="TrebuchetMS")
scrollbar = Scrollbar(root, command=ChatLog.yview)
ChatLog['yscrollcommand'] = scrollbar.set
scrollbar.place(x=480, y=0, height=550, width=20)
ChatLog.place(x=0, y=0, height=550, width=480)
menubar = Menu(root)
echo_menu = Menu(menubar, tearoff=0)
device_menu = Menu(menubar, tearoff=0)
tools_menu = Menu(menubar, tearoff=0)
other_menu = Menu(menubar, tearoff=0)
version_menu = Menu(menubar, tearoff=0)
echo_menu.add_command(label="Save Conversation", command=save_conversation)
echo_menu.add_command(label="Contact Developer", command=contact_developer)
echo_menu.add_command(label="Report Problem", command=bug_report)
version_menu.add_command(label="Changelog", command=changelog)
version_menu.add_command(label="Website", command=open_website)
echo_menu.add_command(label="About", command=about_echo)
echo_menu.add_command(label="Help", command=echo_help)
echo_menu.add_command(label="Settings", command=echo_settings)
version_menu.add_command(label="Update", command=update_echo)
echo_menu.add_command(label="Reset", command=reset_echo)
echo_menu.add_command(label="Restart", command=restart_echo)
echo_menu.add_command(label="Exit", command=exit_echo)
device_menu.add_command(label="Task Manager", command=task_manager)
device_menu.add_command(label="System Info", command=system_information)
device_menu.add_command(label="Terminal Command", command=terminal_command)
device_menu.add_command(label="Sign Out", command=sign_out)
device_menu.add_command(label="Shutdown Device", command=shutdown_device)
device_menu.add_command(label="Restart Device", command=restart_device)
tools_menu.add_command(label="Timer", command=echo_timer)
other_menu.add_command(label="README", command=echo_readme)
other_menu.add_command(label="LICENSE", command=echo_license)
menubar.add_cascade(label="Echo", menu=echo_menu)
menubar.add_cascade(label="Device", menu=device_menu)
menubar.add_cascade(label="Tools", menu=tools_menu)
menubar.add_cascade(label="Other", menu=other_menu)
menubar.add_cascade(label="1.6.0", menu=version_menu)
root.config(menu=menubar)
root.bind("<Escape>", exit_echo_param)
root.protocol("WM_DELETE_WINDOW", exit_echo_no_confirm)
ChatLog.config(font=("TrebuchetMS", 12))
logging.info("Finished Building And Configuring GUI")
logging.info("Checking Data To See If Set Up")
user_data_file_check = open(f"{current_directory}\\Data\\UserData.json").read()
if user_data_file_check == "" or user_data_file_check.isspace():
    logging.info("User Data Not Found. Setup Incomplete")
    showinfo(title="Setup", message="You Have Not Set Up EchoAI Yet! The Following Process Will Help With Setup!")
    logging.info("Setup Prompt Shown")
    setup()
    exit_echo_no_confirm()
else:
    pass
logging.info("User Data Found. EchoAI Is Already Set Up")
logging.info("Starting And Configuring TTS Voice")
engine = pyttsx3.init("sapi5")
voices = engine.getProperty('voices')
rate = engine.getProperty('rate')
settings_file = json.load(open(f"{current_directory}\\Data\\settings.json", "r+"))
gender = settings_file['voice_gender']
volume = settings_file["volume"]
engine.setProperty('voice', voices[int(gender)].id)
engine.setProperty('volume', float(volume))
engine.setProperty('rate', 150)
logging.info("Finished Configuring TTS Voice")
name_file = json.load(open(f"{current_directory}\\Data\\UserData.json"))
name = name_file['name']
ChatLog.config(state=NORMAL)
ChatLog.insert(END, "Press The Green Button Below To Make Me Listen!\n\n")
logging.info("Checking For Update On Startup")
url = "http://github.com/teekar2023/EchoAI/releases/latest/"
r = requests.get(url, allow_redirects=True)
redirected_url = r.url
if redirected_url != "https://github.com/teekar2023/EchoAI/releases/tag/v1.6.0":
    logging.warning("Newer Version Available! Current Version: 1.6.0")
    ChatLog.insert(END, "There Is A New Version Of EchoAI Available! Use The Update Button In The v1.6.0 Dropdown To "
                        "Download The Update Installer!\n\n")
    pass
else:
    pass
logging.info("Done With Startup. Moving Onto echo_input() Function")
ChatLog.config(state=DISABLED)
echo_input()
root.mainloop()
