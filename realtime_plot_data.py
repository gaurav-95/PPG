# -*- coding: utf-8 -*-
"""
Created on Fri Apr 16 21:18:14 2021

@author: Gaurav
"""


from datetime import datetime
from dateutil.tz import gettz
from datetime import timedelta
import requests
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import pandas as pd
from threading import Timer

secret_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiJkZWJhbmphbiIsImlhdCI6MTYxNjY0NjA3OH0.Tfyog7lHPADpickUc1itaxdC_fs4_eAxLQDY3G9C5Z4"
plt.style.use('fivethirtyeight')

plt.tight_layout()
plt.show()


def animate(xyz):
    data = xyz
    x = data['x']
    y = data['y']
    z = data['z']

    plt.cla()

    plt.plot(x, y, label='Channel 1')
    plt.plot(x, z, label='Channel 2')

    plt.legend(loc='upper left')
    plt.tight_layout()


def user_list():   
    now = datetime.now(tz=gettz('Asia/Kolkata'))
    prev = now - timedelta(seconds=3)
    timestamp = prev.strftime("%d/%m/%Y %H:%M:%S")
        
    #print(now)
    #print(prev)
        
    print(timestamp)

    user_list = {"secret_token": secret_token, "timestamp": timestamp}
    user_url = "https://apiserverparentprotect.herokuapp.com/get-active-users"
    response = requests.post(user_url, user_list)
    #print(response)
        
    user = response.json()["data"]['users']
    #print(user)
        
    return user

    Timer(5, user_list).start()
    
user = user_list()
#print(user)

def do_plot(user): 
    now = datetime.now(tz=gettz('Asia/Kolkata'))
    prev = now - timedelta(seconds=4)
    
    from_time = prev.strftime("%d/%m/%Y") + "%20" + prev.strftime("%H:%M:%S")
    #print(from_time)

    to_time = now.strftime("%d/%m/%Y")+ "%20" + now.strftime("%H:%M:%S")
    #print(to_time)
    
    for i in user:
        user_data = requests.get("https://apiserverparentprotect.herokuapp.com/accelerometer-data?secret_token="+secret_token+"&type=accelerometer&dateFrom="+from_time+"&dateTo="+to_time+"&userID="+i)
        useracc = user_data.json()['data']
        
        x = useracc['acc_data'][0::3]
        y = useracc['acc_data'][1::3]
        z = useracc['acc_data'][2::3]
        #print(x,y,z)
        
        xyz = pd.DataFrame(list(zip(x, y, z)), columns =['x', 'y', 'z'])
            
        ani = FuncAnimation(plt.gcf(), animate(xyz), interval=1000)
        
        return ani
        
        Timer(5, do_plot(user)).start()
        





