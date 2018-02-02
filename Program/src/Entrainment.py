'''
Created on Oct 22, 2015

@author: zar10
'''
import json
import pandas as pd
import numpy as np
import scipy.stats as sci
#partIDs = ['interval1','interval2','interval3','interval4'] 
partIDs = ['interval1','interval2'] 

DemographicInfo = pd.read_csv('Demographics.csv')
Gender_Mapping = {1:'Male',0:'Female'}

def read_featureFile(featureFile):
    return pd.read_csv(featureFile,index_col=0)
def get_group_ID(index):
    if len(index.split('_')) == 1 and len(index.split('-')) < 2:
        return index
    elif index[0]=='T':
        index.split('_')[1]
    else:
        return index[0:4]
def get_Individual_ID(index):
    if index[0]=='T':
        return index.split('_')[-1].split('-')[-1]
    else:
        return index[-1]
        
def get_game_number(index):
    if index[0]=='T':
        return index.split('_')[-1].split('-')[0]
    else:
        return index[-3]
    #TODO

def get_diff(featureDf):
    diffDic = {index:{'partner':{} , 'other':{}} for index in featureDf.index}
        
    for index , row in featureDf.iterrows():
        speakerID = get_Individual_ID(index)
        speaker_group = get_group_ID(index)
        speaker_game = get_game_number(index)
        for index2 , row2 in featureDf.iterrows():
            if index2 == index:
                continue
            else:
                speaker2_group = get_group_ID(index2) 
                if speaker_group == speaker2_group:
                    for feature in row.index:
                        split = feature.split('@')
                        if len(split) == 1:
                            ext=''
                        else:
                            ext='@'+split[-1]
                        if not feature in ['#total'+ext]:
                            if not index2 in diffDic[index]['partner'].keys():
                                diffDic[index]['partner'][index2]={}
                            diffDic[index]['partner'][index2][feature] = abs(float(row[feature])/float(row['#total'+ext]) - float(row2[feature])/float(row2['#total'+ext]))
                else:    
                    for feature in row.index:
                        split = feature.split('@')
                        if len(split) == 1:
                            ext=''
                        else:
                            ext='@'+split[-1]
                        if not feature in ['#total'+ext]:
                            if not index2 in diffDic[index]['other'].keys():
                                diffDic[index]['other'][index2]={}
                            diffDic[index]['other'][index2][feature] = abs(float(row[feature])/float(row['#total'+ext]) - float(row2[feature])/float(row2['#total'+ext]))
            

    print "============The diffDic=========="
    print diffDic
    return diffDic
 
def save_dictionary(path,diffDic):
    with open(path, 'w') as f:
        json.dump(diffDic,f)
def load_dictionary(path):
    with open(path, 'r') as f:
        diffDic = json.load(f)
    return diffDic

#Mingzhi added to calculate the subgroup proximity
#------------------------------Mingzhi----------------------------
def readDemographics():
    
#     mapping = DemographicInfo.iloc[0,(0,17)]
    speakerID_to_sex = {}
    
    # 1 for male, 2 for female
    for i, row in DemographicInfo.iterrows():
        speakerID_to_sex[i] = row[17]
        
    return speakerID_to_sex
        
sex_mapping = {}
def get_diff_subgroup(featureDf):
    
    speakerID_to_sex = readDemographics()
                
    #The partner means the the partner has the same gender
    
    diffDic = {index:{'partner':{}} for index in featureDf.index}
    
    counter = 0    
    #sex_mapping = {}
    for index , row in featureDf.iterrows():
        sex = speakerID_to_sex[counter]
        sex_mapping[index] = sex
        counter += 1
    
    
    for index , row in featureDf.iterrows():
#         print index
#         print row
        speakerID = get_Individual_ID(index)
        speaker_group = get_group_ID(index)
        speaker_game = get_game_number(index)
        sex = sex_mapping[index]
        
