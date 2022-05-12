'''
DESCRIPTION
####################################################################

This program is made to work with the POMODORO techique used to 
stablish periods of focused working time and resting period

It's mainly used to balance work and rest to avoid procrastination
and burnout

I hope you enjoy this program as much as I did working to develop it

####################################################################

RESOURCES
####################################################################

https://raw.githubusercontent.com/dwyl/quotes/main/quotes.json
Quotes - Credits to the authors of this list

####################################################################

PENDING FEATURES
####################################################################
- Create a server - client relation to gather data parameters modified 
from user
'''

# Dependencies import

import time
from datetime import datetime, timedelta
import winsound
import json
from pathlib import Path
import random
import requests

# Objects


class Colors():  # This class was made to store the color attributes of the employed strings
    def __init__(self):
        self.green = '\033[1;32m'
        self.blue = '\033[34m'
        self.purple = '\033[95m'
        self.red = '\033[31m'
        self.default = '\033[0m'


colors = Colors()  # The class Colors was intanciated to call its attributes

# Config

cwd = Path.cwd()  # The CWD directorty is located so every file can be found properly
# The path for the configuration is declarated
config_path = cwd / r'resources/config.json'

# This try - except block tries to load the config.json file, in case such file is not found
# it will create it with the default values
try:
    config = json.loads(config_path.read_text())
except:
    # The used is asked for a name
    user = input('Input a user name\n')
    # The default config dict is declared
    config = {
        'work': 25,
        'rest': 5,
        'l rest': 20,
        'n pomo': 4,
        'cicles': 8,
        'log': [],
        'user': user,
    }
    # Every key/item from the default config declaration is stored at the 'log' space
    # The log list stores lists with two labes (either 'setting' or 'activity' labels):
    # SETTINGS:
    # - Type of log label (either 'setting' or 'activity' labels)
    # - The dict key of the setting updated
    # - The dict value of the setting updated
    # - The timezone where the user makes the update
    # - The timestamp from when the user makes the update
    # ACTIVITY
    # - Type of log label (either 'setting' or 'activity' labels)
    # - The time registred (in mins)
    # - The type of activity (work, rest or long rest)
    # - The n-th pomodoro
    # - The timezone where the user registers the activity
    # - The timestamp from when the user registers the activity
    for key, item in config.items():
        config['log'].append([
            'settings', str(key), str(item), time.timezone, datetime.now().timestamp()])
    config_path.write_text(json.dumps(config))

# This try - except block tries to load the quotes.json file from github, in case such file cannot be
# accesed it will load a local copy of it
try:
    # quotes.json 'raw' URL
    url_json = 'https://raw.githubusercontent.com/dwyl/quotes/main/quotes.json'
    response = requests.get(url_json)  # Requesting the content of the URL
    data = response.json()  # converting the response into a JSON
    quotes = json.loads(json.dumps(data))  # Load the JSON data
except:
    # Path declaration of the 'quotes.txt' file
    quotes_path = cwd / r'resources/quotes.txt'
    quotes = json.loads(quotes_path.read_text())  # Load the JSON data

len_quotes = len(quotes)  # Get the number of quotes
audio_path = str(cwd)+'/resources/time.wav'  # Get the notification sound
quote_shown = []  # Local list of the quotes already shown

# Functions


