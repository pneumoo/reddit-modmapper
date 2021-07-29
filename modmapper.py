# -*- coding: utf-8 -*-
"""
Created on Sun Dec 25 10:43:45 2016

@author: Brian

This is a set of functions and tools which can map out a "mod network" 
on reddit. A mod network is the relationships of subreddits and moderators 
across reddit. A moderator very interested in a particular cause may have
created several subreddits, and those subreddits may have other moderators 
who have tangential or related interests, each of whom has their own 
subreddits. 

These sets of tools can map that out, when used with Gephi. 

"""

import praw
import time
from bs4 import BeautifulSoup
import requests
import datetime
import networkx as nx


firstsubtarget = "SUB_TARGET_1" 
othersubs= []
skippedsubreddits = []

USERAGENT = 'USERAGENT' 
CLIENT_ID = 'CLIENT_ID'
CLIENT_SECRET = 'CLIENT_SECRET'
USERNAME = 'USERNAME'
PASSWORD = 'PASSWORD'
DAYSINACTIVE = 180

userignore = ["AutoModerator", "publicmodlogs", "rarchives",
              "roger_bot", "moderator-bot"]

def getRedditInstance(UA=USERAGENT, CID=CLIENT_ID, CS=CLIENT_SECRET, UN=USERNAME, PW=PASSWORD):
    r = praw.Reddit(client_id=CID,
                     client_secret=CS,
                     password=PW,
                     user_agent=UA,
                     username=UN)
    return(r)                  


#-----------------------------------------------------------------------------
# DESCRIPTION: This function finds the subreddits that a user moderates. 
# PRAW/reddit don't have a built-in way to do this, so manual scrape is done.
# User-Agent needs to be the same as USERAGENT for this to work
# Be wary of the reddit rate limit. It can be set to 0 if function takes 
# longer than 2 seconds to complete anyway...
# In order to prune the graph somewhat, we check to see if we've already 
# skipped a particular subreddit, and we also call isSubActive() to run some 
# basic checks on if the subreddit has any recent activity. 
#
# INPUTS: a username
#
# RETURNS: a list of subreddits
#-----------------------------------------------------------------------------
def getUserSubMods(user):   #Take in redditor object, not actual username
    time.sleep(0)    # be nice to reddit rate limit
    print("Getting " + user.name + " info")    
    usermodlist = []
    URL = "https://www.reddit.com/user/" + user.name
    data = requests.get(URL, headers={'User-Agent': USERAGENT})
    soup = BeautifulSoup(data.content, 'lxml')
    sidemodlist = soup.find(id="side-mod-list")
    sublinks = sidemodlist.find_all('a')
    for i in sublinks:
        # Checks if this sub has been skipped before. This 
        # speeds up by not checking active subs over and over
        subname = i.get_text()[2:]
        if subname in skippedsubreddits:    # GLOBAL list
            print("QUICK SKIP /r/" + subname)
            continue
        else:
            # Check if the subreddit is actually active...
            # if it's not, add it to the 
            if isSubActive(subname) == True:
                usermodlist.append(subname)
            else:
                skippedsubreddits.append(subname)
    return(usermodlist)


#-----------------------------------------------------------------------------
# DESCRIPTION: Takes in the modnet network and makes a list of unique 
# subreddit names
#
# INPUTS: modnet_dict: (DICT) moderator network 
#
# RETURNS: a list of subreddits
#-----------------------------------------------------------------------------
def getUniqueSubs(modnet_dict):
    relatedsubs = []
    for i in modnet_dict.values():
        for j in i:
            if j not in relatedsubs and j != firstsubtarget:
                relatedsubs.append(j) 
    return(relatedsubs)



#-----------------------------------------------------------------------------
# DESCRIPTION: Expands the graph search space of the modnet network by one 
# degree. 
#
# INPUTS: modnet_dict: (DICT) moderator network of degree n
#
# RETURNS: modnet_dict: (DICT) moderator network of degree n+1
#-----------------------------------------------------------------------------
def expandSepDeg(modnet):
    relatedsubs = getUniqueSubs(modnet)
    for index, sub in enumerate(relatedsubs):
        print("\nFor /r/" + sub + " " + str(index) + " of " + str(len(relatedsubs)))
        newmodlist = getSubMods(sub)
        for user in newmodlist:
            if user.name in userignore:
                print("Ignoring user " + user.name)
                continue
            elif user.name in modnet.keys():
                print("Already have data for " + user.name)
                continue
            else:
                try:
                    usermodlist = getUserSubMods(user)
                    modnet[user.name] = usermodlist
                except:
                    print("Could not get " + user.name + " info. Acct suspended or deleted?")
    return(modnet)



