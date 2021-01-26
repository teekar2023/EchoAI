#  Copyright © 2020 <Sreekar Palla>
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
import json
import logging
import os
import pickle
import random
import subprocess
import time
import webbrowser
from datetime import date
from tkinter import *
from tkinter.filedialog import asksaveasfile
from tkinter.messagebox import showerror, showinfo, askyesno
from tkinter.simpledialog import askstring

import holidays
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
model = load_model('ECHOAI_model.h5')
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
    if not ((not ((name == "") or (nickname == "") or (phone_number == "") or (
            email_address == "") or (home_address == "") or (weather_city == "") or (
                          voice_gender == "Select Voice Gender") or name.isspace() or nickname.isspace() or phone_number.isspace()) and not
             email_address.isspace()) and not home_address.isspace() and not weather_city.isspace()):
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
        button_input()


def open_website():
    logging.info("Opening Github Page")
    webbrowser.open("https://github.com/teekar2023/EchoAI")


def bug_report():
    logging.info("Bug Report Process Starting")
    showinfo(title="Bug Report",
             message="This Might Require A Github Account! If You Do not Have One And Don't Want To Make One, You Can Email Me At sree23palla@outlook.com")
    showinfo(title="Bug Report",
             message=f"Please Attach The Following Log File Into The Bug Report! Path To Log File: {current_directory}\\app.log")
    webbrowser.open("https://github.com/teekar2023/EchoAI/issues/new")


def update_echo():
    url = "http://github.com/teekar2023/EchoAI/releases/latest/"
    r = requests.get(url, allow_redirects=True)
    redirected_url = r.url
    if redirected_url != "https://github.com/teekar2023/EchoAI/releases/tag/v1.3.0":
        update_confirmation = askyesno(title="Update",
                                       message="There Is A New Version Available! Would You Like To Download It?")
        if update_confirmation:
            new_url = str(redirected_url) + "/EchoAI.Setup.exe"
            download_url = new_url.replace("tag", "download")
            webbrowser.open(download_url)
            logging.info("Downloading Updated Version")
            showinfo(title="Update", message="Please Uninstall This Version And Then Install The New Version!")
        else:
            showinfo(title="Update", message="Update Aborted!")
            button_input()
    else:
        showinfo(title="Update", message="There Is No New Update Available!")
        logging.info("No New Update Available")
        button_input()


def save_conversation():
    conversation = ChatLog.get("1.0", 'end-1c')
    logging.info("Saving Current Conversation")
    file = asksaveasfile(mode="w")
    file.write(conversation)
    file.close()


def contact_developer():
    logging.info("Contact Developer Popup Shown")
    showinfo(title="Contact Developer",
             message="You Can Contact The Developer At Any Time By Email:\n sree23palla@outlook.com")
    button_input()


def changelog():
    changelog_window = Toplevel(root)
    changelog_window.title("EchoAI - Changelog")
    changelog_window.geometry("500x500")
    changelog_window.resizable(width=False, height=False)
    changelog_text = Label(changelog_window, text="New In EchoAI v1.3.0:\n"
                                                  "Added Logging!\n"
                                                  "Added Crash Detection!\n"
                                                  "Added App Icon For Window!\n"
                                                  "Added Help Window In ECHO Dropdown!\n"
                                                  "Unit Conversion Support!\n"
                                                  "Basic Translation Support!\n"
                                                  "Fixed Problem Where User Could Manipulate Contents Of The ChatLog Box!\n"
                                                  "Saying 'goodbye' now returns something instead of prompting for exit!\n"
                                                  "Removed Uninstall Function Due To Some Problems!\n"
                                                  "Other Minor Changes And Fixes!\n"
                                                  "Please Report Any Bugs On The Github Page Or Email Me At "
                                                  "sree23palla@outlook.com\n "
                                                  "Thank You For Using EchoAI!")
    website_button = Button(changelog_window, command=open_website, font=("TrebuchetMS", 12, 'bold'),
                            text="Click Here To Open Website!", width="500", height="5",
                            bd=0, bg="#32de97", activebackground="#3c9d9b", fg='#ffffff')
    update_button = Button(changelog_window, command=update_echo, font=("TrebuchetMS", 12, 'bold'),
                           text="Click Here To Check For Updates!", width="500", height="5",
                           bd=0, bg="#32de97", activebackground="#3c9d9b", fg='#ffffff')
    changelog_text.pack(pady=10)
    website_button.pack()
    update_button.pack()


