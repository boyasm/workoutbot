# DEPENDENCIES
import json
import random
import pandas as pd
from icalendar import Calendar, Event, vCalAddress, vText
from datetime import datetime, timedelta
from pathlib import Path
import os

exec(open('code/setup.py').read())

workout_now(data, data_weights, muscle_groups, always_leg, always_deadlift, deadlift_id)

workout_date = datetime.now()
format_string = "%Y-%m-%d"
then = datetime.strftime(workout_date,format_string)
message = "\'WORKOUTBOT - creating an on demand workout for " + then + "\'"
os.system("git commit workouts.ics -m "+message)
os.system("git push")