def activity(config):  # This function process the data stored in the log registry labeled as 'activity'
    # This record dictionary will store the sum of minutes for each activity
    record = {
        'work': 0,
        'rests': 0,
        'long rests': 0,
        'cicles': 0,
        'setings': 0,
        'activity': 0
    }
    # The log list is iterated
    for log in config['log']:
        # If the the log is labeled as 'activity' it will proceed
        if log[0] == 'activity':
            # This block of conditionals will chech for the label of the activity and will
            # sum the minutes on each activity
            record['activity'] += 1
            if log[2] == 'work':
                record['work'] += log[1]
            elif log[2] == 'rest':
                record['rests'] += log[1]
            elif log[2] == 'l rest':
                record['long rests'] += log[1]
            elif log[2] == 'cicles':
                record['cicles'] += log[1]
        elif log[1] == 'settings':
            record['setings'] += 1
    # This conditional checks if there are activity besides the default declaration at the 'log' list
    if int(config["log"][0][-1]) != int(config["log"][-1][-1]):
        # A string with a header will be declared with the beginning time of the activities and the ending time
        string = f'Record from {datetime.fromtimestamp(int(config["log"][0][-1]))} to {datetime.fromtimestamp(int(config["log"][-1][-1]))}\n'
        # The next for loop will check for the key/item pair to sum it to the header string in order to produce the report
        for key, item in record.items():
            string += f'Total minutes {key} = {item}\n'
        # A 'footer' message
        string += f'\nCongratulations {config["user"]}, you are working towards your goals\n'
    else:  # If there are not logs different from the default ones it will declare a string friendly message
        string = '\nNo activity yet, is a good time to work towards your goals!'
    # Either string will be returned (with or without activity)
    return string


def pomodoro(act_label):  # This function will recieve the type of pomodoro activity as a key and execute it

    def notification():  # This function will play a notification sound
        winsound.PlaySound(audio_path, winsound.SND_ALIAS)

    def rand_quote():  # This function will check for a quote and see if such quotes was already shown
        # This list will store for shown quotes registring its position in the 'quotes' variablr
        global quote_shown
        while True:
            # This variable stores a random value between 0 and the total of quotes
            pos = random.randint(0, len_quotes)
            if pos not in quote_shown:  # In case such quotes is not registred as shown it will proceed
                quote_shown.append(pos)  # The new quote is registred as shown
                print(colors.green + quotes[pos]['text'] + '\n' +
                      quotes[pos]['author'] + colors.default + '\n')
                break

    # This function will recieve key of the pomodoro activity, wait the minutes related and will show the progress of the timer
    def waiting_period(act_label):
        minutes = config[act_label]
        time_delta = timedelta(seconds=0)  # The baseline timer will start
        # The waiting time will be declared
        max_time = timedelta(seconds=minutes*60)
        # This for loop will wait and update a timer every second
        for _ in range(minutes*60):
            print(time_delta, ' / ', max_time, flush=True, end='\r')
            time_delta += timedelta(seconds=1)
            time.sleep(1)
        print(str(time_delta) + '\n')  # Lastly the full timer will be shown

    def logging(act_label):  # This function will log the pomodoro activity
        # Since the config['log'] will be modified it will be called as a global variable
        global config
        # The activity will be registred
        config['log'].append(['activity', config[act_label], act_label,
                             cicle, time.timezone, datetime.now().timestamp()])
        # The dictionary will be saved
        config_path.write_text(json.dumps(config))

    # In order will be executed these functions
    rand_quote()  # Displays a quote
    waiting_period(act_label)  # Displays a timer updated every second
    notification()  # It will reproduce a notification sound
    logging(act_label)  # It will register the activity


# Default mesages

# Message for the first menu
opt_str = '''1 - Start pomodoro ({} mins of work - {} mins of rest)
2 - Settings
3 - Record
4 - About
5 - Contact
X - Exit
'''

# Message for the settings menu
set_str = f'''1 - Set working time
2 - Set short rest time
3 - Set long rest time
4 - Set the number of pomodoro before a long rest (cicle)
5 - Set the number of cicles 
X - Back
'''

# Message for the about option
about_str = '''\n\nThe pomodoro technique
The Pomodoro Technique is a time management method developed by Francesco Cirillo in the late 1980s.
It uses a timer to break work into intervals, typically 25 minutes in length, separated by short breaks. 
Each interval is known as a pomodoro, from the Italian word for tomato, after the tomato-shaped kitchen timer 
Cirillo used as a university student.

The technique has been widely popularized by apps and websites providing timers and instructions. 
Closely related to concepts such as timeboxing and iterative and incremental development used in software design,
the method has been adopted in pair programming contexts.

https://en.wikipedia.org/wiki/Pomodoro_Technique

This pomodoro app has an feature where it offers an inspiring quote to start any working and resting period with
the privilege of wisdom from the universal history

The quote list comes from this source
'https://raw.githubusercontent.com/dwyl/quotes/main/quotes.json'
Credits to the authors of this list
'''