def about_echo():
    about_window = Toplevel(root)
    about_window.title("EchoAI - About")
    about_window.geometry("400x400")
    about_window.resizable(width=False, height=False)
    about_text = Label(about_window,
                       text="EchoAI v1.3.0\n"
                            "EchoAI Is A FOSS Simple AI Personal Assistant!\n"
                            "Developed By: Sreekar Palla\n"
                            "Icon Designed By: Vijay Kesevan\n"
                            "Python Version Used: 3.8\n"
                            "OS: Windows 10\n"
                            "Tested On: Windows 10 x64 Based Systems\n"
                            "Feel Free To Contact Me Anytime "
                            "For Help, Bug Reports, Or Suggestions!\n"
                            "sree23palla@outlook.com\n"
                            "Thanks For Using EchoAI!")
    website_button = Button(about_window, command=open_website, font=("TrebuchetMS", 12, 'bold'),
                            text="Click Here To Open Website!", width="400", height="5",
                            bd=0, bg="#32de97", activebackground="#3c9d9b", fg='#ffffff')
    changelog_button = Button(about_window, command=changelog, font=("TrebuchetMS", 12, 'bold'),
                              text="Click Here To View The Changelog!", width="400", height="5",
                              bd=0, bg="#32de97", activebackground="#3c9d9b", fg='#ffffff')
    about_text.pack(pady=10)
    website_button.pack()
    changelog_button.pack()


def echo_settings():
    settings_window = Toplevel(root)
    settings_window.title("EchoAI - Settings")
    settings_window.geometry("500x500")
    settings_window.resizable(width=False, height=False)
    settings_label = Label(settings_window, text="Select The Category Of Settings You Would Like To Modify!")
    settings_label.pack(pady=10)
    user_data_button = Button(settings_window, command=user_data, font=("TrebuchetMS", 12, 'bold'),
                              text="Personal Information", width="100", height="15",
                              bd=0, bg="#32de97", activebackground="#3c9d9b", fg='#ffffff')
    user_data_button.pack()
    other_settings_button = Button(settings_window, command=other_settings, font=("TrebuchetMS", 12, 'bold'),
                                   text="EchoAI Settings", width="100", height="15",
                                   bd=0, bg="#32de97", activebackground="#3c9d9b", fg='#ffffff')
    other_settings_button.pack()


def user_data():
    user_data_window = Toplevel(root)
    user_data_window.title("EchoAI - Settings (User Data)")
    user_data_window.geometry("500x500")
    user_data_window.resizable(width=False, height=False)
    user_data_file = open(f"{current_directory}\\Data\\UserData.json", "r+")
    user_data_file_json = json.load(open(f"{current_directory}\\Data\\UserData.json", "r+"))
    name = user_data_file_json["name"]
    nickname = user_data_file_json["nickname"]
    phone_number = user_data_file_json["phone_number"]
    email_address = user_data_file_json["email_address"]
    home_address = user_data_file_json["home_address"]
    personal_information_text = Label(user_data_window,
                                      text="Change Whatever You Would Like To And Then Click The Save Button!")
    personal_information_text.pack()
    name_input_text = Label(user_data_window, text="NAME")
    name_input_text.pack()
    name_input = Entry(user_data_window, width=450)
    name_input.pack()
    name_input.insert(0, f"{name}")
    nickname_input_text = Label(user_data_window, text="NICKNAME")
    nickname_input_text.pack()
    nickname_input = Entry(user_data_window, width=450)
    nickname_input.pack()
    nickname_input.insert(0, f"{nickname}")
    phone_number_input_text = Label(user_data_window, text="PHONE NUMBER")
    phone_number_input_text.pack()
    phone_number_input = Entry(user_data_window, width=450)
    phone_number_input.pack()
    phone_number_input.insert(0, f"{phone_number}")
    email_address_input_text = Label(user_data_window, text="EMAIL ADDRESS")
    email_address_input_text.pack()
    email_address_input = Entry(user_data_window, width=450)
    email_address_input.pack()
    email_address_input.insert(0, f"{email_address}")
    home_address_input_text = Label(user_data_window, text="HOME ADDRESS")
    home_address_input_text.pack()
    home_address_input = Entry(user_data_window, width=450)
    home_address_input.pack()
    home_address_input.insert(0, f"{home_address}")
    var = IntVar()
    save_button = submit_button = Button(user_data_window,
                                         command=lambda: var.set(1),
                                         font=("TrebuchetMS", 10, 'bold'),
                                         text="Click Here To Save And Continue!", width="400", height="5",
                                         bd=0, bg="#32de97", activebackground="#3c9d9b", fg='#ffffff')
    save_button.pack()
    submit_button.wait_variable(var)
    new_name = name_input.get()
    new_nickname = nickname_input.get()
    new_phone_number = phone_number_input.get()
    new_email_address = email_address_input.get()
    new_home_address = home_address_input.get()
    if new_name == "" or new_nickname == "" or new_phone_number == "" or new_email_address == "" or new_home_address == "" or \
            new_name.isspace() or new_nickname.isspace() or new_phone_number.isspace() or new_email_address.isspace() or \
            new_home_address.isspace():
        showerror(title="EchoAI Settings (Personal Information)",
                  message="You Have Not Filled Everything Out Properly! Settings Will Now Exit!!")
        user_data_window.destroy()
        button_input()
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
        showinfo(title="Settings",
                 message="Finished Saving New Personal Information! Please Restart EchoAI For Changes To Take Place!")
        user_data_window.destroy()
        restart_echo()


