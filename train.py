import pandas as pd
from pymbta3 import Alerts, Routes, Vehicles, Predictions, Stops, Trips
at = Alerts(key = "e093857d5f6d4f0faa7f0e471aee13dd")
rt = Routes(key = "e093857d5f6d4f0faa7f0e471aee13dd")
vh = Vehicles(key = "e093857d5f6d4f0faa7f0e471aee13dd")
pr = Predictions(key = "e093857d5f6d4f0faa7f0e471aee13dd")
st = Stops(key = "e093857d5f6d4f0faa7f0e471aee13dd")
tr = Trips(key = "e093857d5f6d4f0faa7f0e471aee13dd")

import datetime
def get_train_info(train, ta):
    """
    Takes in a prediction object. Returns vehicle ID, trip ID, headsign, and time to arrival.
    """
        
    v_id = train['relationships']['vehicle']['data']['id']
    vehicle = vh.get(id = v_id)
    t_id = vehicle['data'][0]['relationships']['trip']['data']['id']
    trip = tr.get(id = t_id)
    headsign = trip['data'][0]['attributes']['headsign']
    t1 = train['attributes']['arrival_time']

    t1a = datetime.datetime.strptime(t1, "%Y-%m-%dT%H:%M:%S-%U:%W")
    dt = t1a - ta
    hours, remainder = divmod(dt.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return v_id, t_id, headsign, minutes, seconds

def remark(row):
    a = vh.get(id = row["Vehicle"])
    if a['data'][0]['attributes']['current_status'] == "STOPPED_AT":
        if (a['data'][0]['relationships']['stop']['data']['id'] == '70065') or (a['data'][0]['relationships']['stop']['data']['id'] == '70066'):
            print(a['data'][0]['relationships']['stop']['data']['id'])
            return "BRD"
    seconds = 60*int(row["Min"])+int(row["Sec"])
    if seconds < 30:
        return "ARR"
    elif seconds < 60:
        return "APCH"
    if row["Min"] > 20:
        return "20+ min"
def current_stop(row):
    vhc = vh.get(id = row["Vehicle"])
    status = vhc['data'][0]['attributes']['current_status']
    current_stop_id = vhc['data'][0]['relationships']['stop']['data']['id']
    csn = st.get(id = current_stop_id)
    current_stop_name = csn['data'][0]['attributes']['name']
    return status + " " + current_stop_name

summary = pd.DataFrame()
t = datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()
ta = datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M:%S-%U:%W")
sb = pr.get(route = "Red", stop = 70065) #Porter: Ashmont/Braintree
nb = pr.get(route = "Red", stop = 70066)

for dp in sb['data']:
    v_id, t_id, headsign, minutes, seconds = get_train_info(dp, ta)
    a = [v_id, t_id, headsign, minutes, seconds]
    summary = summary.append(pd.DataFrame([a], columns = ["Vehicle", "Trip", "Destination", "Min", 'Sec']), ignore_index=True)
    #print(v_id + "Train bound for " + headsign + " " + t_id + " departing in: " + str(minutes) + " min " + str(seconds) + " sec ")

for dp in nb['data']:
    v_id, t_id, headsign, minutes, seconds = get_train_info(dp, ta)
    a = [v_id, t_id, headsign, minutes, seconds]
    summary = summary.append(pd.DataFrame([a], columns = ["Vehicle", "Trip", "Destination", "Min", 'Sec']), ignore_index=True)
    #print(v_id + "Train bound for " + headsign + " " + t_id + " departing in: " + str(minutes) + " min " + str(seconds) + " sec ")
summary = summary.sort_values(["Min", "Sec"])
summary["Remark"] = summary.apply(lambda row: remark(row), axis = 1)
summary["Current stop"] = summary.apply(lambda row: current_stop(row), axis = 1)

def test():
    a = str(summary.iloc[1, 2]) + ' train arriving in ' + str(summary.iloc[1, 3]) + ' min ' + str(summary.iloc[1, 4]) + ' sec'
    print(a)