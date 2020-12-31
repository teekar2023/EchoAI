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

import pyttsx3
import holidays
import nltk
import numpy as np
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
    data_file = open(f"{current_directory}\\Data\\UserData.json", "w")
    settings_file = open(f"{current_directory}\\Data\\settings.json", "w")
    contacts_file = open(f"{current_directory}\\Data\\contacts.json", "w")
    name = askstring(title="Setup", prompt="What Is Your Name?")
    nickname = askstring(title="Setup", prompt="What Nickname Would You Like Me To Use?")
    phone_number = askstring(title="Setup", prompt="What Is Your Phone Number?")
    email_address = askstring(title="Setup", prompt="What Is Your Email Address?")
    home_address = askstring(title="Setup", prompt="What Is Your Home Address?")
    weather_city = askstring(title="Setup", prompt="What City Would You Like To See Weather Data For By Default?")
    voice_gender = askstring(title="Setup", prompt="What Gender Would You Like My Voice To Be? ('M' For Male or 'F' "
                                                   "For Female)")
    if voice_gender.upper() == "MALE" or voice_gender.upper() == "M":
        gender = 0
    else:
        gender = 1
    settings = {
        "voice_gender": f"{str(gender)}"
    }
    settings_object = json.dumps(settings, indent=4)
    with settings_file as outfile:
        outfile.write(settings_object)
    contacts_data = {
        "contacts": {
            "Me": {
                "name": f"{name}",
                "nickname": f"{nickname}",
                "phone_number": f"{phone_number}",
                "email_address": f"{email_address}",
                "home_address": f"{home_address}"
            }
        }
    }
    data = {
        "name": f"{name}",
        "nickname": f"{nickname}",
        "phone_number": f"{phone_number}",
        "email_address": f"{email_address}",
        "home_address": f"{home_address}",
        "weather_city": f"{weather_city}"
    }
    data_object = json.dumps(data, indent=4)
    with data_file as outfile:
        outfile.write(data_object)
    contacts_object = json.dumps(contacts_data, indent=4)
    with contacts_file as outfile:
        outfile.write(contacts_object)
    showinfo(title="Setup", message="Setup Completed! Please Restart!")
    restart_echo()


def reset_echo():
    reset_confirmation = askyesno(title="Reset", message="Are You Sure You Want To Reset EchoAI?")
    if reset_confirmation:
        os.remove(f"{current_directory}\\Data\\settings.json")
        os.remove(f"{current_directory}\\Data\\UserData.json")
        os.remove(f"{current_directory}\\Data\\contacts.json")
        showinfo(title="Reset",
                 message=f"Reset Successfully Completed! Please Go To {current_directory} And Delete The Folder Named "
                         f"'EchoAI' Or I Will Never Work Again!")
        root.destroy()
    else:
        showinfo(title="Reset", message="Reset Aborted!")
        button_input()


def update_echo():
    url = "http://github.com/teekar2023/EchoAI/releases/latest/"
    r = requests.get(url, allow_redirects=True)
    redirected_url = r.url
    if redirected_url != "https://github.com/teekar2023/EchoAI/releases/tag/v1.1.0":
        update_confirmation = askyesno(title="Update",
                                       message="There Is A New Version Available! Would You Like To Download It?")
        if update_confirmation:
            new_url = str(redirected_url) + "/EchoAI.exe"
            download_url = new_url.replace("tag", "download")
            webbrowser.open(download_url)
            showinfo(title="Update", message="Please Uninstall This Version And Then Install The New Version!")
            subprocess.call(f"{current_directory}\\AppData\\Local\\Programs\\EchoAI\\unins000.exe")
            root.destroy()
        else:
            showinfo(title="Update", message="Update Aborted!")
            button_input()
    else:
        showinfo(title="Update", message="There Is No New Update Available!")
        button_input()


def uninstall_echo():
    print("Calling Uninstall Executable.....")
    subprocess.call(f"{current_directory}\\unins000.exe")
    showinfo(title="Uninstall", message="Goodbye! Please Consider Emailing Me With Your Reason For Uninstalling At "
                                        "sree23palla@outlook.com")
    root.destroy()


def save_conversation():
    conversation = ChatLog.get("1.0", 'end-1c')
    file = asksaveasfile(mode="w")
    file.write(conversation)
    file.close()


def contact_developer():
    showinfo(title="Contact Developer",
             message="You Can Contact The Developer At Any Time By Email:\n sree23palla@outlook.com")
    button_input()


