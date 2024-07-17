#region ###########################  SOURCE DEPENDENCIES #####################  
exec(open('code/utils.py').read())
exec(open('code/params.py').read())
errormessage = ""
#endregion

#region ###########################  OPENING JSON FILE #####################  
f = open('data/exercises.json')

# returns JSON object as 
# a dictionary
data = json.load(f)

f.close()
#endregion

#region ###########################  Opening weights file #####################  
ic = "~/Library/Mobile\ Documents/com~apple~CloudDocs"
data_weights = pd.read_excel(ic + "/Weights.xlsx")
#endregion

#region ###########################  Define parameters from the exercise json #####################  
muscle_groups = data.keys()
n_exercises = {key: len(value) for key, value in data.items()}

for g in muscle_groups:
    for l in data[g]:
        d = data[g][l]['display_name']
        if d == "Deadlift":
            deadlift_id = l
        if d == "Bar Dips":
            bardips_id = l
        if d == "Bench Dips":
            benchdips_id = l

#endregion

#region ###########################  ERROR CHECKS #####################  
probcheck = {}
cutoffs = {}
cutoffs_child = {}

for group in data:
    cutoffs[group] = {} #initialize
    n = n_exercises[group]
    keys = [group+str(i) for i in range(1, n+1)]
    probs = []
    for key in keys:
        data[group][key]["prob_min"] = sum(probs) #create cumsum min
        probs.append(data[group][key]["prob"]) #append to array
        data[group][key]["prob_max"] = sum(probs) #create cumsum max
        probcheck[group] = sum(probs)
        cutoffs[group][key] = [round(data[group][key]["prob_min"], 2), round(data[group][key]["prob_max"], 2)]


nothundred = [i for i in probcheck.values() if i != 1]
if (len(nothundred) != 0):
    errormessage += "// At least one of the exercise group probabilities does not sum to 100%."


# check global inputs
if not always_leg and always_deadlift:
    errormessage += "// You have specified always_deadlift but not always a leg set. This has no corresponding logic and always_deadlift will be ignored"

#endregion