# Message for the contact option
contact_str = '''\nMy name is Wilfred, I'm a programmer developing projects to exercise my coding skills

Visit my GitHub to get other of my projects

https://github.com/WilfredM94code
'''

# Message for the exit option
exit_str = '''Thank you for using this code
Remember to visit my GitHub profile and... let\'s improve!

nhttps://github.com/WilfredM94code'''

# Program start

# Header message printed
print('\nPomodoro by WilfredM94code - Visit my GitHub profile and... let\'s improve!')
# This while loop will be interrupted if the user decides inputs the exit value
while True:
    # The menu input is requested from the user to select an option from the mail menu
    main_opt = input(
        f'\nOptions\n' + f'{opt_str}\nInput a value\n'.format(config['work'], config['rest']))
    # In case the input was either a lowe or uppercase x it will display an exit message and then it will ask for the 'enter' key to exit
    if main_opt.lower() == 'x':
        print(exit_str)
        input('Press enter to exit')
        break
    # This try - except block will try to convert the input option from the mail menu into a int
    # If it can it will proceed, otherwise it will rise an exception and then, it will restart the loop
    try:
        main_opt = int(main_opt)
        if main_opt == 1:  # If the option was 1 it will start the pomodoro
            for cicle in range(1, (config['cicles'] * config['n pomo']) + 1):
                # Work ativity
                input(
                    f'{colors.red}Time to work! - Press enter to continue - {cicle}/ {config["n pomo"] * config["cicles"]}\n{colors.default}')
                pomodoro('work')
                if cicle != 0 and cicle % config['n pomo'] == 0:
                    # Long rest
                    input(
                        f'{colors.purple}Long rest! - Press enter to continue{colors.default}\n')
                    pomodoro('l rest')
                else:
                    # Short rest
                    input(
                        f'{colors.blue}Short rest! - Press enter to continue{colors.default}\n')
                    pomodoro('rest')
        elif main_opt == 2:
            while True:
                set_opt = input(f'\nSettings\n{set_str}\nInput a value\n')
                if set_opt.lower() == 'x':
                    break
                try:
                    set_opt = int(set_opt)
                    while True:
                        try:
                            if set_opt == 1:
                                key = 'work'
                                value = int(
                                    input(f'Set working time in minutes (currently {config[key]} min)\n'))
                            elif set_opt == 2:
                                key = 'rest'
                                value = int(
                                    input(f'Set resting time in minutes (currently {config[key]} min)\n'))
                            elif set_opt == 3:
                                key = 'l rest'
                                value = int(
                                    input(f'Set long resting time in minutes (currently {config[key]} min)\n'))
                            elif set_opt == 4:
                                key = 'n pomo'
                                value = int(
                                    input(f'Set number of pomodoros before a long rest (currently {config[key]} pomodoros)\n'))
                            elif set_opt == 5:
                                key = 'cicles'
                                value = int(
                                    input(f'Set number of cicles (currently {config[key]} cicles)\n'))
                            else:
                                print('Input a useful value')
                                break
                            config[key] = value
                            config['log'].append([
                                'settings', key, value, time.tzname, time.timezone, datetime.now().timestamp()])
                            config_path.write_text(json.dumps(config))
                            print('Settings updated!')
                            break
                        except:
                            print('Input a useful value')
                except:
                    print('Input a useful value')
        elif main_opt == 3:
            print(activity(config))
        elif main_opt == 4:
            print(about_str)
            input('Press enter to continue\n')
        elif main_opt == 5:
            print(contact_str)
            input('Press enter to continue\n')
    except:
        print('Input a useful value')
