#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import seaborn as sn
import matplotlib.pyplot as plt
import numpy as np

pd.options.display.min_rows = 999
pd.options.display.max_columns = 999


# In[2]:


years = [i for i in range(2011, 2021)]
slams = ['ausopen', 'frenchopen', 'usopen', 'wimbledon']
data = pd.DataFrame()

for year in years:
    for slam in slams:
        if year >= 2018 and slam in ['ausopen', 'frenchopen']: #these slams did not have the same data collected
            continue
        try:
            new_data = pd.read_csv('./tennis_slam_pointbypoint-master/' + str(year) + '-' + slam + '-points.csv')
            if year == 2011 and slam == 'ausopen':
                data = new_data
            else:
                data = pd.concat([new_data, data])
        except FileNotFoundError:
            print(year, slam)
            continue


# In[3]:


#function to define a breakpoint for either player
def breakPoint(x):
    if x['PointServer'] == 2:
        if x['P1Score'] == 'GAME':
            return True
        if (x['P1Score'] == '40' and x['P2Score'] != 'AD') and (x['PointWinner'] == 2 and x['P2Score'] != 'GAME'):
            return True
        
    if x['PointServer'] == 1:
        if x['P2Score'] == 'GAME':
            return True
        if (x['P2Score'] == '40' and x['P1Score'] != 'AD') and (x['PointWinner'] == 1 and x['P1Score'] != 'GAME'):
            return True
        
    if x['P1BreakPoint'] == 1 or x['P2BreakPoint'] == 1:
        return True
            
    return False
            

    
#function to identify surface of the match
def surface(x):
    if 'ausopen' in x['match_id']:
        return 'Hard'
    if 'wimbledon' in x['match_id']:
        return 'Grass'
    if 'frenchopen' in x['match_id']:
        return "Clay"
    if 'usopen' in x['match_id']:
        return 'Hard'
    print(x['match_id'])
    
    


# In[4]:


import seaborn as sn
data['DoubleFault'] = (data.P1DoubleFault == 1) | (data.P2DoubleFault == 1)
data['Speed_MPH'] = data.Speed_KMH * 0.621371
data = data[(data.Speed_MPH != 0) & (data.DoubleFault != True)] #drop data that did not have a serve speed

#feature collection
data.loc[:, 'Ace']              = (data.P1Ace == 1) | (data.P2Ace == 1)
data.loc[:,'NetPoint']          = (data.P1NetPoint == 1) | (data.P2NetPoint == 1) 
data.loc[:,'NetPointWon']       = (data.P1NetPointWon == 1) | (data.P2NetPointWon == 1) 
data.loc[:,'UnforcedError']     = (data.P1UnfErr == 1) | (data.P2UnfErr == 1) 
data.loc[:,'Winner']            = (data.P1Winner == 1) | (data.P2Winner == 1)
data.loc[:,'FirstSrvIn']        = (data.ServeNumber == 1) | ((data.P1FirstSrvIn == 1) | (data.P2FirstSrvIn == 1))
data.loc[:,'BreakPoint']        = data.loc[:, ['PointServer', 'P1Score', 'P2Score', 'P1BreakPoint', 'P2BreakPoint', 'PointWinner']].apply(lambda x: breakPoint(x), axis = 1)
data.loc[:,'BreakPointWon']     = (data.BreakPoint) & (data.PointServer != data.PointWinner)
data.loc[:,'DF']                = (data.P1DoubleFault == 1) | (data.P2DoubleFault == 1)
data.loc[:,'ServeSpeed']        = data.Speed_KMH * 0.621371
data.loc[:,'ServerWon']         = (data.PointWinner == data.PointServer)
data.loc[:,'ServerLost']        = (data.PointWinner != data.PointServer)
data.loc[:,'Surface']           = data.loc[:, ['match_id', 'P1Score']].apply(lambda x: surface(x), axis = 1)
data.loc[:,'GamesPlayed']       = data.P1GamesWon + data.P2GamesWon
data.loc[:,'ServerNetPoint']    = ((data.P1NetPoint == 1) & (data.PointServer == 1)) | ((data.P2NetPoint == 1) & (data.PointServer == 2))
data.loc[:,"ServerNetPointWon"] = (data.ServerNetPoint & (data.PointServer == data.PointWinner))




# In[5]:


#rally length on every point
plt.grid()
a_plot = sn.histplot(x = data.Rally, stat = 'probability', binwidth = 3)
a_plot.set(xlim = (0, 35))
a_plot.set(ylim = (0, .45))


plt.title("Total Rally Length")


# In[6]:


#rally length on break points
a_plot = sn.histplot(x = data[data.BreakPoint == True].Rally, stat = 'probability', binwidth = 3)
a_plot.set(xlim = (0, 35))
a_plot.set(ylim = (0, .45))

plt.grid()

plt.title("Total Rally Length on Break Points")


# In[7]:


#rally length on break point saves
a_plot = sn.histplot(x = data[(data.BreakPoint == True) & (data.BreakPointWon != True)].Rally, stat = 'probability', binwidth = 3)
a_plot.set(xlim = (0, 35))
a_plot.set(ylim = (0, .45))

plt.grid()

plt.title("Total Rally Length on Break Point Saves")


# In[8]:


a_plot = sn.lineplot(x = [i for i in range(0,12)], y = data.groupby('GamesPlayed').mean()['BreakPoint'][0:11])
a_plot.set(ylim = (0, .19))
plt.title("Break Points Faced per Game")
plt.grid()
plt.xlabel("Games into Set")


# In[9]:


#bucketing by serve speed and then finding out win percentage and first serve in percentage

#we want the data to be for serves and how serve speed affects break points
#want to make aces known and first serve percentage known

buckets = []
save_percentage = []
rally_length = []
winner_percentage_save = []
winner_percentage_loss = []
unforced_error_percentage_loss = []
unforced_error_percentage_save = []
net_point = []
net_point_won = []
return_net_point = []
return_net_point_won = []


for i in range(80, 145, 5): #going up by fives if between then we bucket them for break point saves and first serves

    bucket_data = data[(data.ServeSpeed >= i) & (data.ServeSpeed <= i + 5)]
    trimmed_data = bucket_data[bucket_data.BreakPoint]
    
    x = bucket_data.groupby('BreakPoint').mean()
    y = trimmed_data.groupby('BreakPointWon').mean()
    
    
    save_percentage.append(1 - x.loc[True, 'BreakPointWon'])#doing the one because has two entries True and False
    rally_length.append(y.loc[True, 'Rally'])
    
    buckets.append(i)
    
    winner_percentage_loss.append(y.loc[False, 'Winner'])
    winner_percentage_save.append(y.loc[True, 'Winner'])
    
    unforced_error_percentage_loss.append(y.loc[True, 'UnforcedError'])
    unforced_error_percentage_save.append(y.loc[False, 'UnforcedError'])
    
    net_point.append(x.loc[True, 'ServerNetPoint'])
    net_point_won.append(x.loc[True, 'ServerNetPointWon'] / x.loc[True, 'ServerNetPoint'])
    
    return_net_point.append(x.loc[True, 'NetPoint'] - x.loc[True, 'ServerNetPoint'])
    return_net_point_won.append((x.loc[True, 'NetPointWon'] - x.loc[True, 'ServerNetPointWon']) / (x.loc[True, 'NetPoint'] - x.loc[True, 'ServerNetPoint']))
    
    
    
    
    
    


# In[10]:


#Save percentage by serve speed

import matplotlib.ticker as mtick
ax = sn.lineplot(x = buckets, y = [i * 100 for i in save_percentage])
ax.yaxis.set_major_formatter(mtick.PercentFormatter())

plt.grid()
plt.title("Save Percentage by Serve Speed")

plt.ylabel("Save Percentage")
plt.xlabel("Serve Speed")


# In[11]:


#winner percentage by player

ax1 = sn.lineplot(x = buckets, y = [i *100 for i in winner_percentage_loss], label = 'Server')
ax2 = sn.lineplot(x = buckets, y = [i * 100 for i in winner_percentage_save], label = 'Returner')
ax1.yaxis.set_major_formatter(mtick.PercentFormatter())
ax2.yaxis.set_major_formatter(mtick.PercentFormatter())

plt.grid()
plt.title("Winner Percentage Server vs Returner by Serve Speed")

plt.ylabel("Winner Percentage")
plt.xlabel("Serve Speed MPH")


# In[12]:


#unforced error percentage by player

ax1 = sn.lineplot(x = buckets, y = [i * 100 for i in unforced_error_percentage_save], label = 'Server')
ax2 = sn.lineplot(x = buckets, y = [i * 100 for i in unforced_error_percentage_loss], label = 'Returner')
ax1.yaxis.set_major_formatter(mtick.PercentFormatter())
ax2.yaxis.set_major_formatter(mtick.PercentFormatter())

