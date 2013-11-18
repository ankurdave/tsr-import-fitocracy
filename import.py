#!/usr/bin/env python2.7

from bs4 import BeautifulSoup
import datetime
import itertools
import requests
import sys
import pprint

if len(sys.argv) < 4:
    print """Usage: import.py INPUT_FILE TSR_EXERCISE_ID TSR_SESSION_COOKIE
Bench press ID: 1
Squat ID: 1429
Deadlift ID: 288
OHP ID: 975
"""
    sys.exit(1)

form_url = "http://thesquatrack.com/track"
input_file = sys.argv[1]
tsr_exercise_id = int(sys.argv[2])
tsr_session_cookie = sys.argv[3]

# Get the web form and extract its CSRF token
cookies = {'tsr_session': tsr_session_cookie}
form = requests.get(form_url, cookies=cookies)
form_soup = BeautifulSoup(form.content)
csrf_tag = form_soup.find_all(lambda t: 'name' in t.attrs and t.attrs['name'] == 'csrf_token')[0]
csrf_token = csrf_tag.attrs['value']
print "CSRF token: " + csrf_token

stop = True

with open(input_file, 'r') as f:
  lines = [line for line in f][1:]
  rows = [line.split(",") for line in lines]
  selected = [(row[1], int(row[3]), int(row[5])) for row in rows]
  selected.sort(key = lambda x: x[0])
  workouts = itertools.groupby(selected, lambda x: x[0])
  for (date, rows) in workouts:
    sets = [(row[1], row[2]) for row in rows]
    date_formatted = datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%m/%d/%Y")
    payload = {
      'csrf_token': csrf_token,
      'workout_dtm': date_formatted,
      'workout_type': 1,
      'entry[0][exercise_id]': tsr_exercise_id,
      'entry[0][block_id]': 0,
      'entry[0][superset_id]': 0,
      'entry[0][activity_id]': 0,
      'entry[0][chains]': '',
      'entry[0][chains_unit]': 4,
      'entry[0][boards]': '',
      'entry[0][boards_unit]': 4,
      'entry[0][deficit]': '',
      'entry[0][deficit_unit]': 6,
      'entry[0][comments]': '',
      'measurement[weight]': '',
      'measurement[weight_unit]': 4,
      'workout_id': '',
      'workout_comment': '',
      'publish': 'Post Workout',
      'workout_hr': '',
      'workout_min': '',
      'workout_sec': '',
      'workout_title': '',
      'exercise_search': ''
    }
    headers = {'referer': form_url}
    set_id = 0
    for weight, reps in sets:
      payload['entry[0][%d][weight]' % set_id] = weight
      payload['entry[0][%d][weight_unit]' % set_id] = 4
      payload['entry[0][%d][reps]' % set_id] = reps
      payload['entry[0][%d][reps_unit]' % set_id] = 1
      payload['entry[0][%d][rpe_unit]' % set_id] = 0
      payload['entry[0][%d][set]' % set_id] = 'work-set'
      payload['entry[0][%d][set_id]' % set_id] = ''
      payload['entry[0][%d][count]' % set_id] = 1
      set_id += 1
    pprint.pprint(payload)
    if stop:
      raw_input("Press Enter to make request...")
    response = requests.post(form_url, params=payload, cookies=cookies, headers=headers)

    if stop and raw_input("Break for debugging? [y/n] ") == 'y':
      import readline
      import code
      vars = globals().copy()
      vars.update(locals())
      shell = code.InteractiveConsole(vars)
      shell.interact()
    else:
      stop = False
