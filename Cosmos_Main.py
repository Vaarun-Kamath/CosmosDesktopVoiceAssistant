import math
import time
import wave
import datetime
import pyaudio
import speech_recognition as sr
import pyttsx3
import webbrowser
import wikipedia
import random
import pyjokes
import os
import struct
import numpy as np
import pygame
import tkinter as tk
from tkinter.filedialog import askopenfilename
import threading
from pygame import mixer
import pygame.gfxdraw
try:
    hasInternet = True
    import pywhatkit
except Exception as ee:
    hasInternet = (
        not str(ee) == 'Error while connecting to the Internet. Make sure you are connected to the Internet!'
    )

computer = pyttsx3.init()
tts_voice = computer.getProperty('voices')
mixer.init()
assistant = 'cosmos'
aliases = ['kosmos', "cosmo's"]
voice_type = 'm'
ttspeed = (180, 175)  # speed for male, female voice
user = ''
check_for = ''
debug_mode = True  # TODO should be False
running = False
noteing = ''
talking = ''
listener = None
mic = None
stop_listening = None
freq_lines = []
dLay = 0
ambience = 2.6
command_taken = "command_taken.wav"
output_given = "command_end.wav"
info_file_path = 'cosmos_assistant.txt'
tts_wav = 'cosmos_tts.wav'
version = '0.2.0'

# list of different greetings
greeting = ('How may I be of assistance.', 'How may I help.', 'How may I serve you today.')

# {trigger : (function to open file, path)}
programs = {'word': (os.startfile, "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD"),
            'powerpoint': (os.startfile, "C:\\Program Files\\Microsoft Office\\root\\Office16\\POWERPNT"),
            'excel': (os.startfile, "C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL"),
            'browser': (os.startfile, "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave"),
            'notepad': (os.system, 'notepad'),
            'calculator': (os.system, 'calc')
            }

# banter[i] = (   ( triggers ) ,  response    )
banter = [(('how are you', 'how have you been'),
           "I am an AI I don't have feelings, of course I am sure your doing great!"),
          (('how old are you', 'what is your age'),
           'Age is just a number and I transcend SPACE and TIME!'),
          (('hello', 'hai', 'hi', 'sup', 'morning', 'evening'),
           "Hello {}"),
          (('are an invalid command', 'i hate you'),
           'ouch that hurts')
          ]

# {trigger : response}
info = {
    'song': '{} play song blank to play you that song',
    'time': '{} what is the time to know the time',
    'joke': '{} tell me a joke to hear a joke',
    'calculator': '{} calculate expression to calculate an expression',
    'help': '{} help trigger to know what the trigger does\nthe triggers are\n'
            'song time joke calculator help open note dice random name question voice terminate',
    'open': '{} run blank to run any program on your computer',
    'note': '{0} write down or {0} transcribe or {0} note down to activate note taking\n'
            'click the screen to stop note taking',
    'dice': '{} roll a dice of n sides',
    'random': '{} select a random number between x and y',
    'question': 'you can ask me any doubts',
    'name': 'you can change my name by saying\n{0} change your name to blank\nyou can change your name by saying\n'
            '{0}change my name to blank',
    'voice': 'you can change my voice by saying\n{0} change your voice to male\nor\n{0} change your voice to female',
    'terminate': 'to terminate me just say:\n{0} terminate\nor\n{0} thank you\nor\n'
                 '{0} that is all\nor\n{0} stop listening\nor\n{0} quit\nor\n{0} close',
}

# {invalid_words : valid counterparts}
operators = {
    'a': '1', 'plus': '+', '+': '+', 'and': '+', 'minus': '-', '-': '-', 'into': '*', 'x': '*', '*': '*', 'times': '*',
    'by': '/', '/': '/', 'mod': '%', 'percent': '*0.01', 'power': '**', 'square': '**2', 'cube': '**3',
    'dot': '.', 'point': '.', '.': '.', 'hole': ')', 'root': '**(-1)', 'of': '*',
    'hundred': '0' * 2, 'thousand': '0' * 3, 'lakhs': '0' * 5, 'lakh': '0' * 5, 'lacs': '0' * 5, 'lac': '0' * 5,
    'crores': '0' * 7, 'crore': '0' * 7, 'million': '0' * 6, 'billion': '0' * 9, 'trillion': '0' * 12,
    'quadrillion': '0' * 15, 'quintillion': '0' * 18, 'sextillion': '0' * 21, 'septillion': '0' * 24,
    'octillion': '0' * 27, 'nonillion': '0' * 30, 'decillion': '0' * 33, 'undecillion': '0' * 36,
    'duodecillion': '0' * 39, 'tredecillion': '0' * 42, 'quattuordecillion': '0' * 45, 'quindecillion': '0' * 48,
    'sexdecillion': '0' * 51, 'septendecillion': '0' * 54, 'octodecillion': '0' * 57, 'novemdecillion': '0' * 60,
    'vigintillion': '0' * 63, 'googol': '0' * 100, 'centillion': '0' * 303
}


