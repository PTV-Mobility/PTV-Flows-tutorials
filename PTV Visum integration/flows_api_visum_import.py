# example scripts to interface Visum with PTV Flows - import corridors defined in a Flows instance into Visum as PrT paths and set some path data.
# chetan joshi, ptv portalnd or 7/1/2025

import requests
import json 
from osgeo import ogr
from datetime import tzinfo, timedelta, datetime, timezone
from zoneinfo import ZoneInfo
import time
import numpy as np
import csv

PRIO = 20480

key  = Visum.Net.AttValue("FLOWSKEY")
match_tsys = Visum.Net.AttValue("MATCH_TSYS") #"h"

# NOTES: 
#   KPI Path result: requests.get(url='https://api.ptvgroup.tech/kpieng/v1/result/by-kpi-id?kpiId={}&apiKey={}'.format(kpiId, key))
#       returns results for each time stamp / TI -> 
#           keys: 
#           'kpiId', 
#           'timeStamp', 
#           'results', -> results for each segment of path: ['value', 'defaultValue', 'unusualValue', 'averageValue', 'progressive'] 
#           'overallResult'  -> average over all path segments: ['value', 'defaultValue', 'unusualValue', 'averageValue', 'progressive'] 
day_name = {0: '', 1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday', 5: 'Friday', 6: 'Saturday', 7: 'Sunday'}

def convert_minutes_to_time(minutes):
    hours = minutes // 60
    remaining_minutes = minutes % 60
    return "{:02d}:{:02d}".format(hours, remaining_minutes)

def collect_path_results(kpiId, days=[1, 2, 3, 4, 5, 6, 7]):
    resp  = requests.get(url='https://api.ptvgroup.tech/kpieng/v1/result/by-kpi-id?kpiId={}&apiKey={}'.format(kpiId, key))
    
    ti_result = []

    if resp.status_code == 200:
        path_result = json.loads(resp.text)
        
        for _result in path_result:
            parsed_datetime= datetime.fromisoformat(_result['timeStamp'].replace('Z', '+00:00'))
            local_timezone = ZoneInfo("America/Los_Angeles")
            local_datetime = parsed_datetime.astimezone(local_timezone)
            local_datetime.strftime("%H:%M:%S")
            # print (_result['timeStamp'], _result['overallResult'])
            if local_datetime.isoweekday() in days:
                ti_result.append([kpiId, local_datetime.ctime(), day_name[local_datetime.isoweekday()], local_datetime.strftime("%H:%M:%S"), 
                                  _result['overallResult']['value'],
                                  _result['overallResult']['defaultValue'],
                                  _result['overallResult']['unusualValue'],
                                  _result['overallResult']['averageValue'],
                                  _result['overallResult']['progressive']] )
                
            # ('2025-04-06T15:32:00Z', '08:32:00', {'value': 6.63083, 'defaultValue': 5.115329, 'unusualValue': 10.769688, 'averageValue': 7.2641454, 'progressive': 6.6872616})
    # return average_time, max_time, worst_hr, worst_day
    return ti_result


#-> Monday =1... Sunday =7
def get_path_results(kpiId, days=[1, 2, 3, 4, 5, 6, 7]):
    resp  = requests.get(url='https://api.ptvgroup.tech/kpieng/v1/result/by-kpi-id?kpiId={}&apiKey={}'.format(kpiId, key))
    average_time = 0
    max_time = 0
    worst_hr = 0
    worst_day= 0

    if resp.status_code == 200:
        try:
            path_result = json.loads(resp.text)
            running_total = 0
            nobs = 0
            trav_time_hr = np.zeros((24, 2))
            for _result in path_result:
                print (_result['timeStamp'], _result['overallResult'])
                parsed_datetime= datetime.fromisoformat(_result['timeStamp'].replace('Z', '+00:00'))
                local_timezone = ZoneInfo("America/Los_Angeles")
                local_datetime = parsed_datetime.astimezone(local_timezone)
                local_datetime.strftime("%H:%M:%S")
                if local_datetime.isoweekday() in days:
                    xtime    = _result['overallResult']['averageValue']
                    # trav_time_hr.append([local_datetime.hour, xtime])
                    trav_time_hr[local_datetime.hour, 0]+=xtime 
                    trav_time_hr[local_datetime.hour, 1]+=1 

                    if xtime > max_time:
                        max_time = xtime
                        worst_hr = local_datetime.hour
                        worst_day= local_datetime.isoweekday()

                    running_total+= xtime
                    nobs+=1
            
            average_time = running_total / nobs
            trav_time_hr[:, 1][trav_time_hr[:, 1]<=0] = 1 
            Visum.Log(PRIO, trav_time_hr[:, 0]/trav_time_hr[:, 1])
            # Visum.Log(PRIO, (_result['timeStamp'], local_datetime.strftime("%H:%M:%S"), _result['overallResult']))
            # ('2025-04-06T15:32:00Z', '08:32:00', {'value': 6.63083, 'defaultValue': 5.115329, 'unusualValue': 10.769688, 'averageValue': 7.2641454, 'progressive': 6.6872616})
        except:
            Visum.Log(PRIO, "failed to set data for kpId: {}".format(kpiId))
            Visum.Log(PRIO, "result: {}".format(path_result))

    return average_time, max_time, worst_hr, worst_day

def generate_useratts():

    if Visum.Net.Paths.AttrExists("kpiId"):
        print ("attr exists...")
    else:
        Visum.Net.Paths.AddUserDefinedAttribute("kpiId", "kpiId", "kpiId", 5)

    if Visum.Net.Paths.AttrExists("travel_time"):
        print ("attr exists...")
    else:
        Visum.Net.Paths.AddUserDefinedAttribute("travel_time", "travel_time", "travel_time", 2)

    # average_time, max_time, worst_hr, worst_day

    if Visum.Net.Paths.AttrExists("max_time"):
        print ("attr exists...")
    else:
        Visum.Net.Paths.AddUserDefinedAttribute("max_time", "max_time", "max_time", 2)

    if Visum.Net.Paths.AttrExists("worst_hr"):
        print ("attr exists...")
    else:
        Visum.Net.Paths.AddUserDefinedAttribute("worst_hr", "worst_hr", "worst_hr", 2)

    if Visum.Net.Paths.AttrExists("worst_day"):
        print ("attr exists...")
    else:
        Visum.Net.Paths.AddUserDefinedAttribute("worst_day", "worst_day", "worst_day", 5)         


def pull_corridors():
    
    generate_useratts()

    resp = requests.get(url='https://api.ptvgroup.tech/kpieng/v1/instance/all?apiKey={}'.format(key))
    corridor_results = json.loads(resp.text)

    if resp.status_code == 200:

        mm = Visum.Net.CreateMapMatcher()
        mm.MapMatchingParameters.SetAttValue('TSysSet', match_tsys)

        if Visum.Net.PathSets.Count > 0:
            pathsetno = int(Visum.Net.PathSets.GetMultiAttValues("NO")[-1][1] + 1)
        else:
            pathsetno = 1

        pathset = Visum.Net.AddPathSet(pathsetno)
        # pathsetno = pathset.AttValue("NO")
        pathno = 1

        for corridor in corridor_results:
            kpiId = corridor['kpiId']
            corridor_name = corridor['location']['name']
            corridor_poly = corridor['location']['shape']

            Visum.Log(PRIO, "matching corridor: {}, kpiId: {}".format(corridor_name, kpiId))

            polyline = ogr.CreateGeometryFromWkt(corridor_poly)
            points   = polyline.GetPoints()

            mm.MatchPointSequence(points)
            fail_point_index = mm.GetPointIndexOfError()

            if fail_point_index == -1:

                Visum.Log(PRIO, "success!")
                
                NodeElements = Visum.CreateNetElements()

                linksequence = mm.GetResultLinkSequence()
                for link in linksequence:
                    # print (link.AttValue("FROMNODENO"), link.AttValue("NO"))
                    NodeElements.Add(Visum.Net.Nodes.ItemByKey(link.AttValue("FROMNODENO")))

                NodeElements.Add(Visum.Net.Nodes.ItemByKey(link.AttValue("TONODENO")))

                # Visum.Net.AddPath(no=2, PathSet=1, fromZone=node1, toZone=node2, PathItems=node_chain
                node1 = linksequence[0].AttValue("FROMNODENO")
                node2 = linksequence[-1].AttValue("TONODENO")

                path = Visum.Net.AddPath(pathno, pathsetno, node1, node2, NodeElements)
                path.SetAttValue("kpiId", kpiId)
                path.SetAttValue("Name", corridor_name)
            
                average_time, max_time, worst_hr, worst_day = get_path_results(kpiId)
                worst_day_name = day_name[worst_day]

                path.SetAttValue("travel_time", average_time)
                path.SetAttValue("max_time", max_time)
                path.SetAttValue("worst_hr", worst_hr)
                path.SetAttValue("worst_day", worst_day_name)
                # NodeElements.Clear()
                Visum.Log(PRIO, "PrT path {} was added.".format(pathno))
                
                pathno+=1

            else:
                Visum.Log(PRIO, "failed!")
            
    else:
        errormsg = "request failed! - error: {}".format(resp.status_code)
        print (errormsg)
        Visum.Log(PRIO, errormsg)



pull_corridors()




# kpiId_set = ['15a5cc7a-0fc9-499f-8b6c-0e414ec2b6e7', 
#              '7ade962f-2e96-4da1-be23-dd306971e09a', 
#              '69bac442-558a-47ad-a0ba-1ab89fe1cb62',
#              '88222b48-8c51-4d14-956b-08e9695b0a55',
#              'd5d73b43-c146-45fd-a4ab-c82aec10dcbe',
#              'fe2cd0e4-2079-4e56-9801-38bdc85d50b6']

# master_list = [['kpiId', 'timestamp', 'day', 'time', 'value', 'defaultValue', 'unusualValue', 'averageValue', 'progressive']]
# ndays = 1
# period= 86399
# fn = r"D:\PTV_OneDrive\OneDrive - PTV Group\Meso_ODOT\r1_meso_hyb\travel_time_data_May_22_2025.csv"

# for i in range(ndays):
#     print ("{} collecting data".format(time.asctime()))
#     for kpiId in kpiId_set:
#         master_list.extend(collect_path_results(kpiId))

#     if i < ndays-1:
#         print (i)
#         time.sleep(period)

# # for row in master_list:
# #     print (row)

# with open(fn, 'w', newline='') as csvfile:
#     writer = csv.writer(csvfile, delimiter =',')
#     writer.writerows(master_list) 