def other_settings():
    other_settings_window = Toplevel(root)
    other_settings_window.title("EchoAI Settings (Settings)")
    other_settings_window.geometry("500x500")
    other_settings_window.resizable(width=False, height=False)
    setting_file = open(f"{current_directory}\\Data\\settings.json", "r+")
    settings_file_json = json.load(open(f"{current_directory}\\Data\\settings.json", "r+"))
    voice_gender_number = settings_file_json["voice_gender"]
    if voice_gender_number == "1":
        voice_gender = "Female"
    else:
        voice_gender = "Male"
    weather_city = settings_file_json["weather_city"]
    volume = settings_file_json["volume"]
    variable = StringVar(other_settings_window)
    variable.set(f"{voice_gender}")
    voice_gender_input_text = Label(other_settings_window, text="VOICE GENDER")
    voice_gender_input_text.pack()
    voice_gender_input = OptionMenu(other_settings_window, variable, "Male", "Female")
    voice_gender_input.config(width=450)
    voice_gender_input.pack()
    weather_city_input_text = Label(other_settings_window, text="WEATHER CITY")
    weather_city_input_text.pack()
    weather_city_input = Entry(other_settings_window, width=450)
    weather_city_input.pack()
    weather_city_input.insert(0, f"{weather_city}")
    volume_slider_text = Label(other_settings_window, text="VOLUME")
    volume_slider_text.pack()
    double_variable = DoubleVar()
    double_variable.set(float(volume))
    volume_slider = Scale(other_settings_window, from_=0, to=1, orient=HORIZONTAL, resolution=.1,
                          variable=double_variable)
    volume_slider.pack()
    var = IntVar()
    save_button = submit_button = Button(other_settings_window,
                                         command=lambda: var.set(1),
                                         font=("TrebuchetMS", 10, 'bold'),
                                         text="Click Here To Save And Continue!", width="400", height="5",
                                         bd=0, bg="#32de97", activebackground="#3c9d9b", fg='#ffffff')
    save_button.pack()
    submit_button.wait_variable(var)
    new_voice_gender = variable.get()
    new_weather_city = weather_city_input.get()
    new_volume = volume_slider.get()
    if new_weather_city == "" or new_weather_city.isspace():
        showerror(title="EchoAI Settings (Personal Information)",
                  message="You Have Not Filled Everything Out Properly! Settings Will Now Exit!!")
        other_settings_window.destroy()
        button_input()
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
            "voice_gender": f"{str(gender)}",
            "volume": f"{str(new_volume)}"
        }
        settings_object = json.dumps(settings, indent=4)
        with setting_file as outfile:
            outfile.write(settings_object)
        setting_file.close()
        logging.info("New Settings Data Saved")
        showinfo(title="Settings",
                 message="Finished Saving New Personal Information! Please Restart EchoAI For Changes To Take Place!")
        other_settings_window.destroy()
        restart_echo()