# helpful command [NON-CRITICAL]
def debug(*val):
    """if 'cosmos' is in debug mode, function prints the val to the console"""
    if debug_mode:
        print(*val)


# helpful command [NON-CRITICAL]
def update(old_version='0.0.0'):
    """updates the txt file to the latest version format"""
    global user, check_for
    if old_version == '0.0.0':  # if file doesn't exist, creates file
        with open(info_file_path, 'w') as info_file:
            talk('Whats your name')
            check_for = 'update'
            while check_for:
                time.sleep(1)  # stalls till response
            info_file.write(
                f"version:{version}\nassistant:{assistant}\nuser:{user}\nalias:{','.join(aliases)}\nvoice:m")
    elif old_version == '0.1.0':  # re-formats the file to an up-to date version
        with open(info_file_path) as info_file:
            with open(f'{info_file_path[:-4]}_temp_delete.txt', 'w') as temp_file:
                for i, line in enumerate(info_file):
                    temp_file.write(
                        (f"alias:{','.join(aliases)}'\nvoice:m\n{line}", line, f'version:{version}\n')[(i != 3)+(not i)]
                    )
                if i < 3:
                    temp_file.write(f"\nalias:{','.join(aliases)}\nvoice:m")
        os.remove(info_file_path)
        os.rename(f'{info_file_path[:-4]}_temp_delete.txt', info_file_path)


def play_tune(is_end=True):
    """plays the ending/beginning tune"""
    mixer.music.load((command_taken, output_given)[is_end])
    mixer.music.play()


def listen_in(func=None):
    """makes cosmos listen in the background"""
    global mic, listener, stop_listening
    mic = sr.Microphone()
    listener = sr.Recognizer()
    with mic as source:
        listener.adjust_for_ambient_noise(source, duration=ambience)
    stop_listening = listener.listen_in_background(mic, take_command if not func else func, phrase_time_limit=10)


def replace_all(text, *values, new_value="", isword=True):
    """removes all instances of values in the text with the new_value
        if isword=True, replaces only if the word is present and not the set of characters"""
    if isword:
        return ' '.join(map(lambda x: (x, new_value)[x in [i.strip() for i in values]], text.split()))
    for value in values:
        text = text.replace(value, new_value)
    return text


def has(list1, *list2, check=any, isword=True):
    """creates a tuple of boolean values: True, if element in list2 is present in list1 else False
        and operates a given function on the iterable
        if isword=True, checks if the words in the string are present
        check=any, returns True if any item in the iterable is True else False
        check=all, returns True if all items in the iterable are True else False"""
    if is_str := type(list1) == str:
        list1 = f' {list1.strip()} '
    if isword and is_str and not any(type(i) != str for i in list2):
        list1 = list1.split()
    return check(i in list1 for i in list2)


def talk(text, with_tune=True):
    """takes in text and says the text out loud,
        also return text"""
    global talking
    can_talk = not bool(talking)
    computer.save_to_file(text, tts_wav)
    talking = True
    stop_listening(wait_for_stop=False)
    for txt in text.split('\n'):  # gives a pause at a new line
        computer.say(talking := txt)
        if can_talk:
            computer.runAndWait()
    listen_in()
    talking = ''
    if with_tune:
        play_tune()
    return text


def transcribe(recognizer, voice):
    """transcribes the converted audio to a text file"""
    global dLay
    try:
        time1 = time.time()
        txt = replace_all(recognizer.recognize_google(voice, language='en-gb').lower(), *aliases, new_value=assistant)
        debug(txt, f'\nTime taken: {(dLay := time.time() - time1)} seconds')
    except LookupError:
        return talk("Could not understand the audio")
    except sr.WaitTimeoutError:
        return debug(sr.WaitTimeoutError)
    except sr.UnknownValueError:
        return
    except sr.RequestError:
        return debug(sr.RequestError, talk('I can not understand you as there is no Internet Connection'))
    except Exception as e:
        return debug(e, "ERROR")
    if '.txt' in noteing:
        with open(noteing, 'a') as note_file:
            note_file.write(f'{txt}\n')


