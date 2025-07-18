# example scripts to interface Visum with PTV Flows - pull flows kpi data and display heatmap and speed profile for a selected PrT Path
# chetan joshi, ptv portalnd or 7/1/2025

import requests
import json 
from osgeo import ogr
from datetime import tzinfo, timedelta, datetime, timezone
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from tkinter import *
from tkinter import ttk
import os

PRIO = 20480
# import tkinter as tk
# from tkcalendar import DateEntry
key  = Visum.Net.AttValue("FLOWSKEY") #"your PTV FLOWS api KEY here"


# Define the colormap
cdict = {
    'red':   [(0.0, 0.0, 0.0),  # Green at 0
              (0.33, 1.0, 1.0), # Yellow at 0.33
              (0.66, 1.0, 1.0), # Red at 0.66
              (1.0, 1.0, 1.0)], # Orange at 1
    'green': [(0.0, 1.0, 1.0),  # Green at 0
              (0.33, 1.0, 1.0), # Yellow at 0.33
              (0.66, 0.0, 0.0), # Red at 0.66
              (1.0, 0.5, 0.5)], # Orange at 1
    'blue':  [(0.0, 0.0, 0.0),  # Green at 0
              (0.33, 0.0, 0.0), # Yellow at 0.33
              (0.66, 0.0, 0.0), # Red at 0.66
              (1.0, 0.0, 0.0)]  # Orange at 1
}

custom_cmap = colors.LinearSegmentedColormap('CustomMap', cdict)


def convert_minutes_to_time(minutes):
    hours = minutes // 60
    remaining_minutes = minutes % 60
    return "{:02d}:{:02d}".format(hours, remaining_minutes)