def changelog():
    changelog_window = Toplevel(root)
    changelog_window.title("Changelog")
    changelog_window.geometry("500x500")
    changelog_window.resizable(width=False, height=False)
    changelog_text = Label(changelog_window, text="New In EchoAI v1.1.0:\n"
                                                  "Added Update Checker!\n"
                                                  "Added Uninstall Function!\n"
                                                  "Added Terminal Command In Device Dropdown!\n"
                                                  "Added More Terminal Prints For Debugging Purposes!\n"
                                                  "Temporarily Disabled Weather Due To Some Problems!\n"
                                                  "Fixes Including Setup And Data Files!\n"
                                                  "Reset Fixes!\n"
                                                  "Added A TTS Voice!\n"
                                                  "Please Report Any Bugs On The Github Page Or Email "
                                                  "sree23palla@outlook.com\n "
                                                  "Thank You For Using EchoAI!")
    changelog_text.pack(pady=10)


def about_echo():
    about_window = Toplevel(root)
    about_window.title("About EchoAI")
    about_window.geometry("400x400")
    about_window.resizable(width=False, height=False)
    AboutText = Label(about_window,
                      text="EchoAI v1.1.0\n"
                           "Developed By: Sreekar Palla\n"
                           "Python Version: 3.8\n"
                           "Feel Free To Contact Me"
                           " For Help, Bug Reports, Or Suggestions!\n"
                           "sree23palla@outlook.com\n"
                           "Thanks For Using EchoAI!")
    AboutText.pack(pady=10)


def echo_settings():
    settings_window = Toplevel(root)
    settings_window.title("EchoAI Settings")
    settings_window.geometry("500x500")
    ComingSoon = Label(settings_window, text="Settings Window Coming Soon!")
    ComingSoon.pack(pady=10)
    # TODO


def restart_echo():
    restart_confirmation = askyesno(title="Restart", message="Are You Sure You Want To Restart EchoAI?")
    if restart_confirmation:
        os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)
    else:
        button_input()


def exit_echo():
    exit_confirmation = askyesno(title="Exit", message="Are You Sure You Want To Exit EchoAI?")
    if exit_confirmation:
        root.destroy()
    else:
        button_input()


def system_information():
    showinfo(title="System Information", message="Check The Terminal That Launched With EchoAI! DO NOT CLOSE IT UNLESS "
                                                 "YOU WANT TO CLOSE EchoAI AS WELL!")
    os.system("systeminfo")


def task_manager():
    showinfo(title="Task Manager", message="In Order To Use EchoAI Again, You Will Need To Close Task Manager! This is "
                                           "a python problem and I cannot do anything about it!")
    os.system("taskmgr")


def terminal_command():
    terminal_input = askstring(title="Command", prompt="Enter A Command To Execute In Terminal!")
    showinfo(title="System Information", message="Check The Terminal That Launched With EchoAI! DO NOT CLOSE IT UNLESS "
                                                 "YOU WANT TO CLOSE EchoAI AS WELL!")
    os.system(terminal_input)


def sign_out():
    lock_confirmation = askyesno(title="Sign Out", message="Are You Sure You Want To Sign Out Of Your Device?")
    if lock_confirmation:
        os.system("shutdown -l")
    else:
        button_input()


def shutdown_device():
    shutdown_confirmation = askyesno(title="Shutdown Device", message="Are You Sure You Want To Shut Down Your Device?")
    if shutdown_confirmation:
        os.system("shutdown /s /t 2")
    else:
        button_input()


def restart_device():
    restart_confirmation = askyesno(title="Restart Device", message="Are You Sure You Want To Restart Your Device?")
    if restart_confirmation:
        os.system("shutdown /r /t 2")
    else:
        button_input()


def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words


def bow(sentence, words, show_details):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1
                if show_details:
                    print("found in bag: %s" % w)
    return np.array(bag)


def predict_class(sentence, model):
    p = bow(sentence, words, show_details=True)
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
    print(f"Predicted Tag: {tag}")
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
            if tag == "wolframalpha":
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
                result = "Weather Has Been Disabled Due To Some Problems Which Will Be Fixed In The Next Update!\n" \
                         "Sorry For The Inconvenience!"
                # TODO
                return result
            if tag == "contacts":
                contacts_file = json.load(open(f"{current_directory}\\Data\\contacts.json"))
                contacts = contacts_file["contacts"]
                result = "Contacts Are Currently In Development And Will Be Released In A Future Update!"
                if "view" in query or "see" in query or "show" in query:
                    return result # TODO
                if "create" in query or "add" in query or "new" in query:
                    return result # TODO
                if "search" in query or "find" in query or "look" in query:
                    return result # TODO
            if tag == "goodbye":
                exit_echo()
            else:
                return result


def echo_response(cmd):
    ints = predict_class(cmd, model)
    res = get_response(ints, intents, cmd)
    return res