def welcome():
    """Welcomes the user"""
    talk(f"Hello {user}, I am {assistant.capitalize()}. \n{random.choice(greeting)}", with_tune=False)
    if not hasInternet:
        talk('You do not have an Internet connection,\nThings may not work', with_tune=False)


def visualize():
    """constantly listens and returns frequencies from the realtime waveform"""
    global freq_lines
    audio_instance = pyaudio.PyAudio()

    # stream object to get data from microphone
    audio_stream = audio_instance.open(format=pyaudio.paInt16,
                                       channels=1, rate=44100,
                                       input=True, output=True,
                                       frames_per_buffer=(chunk := 1024*2))  # samples per frame
    while running:
        data_int = [i - 128 for i in struct.unpack(f'{2 * chunk}B', audio_stream.read(chunk))]
        spec = np.abs((np.fft.fft(data_int))[:chunk]) / (chunk / 2)  # length = 2048
        angle_count = 180 + 1
        final_array = []
        prev = 0
        srt_ndx = -1
        for i in range(angle_count):  # [0-180]
            curr = int((len(spec) // 2 - 1) ** ((i + 1) / angle_count))
            bar, prev = (sum([spec[prev + j] ** 2 for j in range(curr - prev)]) ** 0.5, -1)[curr == prev], curr
            final_array.append(bar)
            if bar == -1:
                continue
            elif srt_ndx == -1:
                srt_ndx = i
            else:
                end_ndx = i
                while (end_ndx - srt_ndx - 1) > 0:
                    final_array[srt_ndx + 1] = final_array[srt_ndx] * 2 / 3
                    final_array[end_ndx - 1] = final_array[end_ndx] * 2 / 3
                    srt_ndx, end_ndx = srt_ndx + 1, end_ndx - 1
                srt_ndx = i
        freq_lines = [i for i in final_array]
    try:
        audio_stream.stop_stream()
        audio_stream.close()
        audio_instance.terminate()
    except AttributeError:
        pass


def startup():
    """runs the program"""
    global running, assistant, user, aliases, voice_type
    running = True
    must_update = False
    listen_in()

    if os.path.exists(info_file_path):
        with open(info_file_path) as info_file:
            if version != (file_version := info_file.readline().partition(':')[-1].strip()):
                must_update = True
            else:
                assistant = info_file.readline().partition(':')[-1].strip()
                user = info_file.readline().partition(':')[-1].strip()
                aliases = info_file.readline().partition(':')[-1].strip().split(',')
                voice_type = info_file.readline().partition(':')[-1].strip()[0]
                computer.setProperty('voice', tts_voice[voice_type == 'f'].id)
                computer.setProperty("rate", ttspeed[voice_type == 'f'])
                for line in info_file.readlines():
                    trigger, _, prg_path = line.partition(':')
                    programs[trigger] = (os.startfile, prg_path)
        if must_update:
            update(file_version)
    else:
        update()
    threading.Thread(target=welcome).start()
    audio_thread = threading.Thread(target=visualize)
    audio_thread.start()
    gui_startup()

    talk(f'Good Bye {user}', with_tune=False)


def gui_startup():
    """runs the GUI of COSMOS"""
    global running, talking, noteing
    background = (28,) * 3
    ofset = 3 * np.pi / 2
    freq_clr_tup = 0, 0, 0
    freq_colour = pygame.Color(freq_clr_tup)
    pygame.init()
    my_screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
    pygame.display.set_caption(assistant)
    pygame.display.set_icon(pygame.image.load('ICON.png'))

    my_screen.fill(background)
    pygame.display.update()
    ang = tic = 0
    fps = 30
    tts_ptr, tts_total_frames = 0, 1

    clock = pygame.time.Clock()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False  # closes the program (Cosmos)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False  # closes the program (Cosmos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                debug(pygame.mouse.get_pos())
                if noteing:
                    try:
                        os.startfile(noteing)
                        debug(talk('I have stopped Transcribing'))
                    except FileNotFoundError:
                        debug(talk('Transcription cancelled'))
                    noteing = ''

        if pygame.display.get_caption() != assistant:
            pygame.display.set_caption(assistant)

        my_screen.fill(background)
        mid = [i // 2 for i in my_screen.get_size()]
        min_mid = min(mid)

        # displays the lag
        delay_txt = pygame.font.SysFont('monospace', min_mid // 15)
        delay_txt.set_bold(True)
        my_screen.blit(delay_txt.render(f'ms:{round(dLay*1000,2)}', True,
                                        ('green', 'white', 'red')[(dLay > 1)+(dLay > 3)]), (35*mid[0]/20, mid[1]/40))

        # surface   co-ordinates    radius  colour
        ht_out = min_mid*4//7 + int(10 * math.sin(10 * ang))
        ht_in = min_mid*3//7 + int(10 * math.cos(10 * ang))
        tts_ht = ht_in - 20
        for i, j in enumerate(freq_lines):
            pygame.draw.aaline(my_screen, freq_colour, mid,
                               (mid[0] + (ht_out + j) * math.cos(math.radians(i) + ofset),
                                mid[1] + (ht_out + j) * math.sin(math.radians(i) + ofset)))
            pygame.draw.aaline(my_screen, freq_colour, mid,
                               (mid[0] + (ht_out + j) * math.cos(math.radians(-i) + ofset),
                                mid[1] + (ht_out + j) * math.sin(math.radians(-i) + ofset)))
        pygame.gfxdraw.aacircle(my_screen, *mid, ht_in, background)
        pygame.gfxdraw.filled_circle(my_screen, *mid, ht_in, background)
        if noteing:
            pygame.gfxdraw.aacircle(my_screen, *mid, ht_in//5, freq_clr_tup)
            pygame.gfxdraw.filled_circle(my_screen, *mid, ht_in//5, freq_clr_tup)
            note_text = delay_txt.render('Click The CENTER DOT to stop Transcribing', True, 'white')
            my_screen.blit(note_text, note_text.get_rect(center=(mid[0], mid[1] / 10)))

        if talking and os.path.exists(tts_wav) and tts_ptr < tts_total_frames:
            while True:
                try:
                    tts_wav_audio = wave.open(tts_wav, 'r')
                    tts_total_frames = tts_wav_audio.getnframes()
                    tts_chunk = tts_wav_audio.getframerate() // fps
                    tts_audio = np.frombuffer(tts_wav_audio.readframes(-1), np.int16)[tts_ptr:tts_ptr + tts_chunk]
                    tts_ptr += tts_chunk
                    tts_audio_pts = [(x * (2 * tts_ht) / tts_chunk + mid[0] - tts_ht, mid[1] - y / max(mid))
                                     for x, y in enumerate(tts_audio)]
                    if len(tts_audio_pts) > 0:
                        pygame.draw.polygon(my_screen, (255,) * 3,
                                            [(mid[0] - ht_in, mid[1]), (mid[0] - tts_ht, mid[1]), *tts_audio_pts,
                                             (mid[0] + tts_ht, mid[1]), (mid[0] + ht_in, mid[1])], 2)
                    tts_wav_audio.close()
                    break
                except PermissionError:
                    pass
        else:
            tts_ptr, tts_total_frames, talking = 0, 1, ''

        # displays cosmos's speech
        tts_font = pygame.font.SysFont('comicsans.ttf', min_mid // 10)
        tts_font.set_bold(True)
        txt_ln = ''
        txt_ofst = 0
        for wrd in talking.split():
            if (fnt_bx := tts_font.size(f'{txt_ln} {wrd}'))[0] > my_screen.get_width():
                tts_text = tts_font.render(txt_ln, True, 'white')
                my_screen.blit(tts_text, tts_text.get_rect(center=(mid[0], txt_ofst + mid[1] * 5 / 3)))
                txt_ofst += fnt_bx[1]
                txt_ln = wrd
            else:
                txt_ln += f' {wrd}'
        tts_text = tts_font.render(txt_ln, True, 'white')
        my_screen.blit(tts_text, tts_text.get_rect(center=(mid[0], txt_ofst + mid[1] * 5 / 3)))

        tic = (tic + 1) % 360
        ang = math.radians(tic)
        freq_colour.hsva = (tic, 100, 100)
        freq_clr_tup = freq_colour.r, freq_colour.g, freq_colour.b
        pygame.display.update()
        clock.tick(fps)


def take_command(recognizer, voice):
    """returns a command from the user"""
    global running, debug_mode, user, assistant, check_for, ambience, dLay
    try:
        time1 = time.time()
        command = recognizer.recognize_google(voice, language='en-gb').lower()
        ambience = min(4.0, max(2.6, ambience + ((dLay := time.time() - time1) - 3) * 0.1))
        debug(command := replace_all(command, *aliases, new_value=assistant), f'\nTime taken: {dLay} seconds')
    except LookupError:
        return talk("Could not understand the audio")
    except sr.WaitTimeoutError:
        return debug(sr.WaitTimeoutError)
    except sr.UnknownValueError:
        return
    except sr.RequestError:
        return debug(sr.RequestError, talk('I can not understand you as there is no Internet Connection'))
    except Exception as e:
        return debug(e, "ERROR")

    if check_for:
        command_update = replace_all(command, assistant, 'your', 'my', 'name', 'is').strip().lower()
        if check_for == 'update':
            user = command_update
        elif check_for[:3] == 'y/n':
            if has(command, 'yes', 'yup'):
                if int(check_for[3]):
                    user = check_for[4:]
                else:
                    assistant = check_for[4:]
        check_for = None
        return
    elif assistant not in command or (command := command.replace(assistant, '').lower().strip()) == '':
        return
    play_tune(is_end=False)
    if has(command, 'debug'):
        debug_mode = not debug_mode
        return debug(talk(f'You are {"no longer" * (not debug_mode)} in Debug Mode'))
    elif has(command, *"thank you_that is all_that's all_stop listening_chup_shut_terminate_quit_close".split('_'),
             isword=False):
        talk(("Happy to Help" if 'thank you' in command else "Okay") + f"\nTerminating {assistant}")
        stop_listening(wait_for_stop=False)
        running = False  # closes the program (Cosmos)
        return
    run_computer(command)


def run_computer(command):
    """operates certain functions depending on the users' command"""
    global assistant, user, check_for, voice_type, noteing

    # checks if certain triggers are present in the command and gives an appropriate response
    bantered = False
    for value in banter:
        if has(command, *value[0], isword=False):
            talk(value[1].format(user), with_tune=False)
            command = replace_all(command, *value[0], isword=False)
            bantered = True
    if bantered:
        return talk('')

    # checks for a song to play
    if has(command, 'play', 'song', check=all):
        debug(talk("Playing" + (song := replace_all(command, "play", "song"))))
        pywhatkit.playonyt(song)

    # checks if the time is requested
    elif 'time' in command and has(command, 'what is ', "what's ", 'tell ', isword=False):
        debug(talk('The time is ' + datetime.datetime.now().strftime('%I:%M %p')))

    # checks if a doubt is queried
    elif has(command, 'search', 'who', 'what', 'when', 'how', 'why'):
        search = replace_all(command, *'search what who is was will did about how for when'.split())
        talk("Searching about " + search, with_tune=False)
        webbrowser.open("https://www.google.com/search?q=" + search)
        if has(command, 'who is ', 'what is ', 'who are ', 'when was ', isword=False):
            try:
                talk(wikipedia.summary(search, 1), with_tune=False)
            except wikipedia.exceptions.DisambiguationError as e:
                debug(e, ": No Info on Search...\n Opening Google")
            except wikipedia.exceptions.PageError as e:
                debug(e, ": No Info on search...\n Opening Google")
            except Exception as e:
                debug(e)
        play_tune()

    # tells a joke
    elif has(command, 'tell', 'joke', check=all):
        debug(talk(pyjokes.get_joke()))

    # rolls a n-sided dice and gives the outcome
    elif has(command := command.replace('dice', 'die'), 'roll', 'die', check=all):
        is_num = False
        for i in command.split():
            if i.isnumeric():
                talk(f'The {i} sided dice landed on {random.randint(1, int(i))}')
                is_num = True
                break
        if not is_num:
            talk(f'The dice landed on {random.randint(1, 6)}')

    # Selects a random number within range
    elif has(command, 'random', 'number', check=all):
        rng = [int(i) for i in command.split() if not i.isalpha()][:2]
        talk(f'Okay, The random number is: {random.randint(min(rng), max(rng))}')

    # opens/runs the requested program
    elif has(command, 'open', 'run'):
        command = replace_all(
            replace_all(command, 'open', 'run').replace('world', 'word'), *'google chrome web brave'.split(),
            new_value='browser')
        if has(command, *programs.keys()):
            for prog in list(set(programs.keys()) & set(command.split())):
                talk(f'Opening {prog}')
                programs[prog][0](programs[prog][1])
        else:
            # open a file and accept key=keyword/callword:value=path
            tk.Tk().withdraw()
            if prog_path := askopenfilename():
                with open(info_file_path, 'a') as info_file:
                    command = replace_all(command, *programs.keys())
                    info_file.write(f'\n{(trigger := command.split()[0])}:{prog_path}')
                programs[trigger] = (os.startfile, prog_path)
                os.startfile(prog_path)

    # takes down notes for you
    elif has(command, 'transcribe', 'note', 'write', 'right'):
        noteing = f"Cosmos_notes{datetime.datetime.now().strftime('%H_%M_%S_%f %d-%m-%Y')}.txt"
        talk('I have started Transcribing')
        stop_listening(wait_for_stop=False)
        listen_in(transcribe)

    # changes either assistants's or user's name
    elif has(command, 'change', 'name', check=all):
        typ = [assistant, user]
        typ_name = ('your', 'my', 'assistant', 'user')
        if not has(command, *typ_name):
            return talk(f"I am sorry, I do not know whose name to change\n{info['name'].format(assistant)}")
        is_user = has(command, typ_name[1], typ_name[3])
        command = replace_all(command, 'change', 'name', 'to', *typ_name).strip()
        talk(f"Would you like {typ_name[not is_user]} name to change from {typ[is_user]} to {command}")
        check_for = f'y/n{int(is_user)}{command}'
        while check_for:
            time.sleep(1)
        typ = [assistant, user]
        talk(f"{typ_name[not is_user].capitalize()} name is set to {(typ[is_user])}")
        # editting line 2 or 3 of the ifo_file using a temporary file
        with open(info_file_path) as info_file:
            with open(f'{info_file_path[:-4]}_temp_delete.txt', 'w') as temp_file:
                for i, line in enumerate(info_file):
                    temp_file.write(f'{typ_name[2 + is_user]}:{typ[is_user]}\n' if i == (1 + is_user) else line)
        os.remove(info_file_path)
        os.rename(f'{info_file_path[:-4]}_temp_delete.txt', info_file_path)

    # changes Voice
    elif has(command, 'change', 'voice', check=all):
        typ = replace_all(replace_all(command, 'change', 'voice', 'your', 'to'),
                          'mail', 'male', new_value='m').replace('female', 'f')
        if typ in ('m', 'f'):
            computer.setProperty('voice', tts_voice[(is_female := typ == 'f')].id)
            computer.setProperty("rate", ttspeed[(is_female := typ == 'f')])
            with open(info_file_path) as info_file:
                with open(f'{info_file_path[:-4]}_temp_delete.txt', 'w') as temp_file:
                    for i, line in enumerate(info_file):
                        temp_file.write(f'voice:{(voice_type := ("m", "f")[is_female])}\n' if i == 4 else line)
            os.remove(info_file_path)
            os.rename(f'{info_file_path[:-4]}_temp_delete.txt', info_file_path)
            talk('hello, This is the sound of my voice')
        else:
            talk(f"I am sorry, I do not know which voice to change to\n{info['voice'].format(assistant)}")

    # evaluates a simple expression
    elif has(command, 'calculate', 'evaluate'):
        command = replace_all(command, 'calculate', 'evaluate', 'expression', 'the')
        command = command.replace('whole', 'hole').replace('squared', 'square').replace('cubed', 'cube').strip()
        elems = command.split()
        i = 0
        while i < len(elems):
            debug(elems)
            if not (val := operators.get(elems[i])) and elems[i].isalpha():
                elems.pop(i)
            else:
                elems[i] = val if val else elems[i].replace('%', '*0.01')
                i += 1
        command = ''.join(elems)
        command = '(' * (command.count(')')-command.count('(')) + command.replace('***', '**')
        try:
            debug(command, '=', talk(str(eval(command))))
        except Exception as e:
            debug(talk(str(e)))

    # tells the user the commands and their Syntax
    elif has(command, 'help'):
        talk('hey, did you know that you can ask me questions like', with_tune=False)
        if not len(triggers := set(command.replace('help', '', 1).split()) & set(info.keys())):
            triggers = info.keys()
        for trigger in triggers:
            talk(info[trigger].format(assistant), with_tune=False)
        talk("but remember to always say my name otherwise it doesn't count")

    # checks if cosmos is called with an invalid command
    elif running:
        talk(f'{command} is an invalid command')


if __name__ == '__main__':
    startup()
