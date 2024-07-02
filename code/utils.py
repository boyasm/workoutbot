def lb_to_kg(lb):
    val = 0.45359237 * lb
    rd = round(val * 2) / 2
    return(rd)

def pick_group(groups, always_leg):
    selected = []
    
    groups_list = list(muscle_groups)
    groups_list_no_leg = groups_list.copy()
    groups_list_no_leg.remove('leg')

    if always_leg:
        selected = ['leg', 'leg'] + random.sample(groups_list_no_leg,k=4)
        
    else:
        selected=random.sample(groups_list,k=6)

    return(selected)

def pick_exercise(group, cutoffs, already_selected = None):
    group_cutoffs = cutoffs[group]
    selected = None
    while selected is None:
        p = random.uniform(0, 1)
        for e in group_cutoffs:
            if (p > float(group_cutoffs[e][0])) and (p < float(group_cutoffs[e][1])):
                if already_selected is None:
                    selected = e
                elif (e not in already_selected): #if the exercise has not been already chosen
                    if (e in [bardips_id, benchdips_id]) and (len([x for x in [bardips_id, benchdips_id] if x in already_selected])==0): #make sure we never get two dips
                        selected = e
                    elif (e not in [bardips_id, benchdips_id]):
                        selected = e
    return(selected)


def prepare_workout(muscle_groups, always_leg, always_deadlift, deadlift_id):
    exercise_index = 0
    exercises = []

    groups = pick_group(muscle_groups, always_leg)

    i = 0
    while (i <= 5):
        if always_leg and always_deadlift and i==0:
            exercises = exercises + [deadlift_id]
        else:
            exercises = exercises + [pick_exercise(groups[i], cutoffs, already_selected=exercises)]
        
        i += 1
    
    return(exercises)

def pick_variant(exercise, data):
    exercise = 'leg1'
    group = exercise.join(filter(lambda x: x.isalpha(), "a1a2a3s3d4f5fg6h"))

def make_workout(data, data_weights, muscle_groups, always_leg, always_deadlift, deadlift_id):
    formatNumber = lambda n: n if n%1 else int(n)

    exercises = prepare_workout(muscle_groups, always_leg, always_deadlift, deadlift_id)

    workout = {'set1': {'set1_e1' : {}, 'set1_e2': {}},
            'set2': {'set2_e1' : {}, 'set2_e2': {}},
            'set3': {'set3_e1' : {}, 'set3_e2': {}} }

    ids = [[0,1], [2,3], [4,5]]

    for e in ids:
        set_num = 'set' + str(int(e[0]/2 + 1))
        
        for i in e:
            which_exercise = e.index(i) + 1
            exercise_num = set_num + '_e' + str(int(which_exercise))

            exercise = exercises[i]

            group = "".join(filter(lambda x: x.isalpha(), exercise))
            

            # get the name
            name = data[group][exercise]["display_name"]

            # decide the variant if one exists
            v = data[group][exercise]["variant"]
            if v is not None:
                v_prob = data[group][exercise]["variant_prob"]
                variant = random.choices(v, weights=v_prob, k=1)
                eid = exercise + "-" + str(v.index(variant[0])+1)
                name = variant[0] + " " + name
            else:
                eid = exercise

            # pull in the weights based on eid
            # if not in weights spreadsheet - just reps
            if eid in data_weights.ID.values:
                w_min = formatNumber(data_weights.Min[data_weights.ID == eid].values[0])
                w_mid = formatNumber(data_weights.Mid[data_weights.ID == eid].values[0])
                w_max = formatNumber(data_weights.Max[data_weights.ID == eid].values[0])

                w = str(w_min) + "/" + str(w_mid) + "/" + str(w_max) + " (KG: " + str(formatNumber(lb_to_kg(w_min))) + "/" + str(formatNumber(lb_to_kg(w_mid))) + "/" + str(formatNumber(lb_to_kg(w_max))) + ")"
                
            else:
                w = None

            workout[set_num][exercise_num] = {"id": eid, "name": name, "weights": w}

    return(workout)


def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + timedelta(days_ahead)

def format_workout(workout):
    output_string = ""
    
    for s in ["1", "2", "3"]:
        output_string += "** SET " + s + " **\n"
        for x in ['set'+s+'_e1', 'set'+s+'_e2']:
            if workout['set'+s][x]['weights'] is None:
                stub = ""
            else:
                stub = " @ " + workout['set'+s][x]['weights']
            
            output_string += workout['set'+s][x]['name'] + stub + "\n"

    return(output_string)

def create_weeks(days, data, data_weights, muscle_groups, always_leg, always_deadlift, deadlift_id):
    # DAYS is M - SU LIKE A PELOTON WEEK

    directory = Path.cwd()

    # init the calendar
    try:
        e = open(os.path.join(directory, 'workouts.ics'), 'rb')
    except FileNotFoundError:
        print("Creating calendar")
        cal = Calendar()
    else:
        print("Opened calendar")
        cal = Calendar.from_ical(e.read())
        e.close()

    for i in range(0,7):
        if days[i]:
            workout_date = next_weekday(datetime.now(), i)
            workout = make_workout(data, data_weights, muscle_groups, always_leg, always_deadlift, deadlift_id)
            formatted_workout = format_workout(workout)

            # Add subcomponents
            event = Event()
            event.add('summary', 'Workout')
            event.add('description', formatted_workout)
            event.add('dtstart', datetime(workout_date.year,workout_date.month,workout_date.day).date())
            event.add('dtend', datetime(workout_date.year,workout_date.month,workout_date.day).date() + timedelta(days=1))

            # Add the event to the calendar
            cal.add_component(event)

    # Write to disk
    # try:
    #     directory.mkdir(parents=True, exist_ok=False)
    # except FileExistsError:
    #     print("Folder already exists")
    # else:
    #     print("Folder was created")
    
    f = open(os.path.join(directory, 'workouts.ics'), 'wb')
    f.write(cal.to_ical())
    f.close()

def workout_now(data, data_weights, muscle_groups, always_leg, always_deadlift, deadlift_id):
    #modification of create_weeks
    #stuff will need to be changed in both
    #TODO properly modularize this

    directory = Path.cwd()

    # init the calendar
    try:
        e = open(os.path.join(directory, 'workouts.ics'), 'rb')
    except FileNotFoundError:
        print("Creating calendar")
        cal = Calendar()
    else:
        print("Opened calendar")
        cal = Calendar.from_ical(e.read())
        e.close()

    workout_date = datetime.now()
    workout = make_workout(data, data_weights, muscle_groups, always_leg, always_deadlift, deadlift_id)
    formatted_workout = format_workout(workout)

    # Add subcomponents
    event = Event()
    event.add('summary', 'Workout')
    event.add('description', formatted_workout)
    event.add('dtstart', datetime(workout_date.year,workout_date.month,workout_date.day).date())
    event.add('dtend', datetime(workout_date.year,workout_date.month,workout_date.day).date() + timedelta(days=1))

    # Add the event to the calendar
    cal.add_component(event)

    # Write to disk
    # try:
    #     directory.mkdir(parents=True, exist_ok=False)
    # except FileExistsError:
    #     print("Folder already exists")
    # else:
    #     print("Folder was created")
    
    f = open(os.path.join(directory, 'workouts.ics'), 'wb')
    f.write(cal.to_ical())
    f.close()