# Checks to see if the subreddit is "active"
# Logic here says a subreddit is Active if a sumbission in the last <DAYSINACTIVE> days
# Handles quarantined subreddits, too
#-----------------------------------------------------------------------------
# DESCRIPTION: Checks to see if the subreddit is "active".
# Logic here says a subreddit is Active if a sumbission in the 
# last <DAYSINACTIVE> days. Handles quarantined subreddits, too
#
# INPUTS: subtarget: (STR) a subreddit name
#
# RETURNS: True/False if sub is active or not.
#-----------------------------------------------------------------------------
def isSubActive(subtarget):
    reddit = getRedditInstance()
    sub = reddit.subreddit(subtarget)
    # Need to do these try/except blocks for quarantined subreddits
    try:
        # f Sub has new posts in <DAYSINACTIVE> days        
        for i in sub.new(limit=1):
            lastpostdate =  datetime.datetime.fromtimestamp(i.created)
            delta = datetime.datetime.now() - lastpostdate      
            if delta.days < DAYSINACTIVE:
                return(True)            
        else:
            print("/r/" + subtarget + " not active in last " + str(DAYSINACTIVE) + " days. Skipping...")
            return(False)
    except:
        try:
            # (QUARANTINED) If Sub has new posts in <DAYSINACTIVE> days 
            try:         
                sub.quaran.opt_in()
            except: 
                print("/r/" + subtarget + " inaccessable, quarantined... Skipping...")              
                return(False)
            for i in sub.new(limit=1):
                lastpostdate =  datetime.datetime.fromtimestamp(i.created)
                delta = datetime.datetime.now() - lastpostdate      
                if delta.days < DAYSINACTIVE:
                    return(True)            
            else:
                print("/r/" + subtarget + " not active in last " + str(DAYSINACTIVE) + " days. Skipping...")
                return(False)
        except:
            return(True)



def revDict(modnet_dict):
    from collections import defaultdict
    revDict = defaultdict(list)  
    for k, v in modnet_dict.items():
        for item in v:
            revDict[item].append(k)
    return(revDict)



# This does output parallel edges if there are any
def makeEdgeList(modnet_dict):
    from itertools import combinations
    edges = []
    for k, v in modnet_dict.items():
        if len(v) > 1:
            for values in combinations(v, 2):
                edges.append(values)
    return(edges)


#-----------------------------------------------------------------------------
# DESCRIPTION:  Converts the modnet_dict into a .gexf, and also adds some 
# additional information like number of subreddit subscribers. 
# 
# INPUTS:
#	* modnet_dict: (DICT) dictionary of moderator network
#	* filename: (STR) filename to save the .gexf file
#
# RETURNS: Returns nothing, but writes .gexf to file. 
#-----------------------------------------------------------------------------
def getFinalSubData(modnet_dict):
    reddit = getRedditInstance()  
    relatedsubs = getUniqueSubs(modnet_dict)
    relatedsubs.append(firstsubtarget)
    for sub in relatedsubs:
        subnum = reddit.subreddit(sub).subscribers
        for key in modnet_dict.keys():
            if sub in modnet_dict[key]:
                subindex = modnet_dict[key].index(sub)
                modnet_dict[key][subindex] = {str(sub): str(subnum)}
    return(modnet_dict)


#-----------------------------------------------------------------------------
# DESCRIPTION:  Converts the modnet_dict into a .gexf, and also adds some 
# additional information like number of subreddit subscribers. 
# 
# INPUTS:
#	* modnet_dict: (DICT) dictionary of moderator network
#	* filename: (STR) filename to save the .gexf file
#
# RETURNS: Returns nothing, but writes .gexf to file. 
#-----------------------------------------------------------------------------
def makeGEXF(modnet_dict, filename="test.gexf"):
    reddit = getRedditInstance()
    edges = []
    M = nx.MultiGraph()
    edges = makeEdgeList(modnet_dict)
    for i in edges:
        M.add_edge(i[0],i[1],weight=1)
    
    G = nx.Graph()
    for u,v,data in M.edges_iter(data=True):
        w = data['weight']
        if G.has_edge(u,v):
            G[u][v]['weight'] += w
        else:
            G.add_edge(u, v, weight=w)
    
    for node in G.nodes():
        print("Getting subscribers for /r/" +  node)
        subnum = reddit.subreddit(node).subscribers
        G.node[node] = {'subscribers': subnum}
    
    nx.write_gexf(G, filename)        
    print("GEXF file created successfully")






