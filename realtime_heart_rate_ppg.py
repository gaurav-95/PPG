# -*- coding: utf-8 -*-
"""
Created on Thu Apr 29 15:06:10 2021

@author: Gaurav
"""

from datetime import datetime
from dateutil.tz import gettz
from datetime import timedelta
import requests
import pandas as pd
from apscheduler.scheduler import Scheduler
from scipy.signal import butter, iirnotch, lfilter, find_peaks
#from itertools import repeat

sched = Scheduler()
sched.start()
            
def flatten(List_2D):
    List_flat=[]
    for i in range(len(List_2D)): #Traversing through the main list
        for j in range (len(List_2D[i])): #Traversing through each sublist
            List_flat.append(List_2D[i][j])
    return List_flat

def get_foxes(data):
    peaks, _ = find_peaks(data, prominence = 0.3,  distance=5, height=0)
    return peaks

def heart_rate(peaks):
    tot_peaks=len(peaks)
    heart_rate=tot_peaks
    return heart_rate

def normalize(readings):
    readings = (readings-min(readings))/(max(readings)-min(readings))
    return readings

## A high pass filter allows frequencies higher than a cut-off value
def butter_highpass(cutoff, fs, order):
    nyq = 0.5*fs
    normal_cutoff = cutoff/nyq
    b, a = butter(order, normal_cutoff, btype='high', analog=False, output='ba')
    return b, a
## A low pass filter allows frequencies lower than a cut-off value
def butter_lowpass(cutoff, fs, order):
    nyq = 0.5*fs
    normal_cutoff = cutoff/nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False, output='ba')
    return b, a
def notch_filter(cutoff, q):
    nyq = 0.5*fs
    freq = cutoff/nyq
    b, a = iirnotch(freq, q)
    return b, a

def highpass(data, fs, order):
    b,a = butter_highpass(cutoff_high, fs, order=order)
    x = lfilter(b,a,data)
    return x

def lowpass(data, fs, order):
    b,a = butter_lowpass(cutoff_low, fs, order=order)
    y = lfilter(b,a,data)
    return y

def notch(data, powerline, q):
    b,a = notch_filter(powerline,q)
    z = lfilter(b,a,data)
    return z

def final_filter(data, fs, order):
    b, a = butter_highpass(cutoff_high, fs, order=order)
    x = lfilter(b, a, data)
    d, c = butter_lowpass(cutoff_low, fs, order = order)
    y = lfilter(d, c, x)
    f, e = notch_filter(powerline, 30)
    z = lfilter(f, e, y)     
    return z

timediff=59
fs = 25
cutoff_high = 2.4
cutoff_low = 0.7
powerline = 1
order = 5

secret_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiJkZWJhbmphbiIsImlhdCI6MTYxNjY0NjA3OH0.Tfyog7lHPADpickUc1itaxdC_fs4_eAxLQDY3G9C5Z4"

user_url = "https://apiserverparentprotect.herokuapp.com/get-active-users"

def main():
    now = datetime.now(tz=gettz('Asia/Kolkata'))
    prev = now - timedelta(seconds=5)
    timestamp = now.strftime("%d/%m/%Y %H:%M:%S")
    
    user_list = {"secret_token": secret_token, "timestamp": timestamp}
    response = requests.post(user_url, json=user_list)
    
    user = response.json()['data']['users']
    #user = ['607c1911676b1700046ae8ea']
    
    prev = now - timedelta(seconds=timediff)
    from_time = prev.strftime("%d/%m/%Y") + "%20" + prev.strftime("%H:%M:%S")
    #print(from_time)

    to_time = now.strftime("%d/%m/%Y")+ "%20" + now.strftime("%H:%M:%S")
    #print(to_time)
    
    for i in user:
        user_data = requests.get("https://apiserverparentprotect.herokuapp.com/get-data?secret_token="+secret_token+"&type=heart_rate_voltage&dateFrom="+from_time+"&dateTo="+to_time+"&userID="+i)
        heart_data = user_data.json()['data']
        tot=len(heart_data)
        #print(tot)
        
        pp=[]
        p=[]
        l=[]
        #times=[]
        
        for j in range(tot):
            heart_data[j]['heart_rate_voltage']['values'].pop(0)
            l.append(heart_data[j]['heart_rate_voltage']['values'][0::3])
            pp.append(heart_data[j]['heart_rate_voltage']['values'][1::3])
            p.append(heart_data[j]['heart_rate_voltage']['values'][2::3])
            #times.extend(repeat(heart_data[j]['timestamp'], 25))
        
        ppg_l=flatten(pp)
        ppg_h=flatten(p)
        
        ppgrec = pd.DataFrame(zip(ppg_l, ppg_h), columns=['ppg', 'ppg_h'])
        ppgrec = ppgrec.astype({"ppg":'float', "ppg_h":'float'})
        #ppgrec['times'] = pd.to_datetime(ppgrec['times'])
        #print(ppgrec)
        
        readings = ppgrec['ppg']
        
        filter_signal = final_filter(readings, fs, order)
        filter_signal = normalize(filter_signal) 
        peaks_butter=get_foxes(filter_signal)
        hr_butter=heart_rate(peaks_butter)
        print(i,"\nHeart Rate (BPM):", hr_butter,"\n",timestamp)
        

sched.add_interval_job(main, seconds = 5)
#sched.modify(max_instances=10)