def pull_corridor_kpi():
    
    marked = Visum.Net.Marking.GetAll
    kpiId  = marked[0].AttValue("kpiId")

    status.config(text= "Extracting results for path: {}".format(marked[0].AttValue("NAME")))
    ws.update()

    utc_offset = -7
    # result.keys -> dict_keys(['name', 'notes', 'kpiInstanceParameters', 'location', 'kpiId', 'thresholdsDefinition', 'template', 'direction', 'visualizationModes', 'unitOfMeasure'])
    timestamps = dict()
    ti_result  = dict()

    resp  = requests.get(url='https://api.ptvgroup.tech/kpieng/v1/result/by-kpi-id?kpiId={}&apiKey={}'.format(kpiId, key))
    result= json.loads(resp.text)

    timestamps[kpiId] = []
    ti_result[kpiId]  = [] 

    cnt   = 0 
    total = 0
    min_time = 999
    max_time = 0
    num_timestamps = len(result)
    
    for x in result:
        # print (x['overallResult']['value'])
        travel_time = x['overallResult']['value']
        total+=travel_time
        cnt+=1
        if travel_time < min_time:
            min_time = travel_time
        
        if travel_time > max_time:
            max_time = travel_time

        parsed_datetime = datetime.fromisoformat(x['timeStamp'].replace('Z', '+00:00'))
        local_timezone = ZoneInfo("America/Los_Angeles")
        local_datetime = parsed_datetime.astimezone(local_timezone)
        local_datetime.strftime("%H:%M:%S")
        local_datetime.isoweekday() #-> Monday =1... Sunday =7
        
        #APPLY SOME OTHER FILTERS HERE...
        # if (parsed_datetime.day, parsed_datetime.month, parsed_datetime.year) == (4, 4, 2025):
        if local_datetime.isoweekday() < 6:
            progressive_result = x['results']

            # ti = parsed_datetime.hour*60 + parsed_datetime.minute
            # ti = (24*60+ti + utc_offset*60)%(24*60)
            ti = local_datetime.hour*60 + local_datetime.minute
            ti_result[kpiId].append([ti, travel_time])

            prev_dist = 0
            for row in progressive_result:
                #parsed_datetime.hour,
                dist = row['progressive']-prev_dist
                # tx = parsed_datetime.hour
                tx = local_datetime.hour
                # timestamps[kpiId].append([row['progressive'], ti, row['value'], round(0.602*60*dist/row['value'],2), (24+tx + utc_offset)%24]) 
                timestamps[kpiId].append([row['progressive'], ti, row['value'], round(0.602*60*dist/row['value'],2), tx]) 
                prev_dist = row['progressive']

    average_time = round(total / cnt, 2)
    default_time = round(x['overallResult']['defaultValue'], 2)

    Visum.Log(PRIO, "typical time: {} mins, average time: {} mins".format(default_time, average_time))


    data_flat = pd.DataFrame(timestamps[kpiId], columns=["progressive", "timestamp", "T", "V", "hour"])
    # data_flat.to_csv(r"D:\PTV_OneDrive\OneDrive - PTV Group\Scripting\datasets\heatmap.csv")
    heatmap_data = pd.pivot_table(data_flat, values='V', index='progressive', columns='timestamp', aggfunc="mean")

    trav_time_ti = heatmap_data.to_numpy()
    column_names = heatmap_data.columns
    row_names    = heatmap_data.index

    fig, (ax0, ax1) = plt.subplots(2, 1)
    fig.suptitle("Segment speed profile")
    # ax = fig.add_axes() #[0,0,1.5,1])
    # fig.add_axes()
    im = ax0.imshow(heatmap_data, cmap=custom_cmap.reversed(), interpolation='nearest') #'bilinear'
    xix = np.arange(0,len(column_names),12)
    ax0.set_xticks(xix)
    ax0.set_xticklabels([convert_minutes_to_time(column_names[i]) for i in xix], rotation=45)

    yix = np.arange(0, len(row_names), 10)
    ax0.set_yticks(yix)
    ax0.set_yticklabels([round(row_names[i],2) for i in yix])

    # ax0.set_xlabel("Time progression", size=10)
    ax0.set_ylabel("Distance along path", size=10)
    cb = fig.colorbar(im, shrink=1.0)
    cb.ax.set_ylabel('Speed')
    # cb.ax0.set_ylabel('Speed')
    result = trav_time_ti.mean(0)
    # ax2 = plt.subplot(212, sharex=ax1)
    ax1.plot(np.arange(len(result)), result)
    ax1.set_xticks(xix)
    ax1.set_xticklabels([convert_minutes_to_time(column_names[i]) for i in xix], rotation=45)
    ax1.grid(True)
    ax1.set_xlabel("Time slice", size=10)
    ax1.set_ylabel("Speed (mph)", size=10)

    # Calculate the proper aspect for the second axes
    # aspect0 = ax0.get_aspect()
    # if aspect0 == 'equal':
    #     aspect0 = 1.0
    # dy = np.abs(np.diff(ax1.get_ylim()))
    # dx = np.abs(np.diff(ax1.get_xlim()))

    # aspect = aspect0 / (float(dy) / dx)
    # ax1.set_aspect(aspect)
    ax0.set_aspect('auto')

    # Visum.Log(PRIO, (ax0.get_aspect(), ax1.get_aspect()))
    
    plt.tight_layout()
    plt.show()

    status.config(text= "Done!")
    # ws.grab_set()


# kpiId = '15a5cc7a-0fc9-499f-8b6c-0e414ec2b6e7'
# kpiId = '69bac442-558a-47ad-a0ba-1ab89fe1cb62'
# pull_corridor_kpi(kpiId)

def cancel():
    print (os.getcwd())
    ws.destroy()


# --------------------------------------------------------- GUI BODY ---------------------------------------------------------------------- #
ws = Tk()

ws.title("Flows-API: KPIs")
# ws.grab_set()
# ws.focus_set()
Label(ws, text="Select PrT Path & Click Run:").grid(row=0, column=0, sticky=W, padx=2, pady=2)
status = Label(ws)
status.grid(row=11, column=1, sticky=W, padx=2, pady=2)

# text_area = scrolledtext.ScrolledText(ws, wrap=NONE, 
#                                       width=50, height=10, bg = "black", fg="white")

# text_area.grid(row=1, column=1, sticky=NSEW, pady=10, padx=10) 
# text_area.config(state= DISABLED)

ws.grid_columnconfigure(1, weight=1)
ws.grid_rowconfigure(1, weight=1)


Button(ws, text="Run", height= 1, width=7, command = pull_corridor_kpi).grid(row=2, column=1, sticky=E, padx=5, pady=5)
Button(ws, text="Exit", height= 1, width=7, command = cancel).grid(row=2, column=2, sticky=E, padx=5, pady=5)

ws.mainloop()