plt.grid()
plt.title("Unforced Error Percentage Server vs Returner by Serve Speed")

plt.ylabel("Unforced Error Percentage")
plt.xlabel("Serve Speed MPH")


# In[13]:


data[data.BreakPoint].groupby('FirstSrvIn').mean()


# In[17]:


#Server percentage chance to get to the net
ax = sn.lineplot(x = buckets, y = [i * 100 for i in net_point])

ax.yaxis.set_major_formatter(mtick.PercentFormatter())

plt.grid()
plt.title("Server Percentage Chance to Get to the Net")

plt.ylabel("Server Net Point Percentage")
plt.xlabel("Serve Speed MPH")


# In[18]:


#server win percentage at the net
ax = sn.lineplot(x = buckets, y = [i * 100 for i in net_point_won])
ax.yaxis.set_major_formatter(mtick.PercentFormatter())


plt.grid()
plt.title("Server Win Percentage at the Net by Serve Speed")

plt.ylabel("Server Net Point Win Percentage")
plt.xlabel("Serve Speed MPH")


# In[16]:


#Returner percentage chance to get to the net
ax = sn.lineplot(x = buckets, y = [i * 100 for i in return_net_point])
ax.yaxis.set_major_formatter(mtick.PercentFormatter())


plt.grid()
plt.title("Returner Percent Chance to get to Net by Serve Speed")

plt.ylabel("Returner Net Point Win Percentage")
plt.xlabel("Serve Speed MPH")


# In[18]:


#returner win percentage at the net

ax = sn.lineplot(x = buckets, y = [i * 100 for i in return_net_point_won])
ax.yaxis.set_major_formatter(mtick.PercentFormatter())

plt.grid()
plt.title("Returner Win Percentage at the Net by Serve Speed")

plt.ylabel("Returner Net Point Win Percentage")
plt.xlabel("Serve Speed MPH")


# In[161]:


#1st serve rally length

a_plot = sn.histplot(x = data[(data.P1FirstSrvIn == 1) | (data.P2FirstSrvIn == 1)].Rally, stat = 'probability', binwidth = 3)

a_plot.set(xlim = (0, 35))
plt.title("Rally Length on First Serves")


# In[162]:


#second serve rally length

a_plot = sn.histplot(x = data[(data.P1SecondSrvIn == 1) | (data.P2SecondSrvIn == 1)].Rally, stat = 'probability', binwidth = 3)
a_plot.set(xlim = (0, 35))
plt.title("Rally Length on Second Serves")


# In[163]:


# first serve rally length without aces
a_plot = sn.histplot(x = data[((data.P1Ace == 1) | (data.P2Ace != 1)) & ((data.P1FirstSrvIn == 1) | (data.P2FirstSrvIn == 1))].Rally, stat = 'probability', binwidth = 3)

a_plot.set(xlim = (0, 35))
plt.title("Rally Length First Serve without Aces")


# In[164]:


# rally length when the server won the point

a_plot = sn.histplot(x = data[data.PointWinner == data.PointServer].Rally, stat = 'probability', binwidth = 3)

a_plot.set(xlim = (0, 35))
plt.title("Rally Length When the Server Won the point")


# In[165]:


# rally length when the server loses the point

a_plot = sn.histplot(x = data[data.PointWinner != data.PointServer].Rally, stat = 'probability', binwidth = 3)

a_plot.set(xlim = (0, 35))
a_plot.set(ylim = (0, .45))
plt.title("Rally Length When the Server Loses the Point")


# In[166]:


data['ServerWon'] = (data.PointWinner == data.PointServer)
data['ServerLost'] = (data.PointWinner != data.PointServer)


# In[167]:


#bucketing by fours and then determining serve percentage winning

bucket = []
won_points = []
total_points = []

series = data.groupby('Rally').sum()['ServerWon']
series2 = data.groupby('Rally').sum()['ServerLost'] + series


for i in range(1, 32, 4):
    bucket.append(i)
    won_points.append(series[i] + series[i+1] + series[i+2] + series[i+3])
    total_points.append(series2[i] + series2[i+1] + series2[i+2] + series2[i+3])
    
final = []
for i in range(len(won_points)):
    final.append(won_points[i] / total_points[i])


