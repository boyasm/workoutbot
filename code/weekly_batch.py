# DEPENDENCIES
import json
import random
import pandas as pd
from icalendar import Calendar, Event, vCalAddress, vText
from datetime import datetime, timedelta
from pathlib import Path
import os
from numbers_parser import Document

exec(open('code/setup.py').read())

create_weeks(workout_days, data, data_weights, muscle_groups, always_leg, always_deadlift, deadlift_id)

next_monday = next_weekday(datetime.now(), 0)
format_string = "%Y-%m-%d"
then = datetime.strftime(next_monday,format_string)
message = "\'WORKOUTBOT - updating workouts for the week of " + then + "\'"
os.system("git commit workouts.ics -m "+message)
os.system("git push")