def button_input():
    voice_button = Button(root, font=("Verdana", 12, 'bold'), text="Click To Use!", width="500", height="50",
                          bd=0, bg="#32de97", activebackground="#3c9d9b", fg='#ffffff',
                          command=command)
    voice_button.place(y=550, x=0)


def command():
    r = sr.Recognizer()
    mic = sr.Microphone()
    try:
        with mic as source:
            audio = r.listen(source, timeout=30, phrase_time_limit=3)
            cmd: str = r.recognize_google(audio)
            print(f"{name}: {cmd}")
            ChatLog.config(state=NORMAL)
            ChatLog.insert(END, f"{name}: " + cmd + '\n\n')
            ChatLog.config(foreground="#442265", font=("Arial", 12))

            response = echo_response(cmd)
            ChatLog.insert(END, "ECHO: " + response + '\n\n')
            print(f"ECHO: {response}")
            engine.say(response)
            engine.runAndWait()

            ChatLog.yview(END)
    except sr.UnknownValueError:
        showerror(title="EchoAI", message="I Could Not Properly Hear What You Said! Please Try Again!")
        print("UnknownValueError Thrown.....")
        button_input()
    except sr.RequestError:
        showerror(title="EchoAI", message="There Was A Problem With Your Request! Please try Again Later!")
        print("RequestError Thrown.....")
        button_input()
    except sr.WaitTimeoutError:
        ChatLog.insert(END, "You Took Too Long To Speak! Press The Green Button Below To Use Again!")
        print("WaitTimeoutError Thrown!")
        button_input()


root = Tk()
root.title("EchoAI")
root.geometry("500x600")
root.resizable(width=FALSE, height=FALSE)
ChatLog = Text(root, bd=0, bg="white", height="8", width="50", font="Arial")
ChatLog.config(state=DISABLED)
scrollbar = Scrollbar(root, command=ChatLog.yview)
ChatLog['yscrollcommand'] = scrollbar.set
scrollbar.place(x=480, y=0, height=550, width=20)
ChatLog.place(x=0, y=0, height=550, width=480)
menubar = Menu(root)
echo_menu = Menu(menubar, tearoff=0)
device_menu = Menu(menubar, tearoff=0)
echo_menu.add_command(label="Save Conversation", command=save_conversation)
echo_menu.add_command(label="Contact Developer", command=contact_developer)
echo_menu.add_command(label="View Changelog", command=changelog)
echo_menu.add_command(label="About", command=about_echo)
echo_menu.add_command(label="Settings", command=echo_settings)
echo_menu.add_command(label="Update", command=update_echo)
echo_menu.add_command(label="Uninstall", command=uninstall_echo)
echo_menu.add_command(label="Reset", command=reset_echo)
echo_menu.add_command(label="Exit", command=exit_echo)
device_menu.add_command(label="Task Manager", command=task_manager)
device_menu.add_command(label="System Info", command=system_information)
device_menu.add_command(label="Terminal Command", command=terminal_command)
device_menu.add_command(label="Sign Out", command=sign_out)
device_menu.add_command(label="Shutdown Device", command=shutdown_device)
device_menu.add_command(label="Restart Device", command=restart_device)
menubar.add_cascade(label="Echo", menu=echo_menu)
menubar.add_cascade(label="Device", menu=device_menu)
root.config(menu=menubar)
current_directory = os.getcwd()
user_data_file = open(f"{current_directory}\\Data\\UserData.json").read()
if user_data_file == "":
    showinfo(title="Setup", message="You Have Not Set Up EchoAI Yet! The Following Process Will Help With Setup!")
    setup()
else:
    engine = pyttsx3.init("sapi5")
    voices = engine.getProperty('voices')
    rate = engine.getProperty('rate')
    gender_file = json.load(open(f"{current_directory}\\Data\\settings.json"))
    gender = gender_file['voice_gender']
    engine.setProperty('voice', voices[int(gender)].id)
    engine.setProperty('volume', 1.0)
    engine.setProperty('rate', 150)
    name_file = json.load(open(f"{current_directory}\\Data\\UserData.json"))
    name = name_file['name']
    holidays = holidays.US() + holidays.IN() + holidays.UK()
    today = date.today()
    date_formatted = today.strftime("%m-%d-%y")
    check_holiday = date_formatted in holidays
    if check_holiday:
        ChatLog.config(state=NORMAL)
        ChatLog.insert(END, f"Have A Good {holidays.get(date_formatted)}!\n\n")
    else:
        ChatLog.config(state=NORMAL)
    ChatLog.insert(END, "Press The Green Button Below To Make Me Listen!\n\n")
    ChatLog.config(state=DISABLED)
    button_input()
    root.mainloop()
