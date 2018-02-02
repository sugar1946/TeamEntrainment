"""
@author: Anish , Zahra
Processes transcripts and extracts feature values for lexical proximity measures
Input: All game transcripts; lexical items to measure for proximity
Output: CSV file with feature values (number of utterances per speaker per word
and total number of utterances per speaker) 
"""

from nltk.stem import PorterStemmer
import pickle
import glob
import pandas as pd
import textProcessingUtil_forLIWC as util
from pandas.io.tests.parser import index_col

def read_word_pergame_file(filePath):
    wordset = []
    input_file = open(filePath, 'r')
    lines = input_file.readlines()
    input_file.close()
    i=0
    for line in lines:
        if i == 0:
            teamID = line.strip()
            i+=1
        elif line == '\n':
            i=0
        else:
            wordset.append(line.strip())  
            i+=1
    return set(wordset)

def read_word_file(filePath):
    input_file = open(filePath, 'r')
    lines = input_file.readlines()
    print lines
    input_file.close()
    wordset = set([line.strip() for line in lines])
    
    print wordset

    return wordset

def get_player_dict(processed_lines):
    player_dict = {}
    for sent in processed_lines:
        for word in sent[1]:
            #if speaker and word pair tuple is in dictionary, incremement value by 1
            if (sent[0], word) in player_dict:
                player_dict[(sent[0], word)]=player_dict[(sent[0], word)]+1
            #if speaker and word pair tuple is not in dictionary, add it with value 1
            else:
                player_dict[(sent[0], word)]= 1
    return player_dict

def get_total_player_counts(processed_lines):
    #Dictionary for speaker counts, key: speaker number, number of words uttered by speaker
    total = {}
    for sent in processed_lines:
        #iterate through every utterance for given speaker and increment for every word uttered
        for word in sent[1]:
            if sent[0] in total:
                total[sent[0]] = total[sent[0]] + 1
            else:
                total[sent[0]] = 1

    return total

#df = pandas.read_csv('/Users/atkumar10/Documents/Litman Lab/transcriptions/Game1_transcripts/full_topic_sigs_unverified/game_top_words.csv')
#word_iter = df.iterrows()
#while next(word_iter)
#prepare input files: all segment transcriptions 
def set_featurefile_single(files, infeature , outext = '.csv',  per_game=True , intervals = 0):
    files = glob.glob('/Volumes/Litman/Transcriptions/Game1_text_transcripts/half_verified/Standardized/Text/*.txt')
    breakpoints = pd.read_csv('/Volumes/Litman/Transcriptions/Game1_working_corpus_text/breakingpoints_2intervals_v2.csv' , index_col=0)
    speaker_id = []
    word_tokens = []
    total_tokens =[]

    print files


    #load dict with top topic words for each game (key is game number, value is list of top words)
    #r = open(infeature, 'rb')
    #game_words = pickle.load(r)
    #r.close()
    
    #LDA_topics = 
    
    #LDA_topics = set(w.strip() for w in LDA_topics.split(','))
    
    #word_list = [ps.stem(w) for w in game_words]
    #word_list = util.stem(game_words) #zara: you should not need to do this when you already stemmed words when creating top_25_topic_sigs
    if per_game:
        word_list = read_word_pergame_file(infeature)
    else:
        word_list = read_word_file(infeature)
    dfdict = {}          
    for file in files:
        team_num = file[file.find('Team')+4 : file.find('Team')+8]
        game_num = file[file.find('Game', 86, -1):file.find('Game', 86, -1)+5]
        if team_num == '4752':
            print team_num
            
        print "input files:"
        input_file = open(file, 'r')
        print input_file
        l = input_file.readlines()
#         print l
# 
#         if 'that' in l:
#             print True
        
            
        processed_lines = util.overallprocess_lines(l)
#         print "processed_lines"
#         print processed_lines
#         if 'that' in processed_lines:
#             print "True yes it is"
        processed_lines_intervals = []
        
        if intervals == 0:
            processed_lines_intervals.append(processed_lines)
        else:
            end = 0
            for i in breakpoints.columns:
                start = end
                end = breakpoints.loc[int(team_num),i]+1
                processed_lines_intervals.append(processed_lines[start:end])
        input_file.close()      

        
        #dictionary with key: tuple with (player number, word), value: number of times given player
        #has uttered given word
        for i , processed_lines in enumerate(processed_lines_intervals):
            if len(processed_lines_intervals) == 1:
                ext = ''
            else:
                j = i+1
                ext = '@interval'+str(j)
            player_dict = get_player_dict(processed_lines)
    
            #dictionary with key: speaker id, value: total number of words uttered 
            total_player_counts = get_total_player_counts(processed_lines)
    
            #word_list = [ps.stem(w) for w in ['and', 'with', 'but', 'chalices']
    
            for player in range(len(total_player_counts)):
                speaker_id = team_num + ' ' + game_num + '-' + str(player+1)
                if not speaker_id in dfdict:
                    dfdict[speaker_id] = {}
    
                for word in word_list:
#                     if 'that' == word:
#                         
#                         print word
#                         print "player_word_count"
#                         print player_dict[(player+1, word)]
                        #print player_dict
    
                    try:
                        player_word_count = player_dict[(player+1, word)]
                    except KeyError:
                        player_word_count = 0
                    
                        
                    dfdict[speaker_id][word+ext]=(player_word_count)
    
                try:
                    player_total = total_player_counts[player+1]
                except KeyError:
                    player_total = 0
                    
                dfdict[speaker_id]['#total'+ext]=(player_total)


    df = pd.DataFrame.from_dict(dfdict,orient='index')
    df.to_csv(infeature+outext)

            
set_featurefile_single(None,'LIWC_Top25Words_corpus_12_4' ,outext='(2).csv', per_game=False, intervals = 0)