def echo_help():
    list_of_modules = ["What Time Is It?", "What's The Date Today?", "Ask About A Famous Person!",
                       "What Is 0 Divided By 0?", "How Is The Weather Today?", "Tell Me A Joke!", "Tell Me A Fun Fact!",
                       "Ask A Geographical Question!"]
    list_of_tips = [
        "Ever Wondered What Your Device Is Doing In The Background? Find Out By Clicking On The Task Manager Button In The DEVICE Dropdown At The Top Of The Main Window!",
        "View Information About Your Device By Clicking The System Information Button In The DEVICE Dropdown At The Top Of The Main Window!"]  # TODO Add More Tips
    random.shuffle(list_of_modules)
    random.shuffle(list_of_tips)
    item_one = list_of_modules[0]
    item_two = list_of_modules[1]
    item_three = list_of_modules[2]
    item_four = list_of_modules[3]
    item_five = list_of_modules[4]
    tip = list_of_tips[0]
    help_window = Toplevel(root)
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
        button_input()


def exit_echo():
    exit_confirmation = askyesno(title="Exit", message="Are You Sure You Want To Exit EchoAI?")
    if exit_confirmation:
        logging.warning("Exiting EchoAI")
        root.destroy()
        exit()
    else:
        button_input()


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
                     "A Python Problem And I Cannot Do Anything About It!")
    logging.info("Starting Task Manager")
    os.system("taskmgr")


def terminal_command():
    terminal_input = askstring(title="Command", prompt="Enter A Command To Execute In Terminal!")
    if terminal_input is None or terminal_input == "EchoAI" or terminal_input == "echoai":
        button_input()
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
        button_input()


def shutdown_device():
    shutdown_confirmation = askyesno(title="Shutdown Device", message="Are You Sure You Want To Shut Down Your Device?")
    if shutdown_confirmation:
        logging.info("Shutting Down Device")
        os.system("shutdown /s /t 2")
    else:
        button_input()


def restart_device():
    restart_confirmation = askyesno(title="Restart Device", message="Are You Sure You Want To Restart Your Device?")
    if restart_confirmation:
        logging.info("Restarting Device")
        os.system("shutdown /r /t 2")
    else:
        button_input()


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
                if "Christmas" in query:
                    future = date(today.year, 12, 25)
                    diff = future - today
                    result = "It Is " + str(diff.days) + " Days Until Then!"
                    return result
                if "New Year" in query:
                    future = date(today.year, 1, 1)
                    diff = future - today
                    result = "It Is " + str(diff.days) + " Days Until Then!"
                    return result
                if "Memorial Day" in query:
                    future = date(today.year, 5, 25)
                    diff = future - today
                    result = "It Is " + str(diff.days) + " Days Until Then!"
                    return result
                if "Independence Day" in query:
                    future = date(today.year, 7, 3)
                    diff = future - today
                    result = "It Is " + str(diff.days) + " Days Until Then!"
                    return result
                if "Labor Day" in query:
                    future = date(today.year, 9, 7)
                    diff = future - today
                    result = "It Is " + str(diff.days) + " Days Until Then!"
                    return result
                if "Veterans Day" in query:
                    future = date(today.year, 11, 11)
                    diff = future - today
                    result = "It Is " + str(diff.days) + " Days Until Then!"
                    return result
                if "Thanksgiving" in query:
                    future = date(today.year, 11, 26)
                    diff = future - today
                    result = "It Is " + str(diff.days) + " Days Until Then!"
                    return result
                if "Martin Luther" in query or "MLK" in query:
                    future = date(today.year, 1, 20)
                    diff = future - today
                    result = "It Is " + str(diff.days) + " Days Until Then!"
                    return result
                if "Easter" in query:
                    future = date(today.year, 4, 4)
                    diff = future - today
                    result = "It Is " + str(diff.days) + " Days Until Then!"
                    return result
            if tag == "who am i":
                data_file = json.load(open(f"{current_directory}\\Data\\UserData.json"))
                name = data_file['name']
                nickname = data_file['nickname']
                phone_number = data_file['phone_number']
                email_address = data_file['email_address']
                home_address = data_file['home_address']
                result = f"\nYou Are {name} But Since We're Friends, I Get To Call You {nickname}" + '\n' + \
                         f"Phone Number: {phone_number}" + '\n' + f"Email Address: {email_address}" + '\n' + \
                         f"Home Address: {home_address}"
                return result
            if tag == "weather local":
                result = "Weather Has Been Disabled Due To Some Problems Which Will Be Fixed In The Next Few Updates!\n" \
                         "Sorry For The Inconvenience!"
                # TODO Fix Weather Module
                return result
            else:
                return result


def echo_response(cmd):
    logging.info("Getting EchoAI Response")
    ints = predict_class(cmd, model)
    res = get_response(ints, intents, cmd)
    return res