#         print "for the speaker" + str(speakerID)+" the sex is "+Gender_Mapping[sex]
        if index == '2252 Game1-4':
            print 2252
        
        for index2 , row2 in featureDf.iterrows():
            if index2 == index:
                continue
            else:
                speaker2_group = get_group_ID(index2)
                
                sex2 = sex_mapping[index2] 
                
                print 
                if speaker_group == speaker2_group and sex == sex2:
                    for feature in row.index:
                        split = feature.split('@')
                        if len(split) == 1:
                            ext=''
                        else:
                            ext='@'+split[-1]
                        if not feature in ['#total'+ext]:
                            if not index2 in diffDic[index]['partner'].keys():
                                diffDic[index]['partner'][index2]={}
                            diffDic[index]['partner'][index2][feature] = abs(float(row[feature])/float(row['#total'+ext]) - float(row2[feature])/float(row2['#total'+ext]))
                            if index == '2252 Game1-4':
                                print 2252
                                print diffDic['2252 Game1-4']
    print "++++++++++diffDic++++++++++"       
    print diffDic                    
    return diffDic


def proximity_subgroup(diffDic):
    
    speaker_ID_sex = readDemographics()        
    
    partner_diff = {}
    other_diff = {}
    avgDic = {}
    proximity = {index:{} for index in diffDic.keys()}
    print "=====153"
    print diffDic['2252 Game1-4']
    for speaker in diffDic.keys():
        avgDic[speaker]={'partnerDiff':{}}
        partner_diff = {}
        other_diff = {}
        num=0
        for speaker2 in diffDic[speaker]['partner'].keys():
            if get_game_number(speaker) == get_game_number(speaker2):
                if not get_Individual_ID(speaker) == get_Individual_ID(speaker2):
                    if partner_diff == {}:
                        partner_diff = diffDic[speaker]['partner'][speaker2]
                        num+=1
                    else:
                        partner_diff = dict( (n, partner_diff.get(n, 0)+diffDic[speaker]['partner'][speaker2].get(n, 0)) for n in set(partner_diff)|set(diffDic[speaker]['partner'][speaker2]) )
                        num+=1
                else:
                    proximity[speaker]={f:{'partner_diff':0.0 } for f in diffDic[speaker]['partner'][speaker2]}
        #num = len(diffDic[speaker]['partner'])
        avgDic[speaker]['partnerDiff'] = dict( (n, partner_diff.get(n, 0)/num) for n in set(partner_diff) )
#         num=0
#         for speaker2 in diffDic[speaker]['other'].keys():
#             if get_game_number(speaker) == get_game_number(speaker2):
#                 if other_diff == {}:
#                     other_diff = diffDic[speaker]['other'][speaker2]
#                     num+=1
#                 else:
#                     other_diff = dict( (f, other_diff.get(f, 0)+diffDic[speaker]['other'][speaker2].get(f, 0)) for f in set(other_diff)|set(diffDic[speaker]['other'][speaker2]) )
#                     num+=1
#         #num = len(diffDic[speaker]['other'])
#         avgDic[speaker]['otherDiff'] = dict( (n, other_diff.get(n, 0)/num) for n in set(other_diff) )
        #print speaker
        print "183"
        print avgDic['2252 Game1-4']
        proximity[speaker] = dict((f ,{'partnerDiff': avgDic[speaker]['partnerDiff'][f]})  for f in set(avgDic[speaker]['partnerDiff']))
#         proximity[speaker] = dict((f ,dict((('partnerDiff', avgDic[speaker]['partnerDiff'][f]), ('otherDiff',avgDic[speaker]['otherDiff'][f]))))  for f in set(avgDic[speaker]['partnerDiff']))
    
    proximitynew = {}
    length={}
    
    print "!!!!!!!!!!!!!proximity!!!!!!!!!!!!"
    print len(proximity)
    print proximity['2252 Game1-4']
    print "!!!!!!!!!!!!!sex!!!!!!!!!!!!"
    print sex_mapping['2252 Game1-4']
    
    for speaker in proximity.keys():
        teamid = get_group_ID(speaker)
        gameid = get_game_number(speaker)
        id = teamid
#         print "==============speaker=========="
#         print speaker                    
#         print id
#         
#         print proximity[speaker]
        
        sex = Gender_Mapping[sex_mapping[speaker]]
#         print sex
            
        if not id in proximitynew.keys():
            proximitynew[id] = {}
            length[id] = {'Female':0,'Male':0}
            length[id][sex]=1
        else:
            length[id][sex]+=1
        for f in proximity[speaker].keys():
#             proximitynew[id][f+'@FemaleDiff'] = 0.0
#             proximitynew[id][f+'@MaleDiff'] = 0.0

            if not f+'@'+sex+'Diff' in proximitynew[id].keys():
                proximitynew[id][f+'@'+sex+'Diff'] = proximity[speaker][f]['partnerDiff']
            else:
                proximitynew[id][f+'@'+sex+'Diff'] += proximity[speaker][f]['partnerDiff']
        
    for id in proximitynew.keys():
        for f in proximitynew[id].keys():
            if 'Female' in f:   
                proximitynew[id][f] = proximitynew[id][f]  / length[id]['Female']
            else:
                proximitynew[id][f] = proximitynew[id][f]  / length[id]['Male']
    print '================proximitynew============'
        
    print proximitynew['2252']
    #proximityDf = pd.DataFrame.from_dict(proximitynew, orient='index')
    print"-----------------"
#     print proximitynew
#     print len(proximitynew)
#     return proximitynew
    

#----------------------------------------------------------

def proximity(diffDic):
    partner_diff = {}
    other_diff = {}
    avgDic = {}
    proximity = {index:{} for index in diffDic.keys()}
    for speaker in diffDic.keys():
        avgDic[speaker]={'partnerDiff':{},'otherDiff':{}}
        partner_diff = {}
        other_diff = {}
        num=0
        for speaker2 in diffDic[speaker]['partner'].keys():
            if get_game_number(speaker) == get_game_number(speaker2):
                if not get_Individual_ID(speaker) == get_Individual_ID(speaker2):
                    if partner_diff == {}:
                        partner_diff = diffDic[speaker]['partner'][speaker2]
                        num+=1
                    else:
                        partner_diff = dict( (n, partner_diff.get(n, 0)+diffDic[speaker]['partner'][speaker2].get(n, 0)) for n in set(partner_diff)|set(diffDic[speaker]['partner'][speaker2]) )
                        num+=1
                else:
                    proximity[speaker]={f:{'partner_diff':0.0 , 'other_diff':0.0} for f in diffDic[speaker]['partner'][speaker2]}
        #num = len(diffDic[speaker]['partner'])
        avgDic[speaker]['partnerDiff'] = dict( (n, partner_diff.get(n, 0)/num) for n in set(partner_diff) )
        num=0
        for speaker2 in diffDic[speaker]['other'].keys():
            if get_game_number(speaker) == get_game_number(speaker2):
                if other_diff == {}:
                    other_diff = diffDic[speaker]['other'][speaker2]
                    num+=1
                else:
                    other_diff = dict( (f, other_diff.get(f, 0)+diffDic[speaker]['other'][speaker2].get(f, 0)) for f in set(other_diff)|set(diffDic[speaker]['other'][speaker2]) )
                    num+=1
        #num = len(diffDic[speaker]['other'])
        avgDic[speaker]['otherDiff'] = dict( (n, other_diff.get(n, 0)/num) for n in set(other_diff) )
        #print speaker
        proximity[speaker] = dict((f ,dict((('partnerDiff', avgDic[speaker]['partnerDiff'][f]), ('otherDiff',avgDic[speaker]['otherDiff'][f]))))  for f in set(avgDic[speaker]['partnerDiff']))
    proximitynew = {}
    length={}
    for speaker in proximity.keys():
        teamid = get_group_ID(speaker)
        gameid = get_game_number(speaker)
        id = teamid
            
        if not id in proximitynew.keys():
            proximitynew[id] = {}
            length[id]=1
        else:
            length[id]+=1
        for f in proximity[speaker].keys():
            if not f+'@partnerDiff' in proximitynew[id].keys():
                proximitynew[id][f+'@partnerDiff'] = proximity[speaker][f]['partnerDiff']
                proximitynew[id][f+'@otherDiff'] = proximity[speaker][f]['otherDiff']
            else:
                proximitynew[id][f+'@partnerDiff'] += proximity[speaker][f]['partnerDiff']
                proximitynew[id][f+'@otherDiff'] += proximity[speaker][f]['otherDiff']
        
    for id in proximitynew.keys():
        for f in proximitynew[id].keys():   
            proximitynew[id][f] = proximitynew[id][f]  / length[id]
    #proximityDf = pd.DataFrame.from_dict(proximitynew, orient='index')

    print "===========proximity============="
    print proximitynew
    return proximitynew
    
 


def get_diff_intervals(featureDf):
    diffDic = {index:{} for index in featureDf.index}
        
    for index , row in featureDf.iterrows():
        speakerID = get_Individual_ID(index)
        speaker_group = get_group_ID(index)
        speaker_game = get_game_number(index)
            
        for index2 , row2 in featureDf.iterrows():
            
            if index2 == index:
                continue
            else:
                print (index2)
                speaker2_group = get_group_ID(index2) 
                if speaker_group == speaker2_group:
                    if speaker_game == get_game_number(index2):
                            
                        for feature in row.index:
                            split = feature.split('@')
                            if len(split) == 1:
                                ext=''
                            else:
                                ext='@'+split[-1]
                            if not feature in ['#total'+ext]:
                                if not index2 in diffDic[index].keys():
                                    diffDic[index][index2]={}
                                diffDic[index][index2][feature] = abs(float(row[feature])/float(row['#total'+ext]) - float(row2[feature])/float(row2['#total'+ext]))
                
    return diffDic

def convergence_allparts_byteam_oneGame_intervals(diffDic):
        
    avgDic_game1 = {}
    numc1={}
        
    convergance_game1 = {}
    Entrainment_game1={}
    max_={}#{index:{} for index in diffDic.keys() if self.get_game_number(index) ==1}
    for speaker in diffDic.keys():
        speakerID = get_group_ID(speaker)+get_Individual_ID(speaker)
        teamID = get_group_ID(speaker)
        if not teamID in numc1.keys():
            numc1[teamID]=0
            Entrainment_game1[teamID] = {}
                
        numc1[teamID] = len(diffDic[speaker].keys())
        if not teamID in avgDic_game1.keys():
            avgDic_game1[teamID]={}
            convergance_game1[teamID]={}
        for speaker2 in diffDic[speaker].keys():

            if not get_Individual_ID(speaker) == get_Individual_ID(speaker2):
                    
                for feature in diffDic[speaker][speaker2].keys():
                    if not feature in avgDic_game1[teamID].keys():
                        avgDic_game1[teamID][feature] = 0.0
                        convergance_game1[teamID][feature] = 0.0
                            
                    avgDic_game1[teamID][feature] += diffDic[speaker][speaker2][feature]
                        
        
            
                #partID = str(partID).strip()
        for f in avgDic_game1[teamID].keys():  
                    
            convergance_game1[teamID][f] =  avgDic_game1[teamID][f]/numc1[teamID]
            if not f in max_.keys():
                max_[f] = 0
            if convergance_game1[teamID][f] > max_[f]:
                max_[f] = convergance_game1[teamID][f]
       
        
       # for teamID in Entrainment_game1.keys():
       #     for f in Entrainment_game1[teamID].keys():
       #         if f in ['pitch_min_firstHalf_secondHalf','pitch_max_firstHalf_secondHalf','pitch_mean_firstHalf_secondHalf', 'pitch_sd_firstHalf_secondHalf', 'shimmer_local_firstHalf_secondHalf', 'intensity_max_firstHalf_secondHalf', 'jitter_local_firstHalf_secondHalf', 'intensity_mean_firstHalf_secondHalf', 'intensity_min_firstHalf_secondHalf', 'pitch_mean_firstSeven_lastSeven', 'jitter_local_firstSeven_lastSeven', 'intensity_mean_firstSeven_lastSeven', 'shimmer_local_firstSeven_lastSeven', 'intensity_max_firstSeven_lastSeven', 'pitch_max_firstSeven_lastSeven', 'intensity_min_firstSeven_lastSeven', 'pitch_min_firstSeven_lastSeven', 'pitch_sd_firstSeven_lastSeven', 'pitch_min_firstThree_lastThree', 'jitter_local_firstThree_lastThree', 'intensity_min_firstThree_lastThree', 'pitch_mean_firstThree_lastThree', 'pitch_sd_firstThree_lastThree', 'intensity_mean_firstThree_lastThree', 'jitter_local_firstFive_lastFive', 'pitch_min_firstFive_lastFive', 'intensity_max_firstFive_lastFive', 'pitch_max_firstFive_lastFive','shimmer_local_firstFive_lastFive','pitch_sd_firstFive_lastFive','intensity_min_firstFive_lastFive','pitch_max_firstThree_lastThree','pitch_mean_firstFive_lastFive','intensity_max_firstThree_lastThree','shimmer_local_firstThree_lastThree','intensity_mean_firstFive_lastFive']:
       #             Entrainment_game1[teamID][f] = Entrainment_game1[teamID][f] / max_['_'.join(f.split('_')[:-1])]
    #converganceDf_game1 = pd.DataFrame.from_dict(convergance_game1, orient='index')
    return convergance_game1    
    
