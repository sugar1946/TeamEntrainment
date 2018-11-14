'''
# Mingzhi
# 10/23/2018
# LIWC_score_eachPlayer will take the number of LIWC category as input and output the LIWC score for each of the player
# in each of the team. It output will have the name convention LIWC_ncategory_eachPlayer.csv
# Usage:


#   python LIWC_score_eachPlayer.py number_of_category
'''

from __future__ import division
import glob, sys
import pandas as pd
import pickle
from subprocess import call
import argparse
import itertools
import numpy as np
from collections import defaultdict

CONFIG_PATH = ''

OUTPUT_PATH = '../output/'

# Corpus: files are all the .txt in the corpus for each team
FILES = glob.glob('../../Corpus/Standardized/*.txt')
#FILES = glob.glob('Team2301_Transcription_Game1_verified_ZR_bad_segment.txt')

# Breakpoints are used in the convergence
#BREAKPOINTS = pd.read_csv(
#            '../config/breakingpoints_2intervals_v2.csv', index_col=0)


# Ignored the text features
IGNORED_CATEGORY = [ "Unique Words", "Other Punctuation", "All Punctuation", "Words Per Sentence", "Dictionary Words",
                    "Six Letter Words", "Numerals", "Newlines", "Sentences" ]

#64 Categories
CATEGORY_64 = ['they','nonfl','funct','feel','certain','insight','assent','number','sad','past','see','affect',\
               'negate','home','conj','preps','ppron','inhib','pronoun','adverb','space','filler','ipron','negemo',\
               'percept','quant','posemo','discrep','relativ','you','incl','achieve','body','cogmech','tentat','time',\
               'leisure','verb','hear','bio','article','excl','present','we','cause','work','ingest','motion','i',\
               'future','social','auxverb','shehe','death','humans','anger','swear','health','money','sexual','anx',\
               'relig','family','friend','#total']

#8 Categories
CATEGORY_8 = ['negate','conj','preps','ppron','adverb','quant','article','auxverb','ipron','Word Count']



class LIWC_perTeam(object):



    # def __init__(self):
    #
    #     self.n_category = n_category
    #
    #     #list_utterances: [(spk1:[w1,w2,w3]),(spk2:[w1,w2,w3])], w1: a processed word
    #     self.list_utterances = list_utterances
    #
    #     # [(spk1:[w1,w2,w3]),(spk2:[w1,w2,w3])], w1: a processed word
    #     self.spk_allUtterance_list = []
    #     # {spk1:text}, text: a processed string. The concatenation of all utterances
    #     self.spk_allUtterance_text = {}
    #
    #
    #     # processed line has the structure [(spk1,[tokens]},(spk1,[tokens]),(spk3,[tokens])]
    #     # byInterval means the [proccessedlines for interval1, proccessedlines for interval2,...]
    #     self.processed_lines = []
    #     self.utteranceNum_spk = {}


    def get_spk_allUtterance_text(self):
        return self.spk_allUtterance_text


    def get_LIWC_score_spl(self):
        return self.get_LIWC_score_spk

    # This fun will be used at each team level. The allUtterances are from all the team
    def allUtterance_bySpeaker(self, processed_lines):

        spk_allUtterance_text = {}

        for u in processed_lines:

            sent = ' '.join(u[1])

            if u[0] in spk_allUtterance_text:
                spk_allUtterance_text[u[0]] = spk_allUtterance_text[u[0]] + ' ' + sent
            else:
                spk_allUtterance_text[u[0]] = '' + sent

        # print "self.spk_allUtterance_text"
        # print spk_allUtterance_text
        return spk_allUtterance_text

    # Reading the saved LIWC scores of text from dictionary
    def LIWC_score_bySpeaker_cached(self, n_category, processed_line, utterance_LIWCscore_dict, spk_token_dict):

        # print "======utterance_LIWCscore_dict======"
        # print utterance_LIWCscore_dict
        # print spk_token_dict

        spk_LIWC_score = defaultdict(lambda:{})  # {speaker: [noun:  # , ppron: # , word count:  #, ]}

        for spk_token in processed_line:

            speaker = spk_token[0]

            if speaker not in spk_LIWC_score:

                for c in CATEGORY_8:

                    spk_LIWC_score[speaker][c] = 0

            index = spk_token_dict[(spk_token[0], ' '.join(spk_token[1]))]

            LIWC_score = utterance_LIWCscore_dict[index]

            # print spk_token
            # print LIWC_score

            for category in LIWC_score:

                category_count = LIWC_score['Word Count'] * LIWC_score[category]

                spk_LIWC_score[speaker][category] += category_count

        # print spk_LIWC_score

        for spk in spk_LIWC_score:

            for category in spk_LIWC_score[spk]:

                if category != 'Word Count':

                    spk_LIWC_score[spk][category] = (spk_LIWC_score[spk][category] / spk_LIWC_score[speaker]['Word Count'])

        # print spk_LIWC_score
        return spk_LIWC_score


    # this fun will return the LIWC score for each of the spk of each team
    # this fun will be used in the iterative loop for each team
    # input : a speakers utterances dictionary from a team : {spk:string,spk2:string}
    # output: dict = {spk:{cat:score}}
    # The Text features categories starting with Upper case such as Newline, Six length words are ignored
    def LIWC_score_bySpeaker(self, n_category, spk_allUtterance_text):
        # Thd data structure for sentences are :
        # sent = [int(speaker_num),[](a list of words]+

        # {spk:{cat:score}}
        LIWC_score_spk = {}


        for speaker in spk_allUtterance_text:
            text = spk_allUtterance_text[speaker]
            # print "for speaker ", speaker
            # print text.strip().split(" ")
            # print "length"
            # print len(text.strip().split(" "))

            scores = {}
            # if text == '':
            #     for category in CATEGORY_64:
            #         scores[category] = 0.0

            # else:
            pickle.dump(text, open("speaker_text", "w"))
            call(["python", "word_category_counter_origin.py", "speaker_text"])
            scores = pickle.load(open("scores.p", "r"))  # the scores should be a dictionary that : {category:score}

            for category in IGNORED_CATEGORY:
                try:
                    del scores[category]
                except KeyError:
                    print "Key" + category + " does not exist"

            # Adding #total to fit the entrainment caculation codes later run by LIWC_entrainment
            # #total is a dummy value which is 1

            # print "========CATEGORY_8======="
            # print CATEGORY_8
            # print n_category

            if n_category == 64:
                for c in CATEGORY_64:
                    if c not in scores:
                        scores[c] = 0

                # print scores


            elif n_category == 8:
                for c in CATEGORY_8:
                    if c not in scores:
                        scores[c] = 0

                keys = scores.keys()

                # LS = 0
                for k in keys:
                    if k not in CATEGORY_8:
                        del scores[k]
                #
                # for k in scores:
                #     print k
                #     print scores[k]
                #     LS += scores[k]

            # scores['#total'] = 1


            # self.LIWC_score_spk_LS[speaker] = {'#total':1}

            #Therefore LIWC_score_spk is a 2D array [speaker, scores]
            LIWC_score_spk[speaker] = scores

        # The number of speakers
        # self.n_size = len(self.LIWC_score_spk)
        return LIWC_score_spk


    def LIWC_score_text(self, n_category, text):

        pickle.dump(text, open("text.p", "w"))
        call(["python", "word_category_counter_origin.py", "text"])
        scores = pickle.load(open("scores.p", "r"))


        for category in IGNORED_CATEGORY:
            try:
                del scores[category]
            except KeyError:
                print "Key" + category + " does not exist"

            # Adding #total to fit the entrainment calculation codes later run by LIWC_entrainment
            # #total is a dummy value which is 1

            # print "========CATEGORY_8======="
            # print CATEGORY_8
            # print n_category

            if n_category == 64:
                for c in CATEGORY_64:
                    if c not in scores:
                        scores[c] = 0

                # print scores


            elif n_category == 8:
                for c in CATEGORY_8:
                    if c not in scores:
                        scores[c] = 0

                keys = scores.keys()

                # LS = 0
                for k in keys:
                    if k not in CATEGORY_8:
                        del scores[k]
                #
                # for k in scores:
                #     print k
                #     print scores[k]
                #     LS += scores[k]

            # scores['#total'] = 1


            # self.LIWC_score_spk_LS[speaker] = {'#total':1}

            #Therefore LIWC_score_spk is a 2D array [speaker, scores]



        # The number of speakers
        # self.n_size = len(self.LIWC_score_spk)
        return scores


    def TDiff_unweighted(self, n_category, loutters, utterance_LIWCscore_dict, spk_token_dict):

        # spk_allUtterance_text = self.allUtterance_bySpeaker(loutters)
        # LIWC_score_spk = self.LIWC_score_bySpeaker(n_category, spk_allUtterance_text)

        LIWC_score_spk = self.LIWC_score_bySpeaker_cached(n_category, loutters, utterance_LIWCscore_dict, spk_token_dict)


        n_size = len(LIWC_score_spk)

        group_member = LIWC_score_spk.keys()

        pairs = list(itertools.combinations(group_member, 2))
        #
        # print "====All possible pairs===="
        # print pairs

        p_diff = 0

        for p in pairs:

            # print "======The diction of each speaker====="
            # print loutters
            # print LIWC_score_spk[p[0]]
            # print LIWC_score_spk[p[1]]

            spk1_list = []
            spk2_list = []
            for category in LIWC_score_spk[p[0]]:

                # print "category: " + str(category)

                spk1_list.append(LIWC_score_spk[p[0]][category])
                spk2_list.append(LIWC_score_spk[p[1]][category])


            spk1_scores = np.around(np.array(spk1_list), 3)
            spk2_scores = np.around(np.array(spk2_list), 3)

            p_diff += sum(abs(spk1_scores - spk2_scores))

        TDiff =  p_diff / len(pairs)

        return TDiff

    def TDiff_weighted(self, n_category, loutters, utterance_LIWCscore_dict, spk_token_dict):

        # spk_allUtterance_text = self.allUtterance_bySpeaker(loutters)
        # LIWC_score_spk = self.LIWC_score_bySpeaker(n_category, spk_allUtterance_text)

        LIWC_score_spk = self.LIWC_score_bySpeaker_cached(n_category, loutters, utterance_LIWCscore_dict, spk_token_dict)

        group_memeber = LIWC_score_spk.keys()
        # print "group member in this window"
        # print group_memeber

        # print "LIWC_score_spk"
        # print LIWC_score_spk


        pairs = list(itertools.combinations(group_memeber, 2))

        # print "====All possible pairs===="
        # print pairs

        p_diff = 0
        for p in pairs:

            # print "======The diction of each speaker====="
            #
            # print LIWC_score_spk[p[0]]
            # print LIWC_score_spk[p[1]]

            spk1_list = []
            spk2_list = []
            for category in LIWC_score_spk[p[0]]:

                # print "category: " + str(category)

                spk1_list.append(LIWC_score_spk[p[0]][category])
                spk2_list.append(LIWC_score_spk[p[1]][category])


            spk1_scores = np.around(np.array(spk1_list), 3)
            spk2_scores = np.around(np.array(spk2_list), 3)

            # print spk1_scores
            # print spk2_scores

            weight = spk1_scores + spk2_scores

            diff = abs(spk1_scores - spk2_scores)

            division = np.divide(diff, weight, out=np.zeros_like(diff), where=weight!=0)
            # print weight
            # print diff
            # print division
            # print diff/weight

            sum_diff = sum(division)

            p_diff += sum_diff

        TDiff = p_diff / len(pairs)

        return TDiff



if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('n', action='store',
                        help='the set of category')
    parser.add_argument('w', action='store',
                        help='The utterances window')


    args = parser.parse_args()

    print args

    if args.n:

        liwc_perTeam = LIWC_perTeam(args.n, args.w)


    else:
        print "Invalid input"

    #set_featurefile_single(sys.argv[1])

