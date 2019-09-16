import json
import random
from dadjokes import Dadjoke
import pyjokes
from ev3dev2.sound import Sound
import platform
import glob
import os

if platform == 'Linux-4.4.87-22-ev3dev-ev3-armv5tejl-with-debian-8.5':
    base_folder = "code"
else:
    import getpass

    username = getpass.getuser()
    if username == "simon":
        base_folder = r"C:\Users\simon\OneDrive - Syddansk Universitet\Studie\7 semester\AI\AIGit\code"

platform = platform.platform()

sound = Sound()

with open('code/jokes/overview.json') as json_file:
    overview = json.load(json_file)

with open('code/jokes/sounds.json') as json_file:
    sounds_overview = json.load(json_file)


def play_sound(sound_file):
    if platform == 'Linux-4.4.87-22-ev3dev-ev3-armv5tejl-with-debian-8.5':
        sound.play_file(sound_file, play_type=sound.PLAY_NO_WAIT_FOR_COMPLETE)
    else:
        from playsound import playsound
        playsound(sound_file)


def speak(text):
    import pyttsx3
    if platform == 'Linux-4.4.87-22-ev3dev-ev3-armv5tejl-with-debian-8.5':
        sound.speak(text, play_type=sound.PLAY_NO_WAIT_FOR_COMPLETE)
    else:
        import pyttsx3
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()


def play_joke(joke_group=None):
    if joke_group is None:
        joke_group = random.choice(list(overview.keys()))

    joke_sub_group = random.choice(overview[joke_group])

    if "module." in joke_sub_group:
        _, joke_module = joke_sub_group.split(".")

        if joke_module == "dadjokes":
            dad_joke = Dadjoke()
            joke = dad_joke.joke

        if joke_module == "pyjokes":
            joke = pyjokes.get_joke()

        speak(joke)

    elif "sound." in joke_sub_group:

        _, sound_group = joke_sub_group.split(".")

        sound_files = sounds_overview[sound_group]
        sound_file = random.choice(sound_files)

        if "folder." in sound_file:
            _, sound_folder_path = sound_file.split(".")

            sound_folder_path = base_folder + "/jokes/sounds/" + sound_folder_path + "/*"
            files = glob.glob(sound_folder_path)

            if len(files) == 0:
                print("No files found", "Looking in ", sound_folder_path)
                return
            sound_file = random.choice(files)
        else:
            sound_file = base_folder + "/" + sound_file
        ext = sound_file.split(".")[-1]

        if ext != "wav":
            print("The sound file has to be a wav file")
            return
        play_sound(sound_file)

    else:
        with open(joke_sub_group) as fp:
            jokes = fp.readlines()

        joke = random.choice(jokes)
        speak(joke)


if __name__ == "__main__":
    play_joke("start_up")
    play_joke("end")
    play_joke("sounds")
    play_joke("random")
    play_joke("test")