# In[168]:


a_plot = sn.lineplot(x = bucket, y = final)

a_plot.set(ylim = (.2, .8))

plt.title("Rally Length by Server Win Percentage")


# In[169]:


#bucketing by fours and then determining serve percentage winning on first serve

bucket = []
won_points = []
total_points = []

series = data[(data.P1FirstSrvIn == 1) | (data.P2FirstSrvIn == 1)].groupby('Rally').sum()['ServerWon']
series2 = data[(data.P1FirstSrvIn == 1) | (data.P2FirstSrvIn == 1)].groupby('Rally').sum()['ServerLost'] + series


for i in range(1, 32, 4):
    bucket.append(i)
    won_points.append(series[i] + series[i+1] + series[i+2] + series[i+3])
    total_points.append(series2[i] + series2[i+1] + series2[i+2] + series2[i+3])
    
final = []
for i in range(len(won_points)):
    final.append(won_points[i] / total_points[i])


# In[170]:


a_plot = sn.lineplot(x = bucket, y = final)

a_plot.set(ylim = (.2, .8))
plt.title("Rally Length Win Percentage on First Serves")


# In[171]:


#bucketing by fours and then determining serve percentage winning on second serve

bucket = []
won_points = []
total_points = []

series = data[(data.P1SecondSrvIn == 1) | (data.P2SecondSrvIn == 1)].groupby('Rally').sum()['ServerWon']
series2 = data[(data.P1SecondSrvIn == 1) | (data.P2SecondSrvIn == 1)].groupby('Rally').sum()['ServerLost'] + series


for i in range(1, 32, 4):
    bucket.append(i)
    won_points.append(series[i] + series[i+1] + series[i+2] + series[i+3])
    total_points.append(series2[i] + series2[i+1] + series2[i+2] + series2[i+3])
    
final = []
for i in range(len(won_points)):
    final.append(won_points[i] / total_points[i])
    
a_plot = sn.lineplot(x = bucket, y = final)

a_plot.set(ylim = (.2, .8))
plt.title("Rally Length Win Percentage on Second Serves")


# In[172]:


#bucketing by fours and then determining win percentage on break points

bucket = []
won_points = []
total_points = []

series = data[(data.P1BreakPoint == 1) | (data.P2BreakPoint == 1)].groupby('Rally').sum()['ServerWon']
series2 = data[(data.P1BreakPoint == 1) | (data.P2BreakPoint == 1)].groupby('Rally').sum()['ServerLost'] + series


for i in range(1, 32, 4):
    bucket.append(i)
    if i + 3 >= 32:
        won_points.append(series[i] + series[i+1] + series[i+2])
        total_points.append(series2[i] + series2[i+1] + series2[i+2])
    else:
        print(i)
        won_points.append(series[i] + series[i+1] + series[i+2] + series[i+3])
        total_points.append(series2[i] + series2[i+1] + series2[i+2] + series2[i+3])
    
final = []
for i in range(len(won_points)):
    final.append(won_points[i] / total_points[i])
    
a_plot = sn.lineplot(x = bucket, y = final)

a_plot.set(ylim = (.2, .8))
plt.title("Rally Length Break Point Saved")


# In[173]:


data2 = data[(data.P1FirstSrvIn == 1) | (data.P2FirstSrvIn == 1)]

#bucketing by fours and then determining serve percentage winning on first serve

bucket = []
won_points = []
total_points = []

series = data2[(data2.P1BreakPoint == 1) | (data2.P2BreakPoint == 1)].groupby('Rally').sum()['ServerWon']
series2 = data2[(data2.P1BreakPoint == 1) | (data2.P2BreakPoint == 1)].groupby('Rally').sum()['ServerLost'] + series


for i in range(1, 32, 4):
    bucket.append(i)
    if i + 3 >= 32:
        won_points.append(series[i] + series[i+1] )
        total_points.append(series2[i] + series2[i+1])
    else:
        print(i)
        won_points.append(series[i] + series[i+1] + series[i+2] + series[i+3])
        total_points.append(series2[i] + series2[i+1] + series2[i+2] + series2[i+3])
    
final = []
for i in range(len(won_points)):
    final.append(won_points[i] / total_points[i])
    
a_plot = sn.lineplot(x = bucket, y = final)

a_plot.set(ylim = (.2, .8))
plt.title("Rally Length Break Point Saved on First Serve")


# In[ ]:




