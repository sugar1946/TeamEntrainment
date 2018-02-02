'''
# Mingzhi
# 01/19/2018
# LIWC_score_eachPlayer will take the number of LIWC category as input and output the LIWC score for each of the play
# in each of the team. It output will have the name convention LIWC_ncategory_eachPlayer.csv
# Usage:


#   python LIWC_score_eachPlayer.py number_of_category
'''

import textProcessingUtil_forLIWC as util
import glob, sys
import pandas as pd
import pickle
from subprocess import call

# Corpus: files are all the .txt in the corpus for each team
FILES = glob.glob('../Standardized/*.txt')

# Breakpoints are used in the convergence
BREAKPOINTS = pd.read_csv(
            '../breakingpoints_2intervals_v2.csv', index_col=0)

# Ignored the text features
IGNORED_CATEGORY = ["Word Count", "Unique Words", "Other Punctuation", "All Punctuation", "Words Per Sentence", "Dictionary Words",
                    "Six Letter Words", "Numerals", "Newlines", "Sentences" ]

#64 Categories
CATEGORY_64 = ['they','nonfl','funct','feel','certain','insight','assent','number','sad','past','see','affect',\
               'negate','home','conj','preps','ppron','inhib','pronoun','adverb','space','filler','ipron','negemo',\
               'percept','quant','posemo','discrep','relativ','you','incl','achieve','body','cogmech','tentat','time',\
               'leisure','verb','hear','bio','article','excl','present','we','cause','work','ingest','motion','i',\
               'future','social','auxverb','shehe','death','humans','anger','swear','health','money','sexual','anx',\
               'relig','family','friend','#total']

#8 Categories
CATEGORY_8 = ['negate','conj','preps','ppron','adverb','quant','verb','auxverb']


class LIWC_perTeam(object):

    def __init__(self, file, n_category, intervals, team_num):
        self.team_num = team_num
        self.n_category = n_category
        self.intervals = intervals
        self.file = file

        # [(spk1:[w1,w2,w3]),(spk2:[w1,w2,w3])], w1: a processed word
        self.spk_allUtterance_list = []
        # {spk1:text}, text: a processed string. The concatenation of all utterances
        self.spk_allUtterance_text = {}
        # {spk:{cat:score}}
        self.LIWC_score_spk = {}

        # processed line has the structure [(spk1,[tokens]},(spk1,[tokens]),(spk3,[tokens])]
        # byInterval means the [proccessedlines for interval1, proccessedlines for interval2,...]
        self.processed_lines = []
        self.processed_lines_intervals = []
        self.utteranceNum_spk = {}

        # Start to initialize. Read all the
        self.preprocessing()

    def get_spk_allUtterance_text(self):
        return self.spk_allUtterance_text


    def get_LIWC_score_spl(self):
        return self.get_LIWC_score_spk

    # This fun will be used at each team level. The allUtterances are from all the team
    def allUtterance_bySpeaker(self, processed_lines):

        self.spk_allUtterance_list = processed_lines

        for u in self.spk_allUtterance_list:

            sent = ' '.join(u[1])

            if u[0] in self.spk_allUtterance_text:
                self.spk_allUtterance_text[u[0]] = self.spk_allUtterance_text[u[0]] + ' ' + sent
            else:
                self.spk_allUtterance_text[u[0]] = ''


    # this fun will return the LIWC score for each of the spk of each team
    # this fun will be used in the iterative loop for each team
    # input : a speakers utterances dictionary from a team : {spk:string,spk2:string}
    # output: dict = {spk:{cat:score}}
    # The Text features categories starting with Upper case such as Newline, Six length words are ignored
    def LIWC_score_bySpeaker(self):
        # Thd data structure for sentences are :
        # sent = [int(speaker_num),[](a list of words]+

        for speaker in self.spk_allUtterance_text:
            text = self.spk_allUtterance_text[speaker]
            pickle.dump(text, open("speaker_text", "w"))
            call(["python", "word_category_counter_origin.py", "speaker_text"])
            scores = pickle.load(open("scores.p", "r"))  # the scores should be a dictionary that : {category:score}
            for category in IGNORED_CATEGORY:
                try:
                    del scores[category]
                except KeyError:
                    print "Key" + category + " does not exist"

            # Adding #total to fit the entraiment caculation codes later run by LIWC_entrainment
            # #total is a dummy value which is 1


            if self.n_category == '64':
                for c in CATEGORY_64:
                    if c not in scores:
                        scores[c] = 0

                # print scores

            if self.n_category == '8':
                for c in CATEGORY_8:
                    if c not in scores:
                        scores[c] = 0

                keys = scores.keys()

                for k in keys:
                    if k not in CATEGORY_8:
                        del scores[k]

            scores['#total'] = 1
            self.LIWC_score_spk[speaker] = scores

        self.n_size = len(self.LIWC_score_spk)

    # Returning the structure [(spk1,[tokens]},(spk1,[tokens]),(spk3,[tokens])]
    def preprocessing(self):

        l = [line for line in self.file.readlines() if line != '\n']

        # processed line has the structure [(spk1,[tokens]},(spk1,[tokens]),(spk3,[tokens])]
        self.processed_lines = util.overallprocess_lines(l)

        if self.intervals == 0:
            self.processed_lines_intervals.append(self.processed_lines)
        else:
            end = 0
            for i in BREAKPOINTS.columns:
                start = end
                end = BREAKPOINTS.loc[int(self.team_num), i] + 1
                self.processed_lines_byIntervals.append(self.processed_lines[start:end])

        self.file.close()

    def total_player_counts(self):
        # Dictionary for speaker counts, key: speaker number, number of words uttered by speaker
        total = {}
        for sent in self.processed_lines:
            # iterate through every utterance for given speaker and increment for every word uttered
            for word in sent[1]:
                if sent[0] in total:
                    total[sent[0]] = total[sent[0]] + 1
                else:
                    total[sent[0]] = 1

        self.utteranceNum_spk = total

