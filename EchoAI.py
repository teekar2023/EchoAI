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
import time
from datetime import date
from tkinter import *
from tkinter.filedialog import asksaveasfile
from tkinter.messagebox import showerror, showinfo, askyesno
from tkinter.simpledialog import askstring

import holidays
import nltk
import numpy as np
import speech_recognition as sr
import weather_forecast as wf
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
    os.mkdir(f"{current_directory}\\EchoAI")
    data_file = open(f"{current_directory}\\EchoAI\\UserData.json", "w+")
    settings_file = open(f"{current_directory}\EchoAI\\settings.json", "w+")  # TODO Use This For Settings!
    settings_file.close()
    name = askstring(title="Setup", prompt="What Is Your Name?")
    phone_number = askstring(title="Setup", prompt="What Is Your Phone Number?")
    email_address = askstring(title="Setup", prompt="What Is Your Email Address?")
    home_address = askstring(title="Setup", prompt="What Is Your Home Address?")
    weather_city = askstring(title="Setup", prompt="What City Would You Like To See Weather Data For By Default?")
    data = {
        "name": f"{name}",
        "phone_number": f"{phone_number}",
        "email_address": f"{email_address}",
        "home_address": f"{home_address}",
        "weather_city": f"{weather_city}"
    }
    json_object = json.dumps(data, indent=4)
    with data_file as outfile:
        outfile.write(json_object)
    showinfo(title="Setup", message="Setup Completed! EchoAI Will Now Restart!")
    restart_echo()


def reset_echo():
    reset_confirmation = askyesno(title="Reset", message="Are You Sure You Want To Reset EchoAI?")
    if reset_confirmation:
        os.remove(f"{current_directory}\\EchoAI\\settings.json")
        os.remove(f"{current_directory}\\EchoAI\\UserData.json")
        showinfo(title="Reset", message=f"Reset Successfully Completed! Please Go To {current_directory} And Delete The Folder Named 'EchoAI' Or I Will Never Work Again!")
        base.destroy()
    else:
        showinfo(title="Reset", message="Reset Aborted!")
        button_input()


def save_conversation():
    conversation = ChatLog.get("1.0", 'end-1c')
    file = asksaveasfile(mode="w")
    file.write(conversation)
    file.close()


def contact_developer():
    showinfo(title="Contact Developer",
             message="You Can Contact The Developer At Any Time By Email:\n sree23palla@gmail.com")
    button_input()


def about_echo():
    about_window = Toplevel(base)
    about_window.title("About EchoAI")
    about_window.geometry("400x400")
    about_window.resizable(width=False, height=False)
    AboutText = Label(about_window,
                      text="EchoAI v1.0\nDeveloped By: Sreekar Palla\nPython Version: 3.8\n Feel Free To Contact Me For"
                           " Help, Bug Reports, Or Suggestions!\nsree23palla@gmail.com!\nThanks For Using EchoAI!")
    AboutText.pack()


def echo_settings():
    settings_window = Toplevel(base)
    settings_window.title("EchoAI Settings")
    settings_window.geometry("500x500")
    ComingSoon = Label(settings_window, text="Settings Window Coming Soon!")
    ComingSoon.pack()


def restart_echo():
    exit_confirmation = askyesno(title="Restart", message="Are You Sure You Want To Restart EchoAI?")
    if exit_confirmation:
        print("Restarting.....")
        os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)
    else:
        button_input()


def exit_echo():
    exit_confirmation = askyesno(title="Exit", message="Are You Sure You Want To Exit EchoAI?")
    if exit_confirmation:
        print("Exiting.....")
        base.destroy()
    else:
        button_input()


def system_information():
    showinfo(title="System Information", message="Check The Terminal That Launched With EchoAI! DO NOT CLOSE IT UNLESS "
                                                 "YOU WANT TO CLOSE EchoAI AS WELL!!!")
    os.system("systeminfo")


def task_manager():
    showinfo(title="Task Manager", message="In Order To Use EchoAI Again, You Will Need To Close Task Manager! This is "
                                           "a python problem and I cannot do anything about it!")
    os.system("taskmgr")


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