def button_input():
    voice_button = Button(root, font=("TrebuchetMS", 12, 'bold'), text="Click To Use!", width="500", height="50",
                          bd=0, bg="#32de97", activebackground="#3c9d9b", fg='#ffffff',
                          command=command)
    voice_button.place(y=550, x=0)


def command():
    logging.info("Button Click Detected. Now Executing Function command()")
    r = sr.Recognizer()
    mic = sr.Microphone()
    try:
        with mic as source:
            logging.info("Listening For Command")
            audio = r.listen(source, timeout=30, phrase_time_limit=3)
            cmd: str = r.recognize_google(audio)
            logging.info(f"User Said: {cmd}")
            ChatLog.config(state=NORMAL)
            ChatLog.insert(END, f"{name}: " + cmd + '\n\n')
            response = echo_response(cmd)
            ChatLog.insert(END, "ECHO: " + response + '\n\n')
            ChatLog.yview(END)
            engine.say(response)
            engine.runAndWait()
            ChatLog.config(state=DISABLED)
    except sr.UnknownValueError:
        logging.error("UnknownValueError Thrown In Function command()")
        showerror(title="EchoAI", message="I Could Not Properly Hear What You Said! Please Try Again!")
        button_input()
    except sr.RequestError:
        logging.error("RequestError Thrown In Function command()")
        showerror(title="EchoAI", message="There Was A Problem With Your Request! Please try Again Later!")
        button_input()
    except sr.WaitTimeoutError:
        logging.error("WaitTimeoutError Thrown In Function command()")
        ChatLog.insert(END, "You Took Too Long To Speak! Press The Green Button Below To Use Again!")
        button_input()


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
with log_bytes as f:
    f.seek(-2, os.SEEK_END)
    while f.read(1) != b'\n':
        f.seek(-2, os.SEEK_CUR)
    last_line = f.readline().decode()
if " - comtypes - DEBUG - CoUnititialize() done." not in last_line and "- root - WARNING - Restarting EchoAI" not in last_line and last_line != "use":
    report_bug = askyesno(title="Crash Detected",
                          message="It Appears That EchoAI Has Crashed Last Time It Was Used. Would You Like To Send A Bug Report?")
    if report_bug:
        bug_report()
log_file.truncate()
logging.info("Loading Application And GUI")
ChatLog = Text(root, bd=0, bg="white", height="8", width="50", font="TrebuchetMS")
ChatLog.config(state=DISABLED)
scrollbar = Scrollbar(root, command=ChatLog.yview)
ChatLog['yscrollcommand'] = scrollbar.set
scrollbar.place(x=480, y=0, height=550, width=20)
ChatLog.place(x=0, y=0, height=550, width=480)
menubar = Menu(root)
echo_menu = Menu(menubar, tearoff=0)
device_menu = Menu(menubar, tearoff=0)
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
menubar.add_cascade(label="ECHO", menu=echo_menu)
menubar.add_cascade(label="DEVICE", menu=device_menu)
menubar.add_cascade(label="v1.3.0", menu=version_menu)
root.config(menu=menubar)
root.protocol("WM_DELETE_WINDOW", exit_echo)
ChatLog.config(foreground="#442265", font=("TrebuchetMS", 12))
logging.info("Finished Building And Configuring GUI")
user_data_file_check = open(f"{current_directory}\\Data\\UserData.json").read()
logging.info("Checking Data To See If Set Up")
if user_data_file_check == "" or user_data_file_check.isspace():
    logging.info("User Data Not Found. Setup Incomplete")
    showinfo(title="Setup", message="You Have Not Set Up EchoAI Yet! The Following Process Will Help With Setup!")
    logging.info("Setup Prompt Shown")
    setup()
else:
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
    holidays = holidays.US()
    today = date.today()
    date_formatted = today.strftime("%m-%d-%y")
    check_holiday = date_formatted in holidays
    if check_holiday:
        ChatLog.config(state=NORMAL)
        ChatLog.insert(END, f"Have A Good {holidays.get(date_formatted)}!\n\n")
    else:
        ChatLog.config(state=NORMAL)
    ChatLog.insert(END, "Press The Green Button Below To Make Me Listen!\n\n")
    logging.info("Done With Startup. Moving Onto button_input() Function")
    ChatLog.config(state=DISABLED)
    button_input()
    root.mainloop()