# This is the main function that iterates every file and
# calculate the LIWC score
def set_featurefile_single(n_category, intervals = 0):

    print "========================Corpus file list==================="
    print FILES

    # The dict record the LIWC scores for all players in the corpus

    scoreLIWC_allPlayers_corpus = {}

    for file in FILES:

        team_num = file[file.find('Team') + 4: file.find('Team') + 8]
        game_num = file[file.find('Game'):file.find('Game') + 5]

        print "============Reading Team " + str(game_num) + "========"
        input_file = open(file, 'r')
        print input_file

        liwc_perTeam = LIWC_perTeam(input_file, n_category, intervals, team_num)
        print "===========Finishing initialize the LIWC object========"
        print liwc_perTeam.processed_lines_intervals

        # has uttered given word
        for i, processed_lines in enumerate(liwc_perTeam.processed_lines_intervals):
            if len(liwc_perTeam.processed_lines_intervals) == 1:
                ext = ''
            else:
                j = i + 1
                ext = '@interval' + str(j)

            liwc_perTeam.allUtterance_bySpeaker(processed_lines)
            liwc_perTeam.LIWC_score_bySpeaker()

            print "=================Finish building liwc_perTeam============="
            print liwc_perTeam.LIWC_score_spk

            for player in range(liwc_perTeam.n_size):

                speaker_id = team_num + ' ' + game_num + '-' + str(player + 1)

                if not speaker_id in scoreLIWC_allPlayers_corpus:
                    scoreLIWC_allPlayers_corpus[speaker_id] = {}

                for category in liwc_perTeam.LIWC_score_spk[player+1]:

                    player_score = liwc_perTeam.LIWC_score_spk[player+1][category]

                    scoreLIWC_allPlayers_corpus[speaker_id][category + ext] = player_score

    print "==============scoreLIWC_allPlayers_corpus==============="
    print scoreLIWC_allPlayers_corpus
    df = pd.DataFrame.from_dict(scoreLIWC_allPlayers_corpus, orient='index')
    df.to_csv("LIWC_"+str(n_category) + "_category.csv")


if __name__ == '__main__':

    set_featurefile_single(sys.argv[1])