#-----------------------------------------------------------------------------
# DESCRIPTION:  Gets a given subreddit's moderators' reddit objects. Note that
# the reddit API allows finding moderators FROM a subreddit, but does not 
# have a built-in way to find subreddits-moderated FROM a user. Hence the 
# difference between getSubMods() and getUserSubMods(). 
# 
# INPUTS:
#	* subtarget: (STR) the primary subreddit of interest
#
# RETURNS: List the Redditor objects for each moderator of the sub
#-----------------------------------------------------------------------------
def getSubMods(subtarget):
    reddit = getRedditInstance()
    modlist = []    # List of Redditor objects     
    try:
        for mod in reddit.subreddit(subtarget).moderator:
            modlist.append(mod)
    except:
        print("/r/" + subtarget + " is quarantined... accessing...")
        try:        
            subreddit = reddit.subreddit(subtarget)
            subreddit.quaran.opt_in()
            for mod in subreddit.moderator:
                modlist.append(mod)
        except: 
            print("Could not retrieve /r/" + subtarget)
    return(modlist) # Returns Redditor objects, not redditor user names


#-----------------------------------------------------------------------------
# DESCRIPTION: Ingests a subreddit name, finds moderators, and creates a 
# dictionary of the 1-degree network of relationships of those moderators. 
# 
# INPUTS:
#	* firstsubtarget: (STR) the primary subreddit of interest
#
# RETURNS: Dict with 1st degree network of mods/subs
#-----------------------------------------------------------------------------
def getOneSub(firstsubtarget):
    modnet = {}
    modlist = getSubMods(firstsubtarget)	#Find moderator redditor objects
    
    for user in modlist:
        if user.name not in userignore:
            try:
				# Find other subreddits this user moderates
                usermodlist = getUserSubMods(user)
                modnet[user.name] = usermodlist
            except:
                print("Could not get " + user.name + " info. Acct suspended or deleted?")
    return(modnet)


#-----------------------------------------------------------------------------
# "Main" Function...

# DESCRIPTION: Ingests subreddits of interest, and creates a network graph
# object for each one. Each of these are combined to form a complete network
# graph, which is then converted to GEXF format and saved so it can then 
# be plotted in Gephi.
# 
# INPUTS:
#	* firstsubtarget: (STR) the primary subreddit of interest
#	* othersubs: (STR LIST) a list of other subreddits to examine, which might
#		have a relationship with firstsubtarget
#	* filename: (STR) file name of the .gexf output
# RETURNS: .gexf file 
#-----------------------------------------------------------------------------
def getAllSubs(firstsubtarget=firstsubtarget, othersubs=othersubs, filename = "test.gexf"):
    reddit = getRedditInstance()    
    allsubs = othersubs.copy()
    allsubs.append(firstsubtarget)

    print(allsubs)
    # Get 1stDeg info from allsubs and create multigraph list    
    MGraphs = []
    for i in allsubs:
        modnet = getOneSub(i)   # Returns mod network of i-th subreddit 
        edges = []
        newMGraph = nx.MultiGraph()
        edges = makeEdgeList(modnet)
        for i in edges:
            newMGraph.add_edge(i[0],i[1],weight=1)
        MGraphs.append(newMGraph)   
    
    # Combine the M Graphs into 1 graph    
    comboMGraph = nx.compose_all(MGraphs)
    
    # With combo graph created, convert back to simple graph
    G = nx.Graph()
    for u,v,data in comboMGraph.edges_iter(data=True):
        w = data['weight']
        if G.has_edge(u,v):
            G[u][v]['weight'] += w
        else:
            G.add_edge(u, v, weight=w)
        
    for node in G.nodes():
        print("Getting subscribers for /r/" +  node)
        subnum = reddit.subreddit(node).subscribers
        G.node[node] = {'subscribers': subnum}
    
    nx.write_gexf(G, filename)        
    print("GEXF file created successfully")



#client_auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
#post_data = {"grant_type": "password", "username": USERNAME, "password": PASSWORD}
#headers = {"User-Agent": USERAGENT}
#response = requests.post("https://www.reddit.com/api/v1/access_token", auth=client_auth, data=post_data, headers=headers)
#TOKEN = response.json()['access_token']
#auth_headers = {"Authorization": "bearer " + TOKEN, "User-Agent": USERAGENT}