def bow(sentence, words, show_details=True):
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
    p = bow(sentence, words, show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list


def get_response(ints, intents_json, query):
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
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
                data_file = json.load(open(f"{current_directory}\\EchoAI\\UserData.json"))
                name = data_file['name']
                phone_number = data_file['phone_number']
                email_address = data_file['email_address']
                home_address = data_file['home_address']
                result = f"Name: {name}" + '\n' + f"Phone Number: {phone_number}" + '\n' + f"Email Address: {email_address}" + '\n' + f"Home Address: {home_address}"
                return result
            if tag == "weather local":
                data_file = json.load(open(f"{current_directory}\\EchoAI\\UserData.json"))
                city = data_file['weather_city']
                if "tomorrow" in query or "week" in query:
                    result = wf.forecast(place=str(city), forecast="weekly")
                    return result
                else:
                    result = wf.forecast(place=str(city), forecast="daily")
                    return result
            if tag == "contacts":
                result = "This Is Coming Soon!"
                return result
            if tag == "goodbye":
                exit_echo()
            else:
                return result


def EchoAI_response(cmd):
    ints = predict_class(cmd, model)
    res = get_response(ints, intents, cmd)
    return res


def button_input():
    SendButton = Button(base, font=("Verdana", 12, 'bold'), text="Click To Use!", width="500", height="50",
                        bd=0, bg="#32de97", activebackground="#3c9d9b", fg='#ffffff',
                        command=command)
    SendButton.place(y=550, x=0)


def command():
    name_file = json.load(open(f"{current_directory}\\EchoAI\\UserData.json"))
    name = name_file['name']
    r = sr.Recognizer()
    mic = sr.Microphone()
    try:
        with mic as source:
            audio = r.listen(source, timeout=30)
            cmd: str = r.recognize_google(audio)
            ChatLog.config(state=NORMAL)
            ChatLog.insert(END, f"{name}: " + cmd + '\n\n')
            ChatLog.config(foreground="#442265", font=("Comic Sans MS", 12))

            response = EchoAI_response(cmd)
            ChatLog.insert(END, "ECHO: " + response + '\n\n')

            ChatLog.config(state=DISABLED)
            ChatLog.yview(END)
    except sr.UnknownValueError:
        showerror(title="EchoAI", message="I Could Not Properly Hear What You Said!")
        button_input()
    except sr.RequestError:
        showerror(title="EchoAI", message="There Was A Problem With Your Request! Please try Again Later!")
        button_input()
    except sr.WaitTimeoutError:
        ChatLog.insert(END, "You Took Too Long To Speak! Press The Button To Use Again!")


base = Tk()
base.title("EchoAI")
base.geometry("500x600")
base.resizable(width=FALSE, height=FALSE)

ChatLog = Text(base, bd=0, bg="white", height="8", width="50", font="Verdana", )

ChatLog.config(state=DISABLED)

scrollbar = Scrollbar(base, command=ChatLog.yview)
ChatLog['yscrollcommand'] = scrollbar.set

scrollbar.place(x=480, y=0, height=550, width=20)
ChatLog.place(x=0, y=0, height=550, width=480)
menubar = Menu(base)
echo_menu = Menu(menubar, tearoff=0)
device_menu = Menu(menubar, tearoff=0)
echo_menu.add_command(label="Save Conversation", command=save_conversation)
echo_menu.add_command(label="Contact Developer", command=contact_developer)
echo_menu.add_command(label="About", command=about_echo)
echo_menu.add_command(label="Settings", command=echo_settings)
echo_menu.add_command(label="Reset", command=reset_echo)
echo_menu.add_command(label="Restart", command=restart_echo)
echo_menu.add_command(label="Exit", command=exit_echo)
device_menu.add_command(label="Task Manager", command=task_manager)
device_menu.add_command(label="System Info", command=system_information)
device_menu.add_command(label="Sign Out", command=sign_out)
device_menu.add_command(label="Shutdown Device", command=shutdown_device)
device_menu.add_command(label="Restart Device", command=restart_device)
menubar.add_cascade(label="Echo", menu=echo_menu)
menubar.add_cascade(label="Device", menu=device_menu)
base.config(menu=menubar)
current_directory = os.getcwd()
if not os.path.exists(f"{current_directory}\\EchoAI"):
    showinfo(title="Setup", message="You Have Not Set Up EchoAI Yet! The Following Process Will Help With Setup!")
    setup()
else:
    name_file = json.load(open(f"{current_directory}\\EchoAI\\UserData.json"))
    name = name_file['name']
    holidays = holidays.US() + holidays.IN() + holidays.UK()
    today = date.today()
    date_formatted = today.strftime("%m-%d-%y")
    check_holiday = date_formatted in holidays
    if check_holiday:
        ChatLog.config(state=NORMAL)
        ChatLog.insert(END, f"Have A Good {holidays.get(date_formatted)}")
    else:
        ChatLog.config(state=NORMAL)
    ChatLog.insert(END, "Press The Green Button Below To Make Me Listen!\n\n")
    ChatLog.config(state=DISABLED)
    button_input()
    base.mainloop()
