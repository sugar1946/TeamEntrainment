'''
@author: Zahra, Mingzhi
group LIWC entrainment
'''

import pandas as pd
import Entrainment as ent

OUTPUT_PATH = '../output/'
import argparse

def read_word_file(filePath):
    word_game_dic = []
    input_file = open(filePath, 'r')
    print('Reading file\n')
    lines = input_file.readlines()
    input_file.close()
    i = 0
    for line in lines:
        word_game_dic.append(line.strip())

    return word_game_dic


def read_word_pergame_file(filePath):
    word_game_dic = {}
    input_file = open(filePath, 'r')
    print('Reading file\n')
    lines = input_file.readlines()
    input_file.close()
    i = 0
    for line in lines:
        if i == 0:
            teamID = line.strip()
            word_game_dic[teamID] = []
            i += 1
        elif line == '\n':
            i = 0
        else:
            word_game_dic[teamID].append(line.strip())
            i += 1
    return word_game_dic


def read_words(filePath, pergame=False):
    if pergame:
        return read_word_pergame_file(filePath)
    else:
        return read_word_file(filePath)


def read_aggregate_frequency_file(featureFile):
    return ent.read_featureFile(featureFile)


# ------Mingzhi-----#
def read_aggregate_frequency_file_gender(featureFile):
    ret = pd.read_csv(featureFile)
    return ret


# ------------------#

def proximity_per_word(featureDF):
    diffDic = ent.get_diff(featureDF)
    proximity = ent.proximity(diffDic)
    return proximity


def convergence_per_word(featureDF):
    diffDic = ent.get_diff_intervals(featureDF)
    convergence_diff = ent.convergence_allparts_byteam_oneGame_intervals(diffDic)
    return convergence_diff


# ----------------Mingzhi-----------#
def proximity_sum_words_Gender(featureDF, words_per_team, method_name, intervals=False, per_team=True):
    proximity_sum = {}
    # proximity_sum_value={}
    proximity = proximity_per_word(featureDF)
    for teamID in proximity:
        # print (teamID)
        if not teamID in proximity_sum:
            proximity_sum[teamID] = {}
            # proximity_sum_value[teamID] = {}
        if not intervals:
            proximity_sum[teamID][method_name + '@FemaleDiff'] = 0.0
            proximity_sum[teamID][method_name + '@MaleDiff'] = 0.0
            # proximity_sum_value[teamID][method_name]=0.0
            # print proximity[teamID]
            #             for x in proximity:
            #                 print proximity[x]
            #             print proximity_sum[teamID]
            if per_team:
                for word in words_per_team[teamID]:
                    if word + '@FemaleDiff' in proximity[teamID] and word + '@MaleDiff' in proximity[teamID]:
                        # print (word , proximity[teamID][word+'@otherDiff'] - proximity[teamID][word+'@partnerDiff'],' ' , featureDF.loc[teamID+' Game1-1' , word] , featureDF.loc[teamID+' Game1-2' , word] , featureDF.loc[teamID+' Game1-3' , word])
                        proximity_sum[teamID][method_name + '@FemaleDiff'] += proximity[teamID][word + '@FemaleDiff']
                        proximity_sum[teamID][method_name + '@MaleDiff'] += proximity[teamID][word + '@MaleDiff']
            else:
                for word in words_per_team:
                    # print teamID , word  *********************************
                    if word + '@FemaleDiff' in proximity[teamID] and word + '@MaleDiff' in proximity[teamID]:
                        # print (word , proximity[teamID][word+'@MaleDiff'] - proximity[teamID][word+'@partnerDiff'],' ' , featureDF.loc[teamID+' Game1-1' , word] , featureDF.loc[teamID+' Game1-2' , word] , featureDF.loc[teamID+' Game1-3' , word])
                        # print word
                        proximity_sum[teamID][method_name + '@FemaleDiff'] += proximity[teamID][word + '@FemaleDiff']
                        proximity_sum[teamID][method_name + '@MaleDiff'] += proximity[teamID][word + '@MaleDiff']

            # proximity_sum_value[teamID][method_name] = proximity_sum[teamID][method_name+'@MaleDiff'] - proximity_sum[teamID][method_name+'@partnerDiff']
            # print (proximity_sum_value[teamID][method_name])
        else:
            for partID in ent.partIDs:
                proximity_sum[teamID][method_name + '@' + partID + '@partnerDiff'] = 0.0
                proximity_sum[teamID][method_name + '@' + partID + '@otherDiff'] = 0.0
                # proximity_sum_value[teamID][method_name+'@'+partID]=0.0
                if per_team:
                    for word in words_per_team[teamID]:
                        proximity_sum[teamID][method_name + '@' + partID + '@partnerDiff'] += proximity[teamID][
                            word + '@' + partID + '@partnerDiff']
                        proximity_sum[teamID][method_name + '@' + partID + '@otherDiff'] += proximity[teamID][
                            word + '@' + partID + '@otherDiff']
                else:
                    for word in words_per_team:
                        proximity_sum[teamID][method_name + '@' + partID + '@partnerDiff'] += proximity[teamID][
                            word + '@' + partID + '@partnerDiff']
                        proximity_sum[teamID][method_name + '@' + partID + '@otherDiff'] += proximity[teamID][
                            word + '@' + partID + '@otherDiff']

                # proximity_sum_value[teamID][method_name+'@'+partID] = proximity_sum[teamID][method_name+'@'+partID+'@otherDiff'] - proximity_sum[teamID][method_name+'@'+partID+'@partnerDiff']

    proximity_diff_df = pd.DataFrame.from_dict(proximity_sum, orient='index')
    # proximity_value_df = pd.DataFrame.from_dict(proximity_sum_value, orient='index')
    return proximity_diff_df  # , proximity_value_df


# -----------------------------------------------------------------------------#

def proximity_sum_words(featureDF, words_per_team, method_name, intervals=False, per_team=True):
    proximity_sum = {}
    proximity_sum_value = {}
    proximity = proximity_per_word(featureDF)
    for teamID in proximity:
        print (teamID)
        if not teamID in proximity_sum:
            proximity_sum[teamID] = {}
            proximity_sum_value[teamID] = {}
        if not intervals:
            proximity_sum[teamID][method_name + '@partnerDiff'] = 0.0
            proximity_sum[teamID][method_name + '@otherDiff'] = 0.0
            proximity_sum_value[teamID][method_name] = 0.0

            # print proximity
            # print proximity_sum[teamID]
            if per_team:
                for word in words_per_team[teamID]:
                    if proximity[teamID][word + '@partnerDiff'] > 0:
                        print (
                        word, proximity[teamID][word + '@otherDiff'] ,proximity[teamID][word + '@partnerDiff'],proximity[teamID][word + '@otherDiff'] - proximity[teamID][word + '@partnerDiff'], ' ',
                        featureDF.loc[teamID + ' Game1-1', word], featureDF.loc[teamID + ' Game1-2', word],
                        featureDF.loc[teamID + ' Game1-3', word])
                        proximity_sum[teamID][method_name + '@partnerDiff'] += proximity[teamID][word + '@partnerDiff']
                        proximity_sum[teamID][method_name + '@otherDiff'] += proximity[teamID][word + '@otherDiff']
            else:
                for word in words_per_team:
                    print teamID , word  #*********************************
                    if proximity[teamID][word + '@partnerDiff'] > 0:
                        print (
                        word, proximity[teamID][word + '@otherDiff'], proximity[teamID][word + '@partnerDiff'], proximity[teamID][word + '@otherDiff'] - proximity[teamID][word + '@partnerDiff'], ' ',
                        featureDF.loc[teamID + ' Game1-1', word], featureDF.loc[teamID + ' Game1-2', word],
                        featureDF.loc[teamID + ' Game1-3', word])
                        # print word
                        proximity_sum[teamID][method_name + '@partnerDiff'] += proximity[teamID][word + '@partnerDiff']
                        proximity_sum[teamID][method_name + '@otherDiff'] += proximity[teamID][word + '@otherDiff']

            proximity_sum_value[teamID][method_name] = proximity_sum[teamID][method_name + '@otherDiff'] - \
                                                       proximity_sum[teamID][method_name + '@partnerDiff']

            # print "==============proximity_sum_value=========="
            # print (proximity_sum_value[teamID][method_name])
        else:
            for partID in ent.partIDs:
                proximity_sum[teamID][method_name + '@' + partID + '@partnerDiff'] = 0.0
                proximity_sum[teamID][method_name + '@' + partID + '@otherDiff'] = 0.0
                proximity_sum_value[teamID][method_name + '@' + partID] = 0.0
                if per_team:
                    for word in words_per_team[teamID]:
                        proximity_sum[teamID][method_name + '@' + partID + '@partnerDiff'] += proximity[teamID][
                            word + '@' + partID + '@partnerDiff']
                        proximity_sum[teamID][method_name + '@' + partID + '@otherDiff'] += proximity[teamID][
                            word + '@' + partID + '@otherDiff']
                else:
                    for word in words_per_team:
                        proximity_sum[teamID][method_name + '@' + partID + '@partnerDiff'] += proximity[teamID][
                            word + '@' + partID + '@partnerDiff']
                        proximity_sum[teamID][method_name + '@' + partID + '@otherDiff'] += proximity[teamID][
                            word + '@' + partID + '@otherDiff']

                proximity_sum_value[teamID][method_name + '@' + partID] = proximity_sum[teamID][
                                                                              method_name + '@' + partID + '@otherDiff'] - \
                                                                          proximity_sum[teamID][
                                                                              method_name + '@' + partID + '@partnerDiff']

    proximity_diff_df = pd.DataFrame.from_dict(proximity_sum, orient='index')
    proximity_value_df = pd.DataFrame.from_dict(proximity_sum_value, orient='index')
    return proximity_diff_df, proximity_value_df


def convergence_sum_words(featureDF, words_per_team, method_name, per_team):
    convergence_sum = {}
    convergence_sum_value = {}
    convergence = convergence_per_word(featureDF)
    for teamID in convergence:
        if not teamID in convergence_sum:
            convergence_sum[teamID] = {}
            convergence_sum_value[teamID] = {}
        for partID in ent.partIDs:
            convergence_sum[teamID][method_name + '@' + partID] = 0.0
            if per_team:
                for word in words_per_team[teamID]:
                    if convergence[teamID][word + '@' + partID] == 0.0:
                        print teamID, word, partID, 0
                        x = 1
                    convergence_sum[teamID][method_name + '@' + partID] += convergence[teamID][word + '@' + partID]
            else:
                for word in words_per_team:
                    if convergence[teamID][word + '@' + partID] == 0.0:
                        print teamID, word, partID, 0
                        x = 1

                    convergence_sum[teamID][method_name + '@' + partID] += convergence[teamID][word + '@' + partID]
        num = len(words_per_team)
        if per_team:
            wl = words_per_team[teamID]
        else:
            wl = words_per_team
        for word in wl:
            if convergence[teamID][word + '@' + 'interval1'] == 0.0 or convergence[teamID][
                word + '@' + 'interval2'] == 0.0:
                convergence_sum[teamID][method_name + '@' + 'interval1'] -= convergence[teamID][
                    word + '@' + 'interval1']
                convergence_sum[teamID][method_name + '@' + 'interval2'] -= convergence[teamID][
                    word + '@' + 'interval2']
                num -= 1
        print teamID, num, len(words_per_team)
        for partID in ent.partIDs:
            for partID2 in ent.partIDs:
                if int(partID[-1]) < int(partID2[-1]):
                    for ff in convergence_sum[teamID]:
                        f = ff[:-10]

                        convergence_sum_value[teamID][f + '@' + partID + '_' + partID2] = (
                                convergence_sum[teamID][f + '@' + partID] - convergence_sum[teamID][f + '@' + partID2])

        pos = 0
        neg = 0
        zero = 0
        if per_team:
            for word in words_per_team[teamID]:
                if convergence[teamID][word + '@' + 'interval1'] - convergence[teamID][word + '@' + 'interval2'] > 0:
                    pos += 1
                elif convergence[teamID][word + '@' + 'interval1'] - convergence[teamID][word + '@' + 'interval2'] < 0:
                    neg += 1
                else:
                    zero += 1
        else:
            for word in words_per_team:
                if convergence[teamID][word + '@' + 'interval1'] - convergence[teamID][word + '@' + 'interval2'] > 0:
                    pos += 1
                elif convergence[teamID][word + '@' + 'interval1'] - convergence[teamID][word + '@' + 'interval2'] < 0:
                    neg += 1
                else:
                    zero += 1
        # print teamID , 'numpos ' , pos , ' num neg '  , neg , ' num zero '  , zero
    convergence_diff_df = pd.DataFrame.from_dict(convergence_sum, orient='index')
    convergence_value_df = pd.DataFrame.from_dict(convergence_sum_value, orient='index')
    return convergence_diff_df, convergence_value_df


# featureDF_proximity = read_aggregate_frequency_file(
#     'LIWC_8_category.csv')
# words_per_team = read_words(
#     'CategoryList_8',
#     pergame=False)

# proximity_diff_df, proximity_value_df = proximity_sum_words(featureDF_proximity, words_per_team, 'LIWC_64_category', intervals= False, per_team = False)
# proximity_diff_df.to_csv('proximity_LIWC_8_category_diff.csv')
# proximity_value_df.to_csv('proximity_LIWC_8_category_value.csv')

# -----Mingzhi: Commen out if you want to calculate the proximity by gender----#
# proximity_diff_df_gender = proximity_sum_words_Gender(featureDF_proximity, words_per_team, 'LIWC_Top25Words_corpus_Highest_funct',intervals= False , per_team = False)
# proximity_diff_df_gender.to_csv('proximityDiff_LIWC_Top25Words_corpus_Highest_funct_byGender.csv')
# -----------------------------------------------------------------------------#

#
#featureDF_convergence = read_aggregate_frequency_file('/Volumes/litman/Transcriptions/Python/Lexical Entrainment/output/LIWC_Top25Words_corpus_Highest_funct_2intervals.csv')
# convergence_diff_df   , convergence_value_df = convergence_sum_words(featureDF_convergence, words_per_team, 'LIWC_Top25Words_corpus_Highest_funct_2intervals' , per_team = False)
# convergence_diff_df.to_csv('convergenceDiff_LIWC_Top25Words_corpus_Highest_funct_2intervals.csv')
# convergence_value_df.to_csv('convergence_LIWC_LIWC_Top25Words_corpus_Highest_funct_2intervals.csv')
#

if __name__ == '__main__':


    parser = argparse.ArgumentParser()
    parser.add_argument('p', action='store_true',
                        help='calculate the proximity based on the csv score')
    parser.add_argument('c', action='store_true',
                        help='calculate the convergence based on the csv score')
    parser.add_argument('--word', '-w', action='store', dest='word_List',
                        help='The category set')
    parser.add_argument('--score', '-s', action='store', dest='score',
                        help='The score file')
    parser.add_argument('--method', '-m', action='store',dext='method', help='the method name that will be displayed')

    args = parser.parse_args()

    featureDF = read_aggregate_frequency_file(
        args.score)
    words_per_team = read_words(
       args.word_List, pergame=False)

    if args.p:

        proximity_diff_df, proximity_value_df = proximity_sum_words(featureDF, words_per_team,
                                                                    args.method, intervals=False, per_team=False)
        proximity_diff_df.to_csv('proximity_'+args.method+'_diff.csv')
        proximity_value_df.to_csv('proximity_'+args.method+'_value.csv')

    elif args.c:
        convergence_diff_df, convergence_value_df = convergence_sum_words(featureDF, words_per_team, args.method,\
                                                                          per_team=False)
        convergence_diff_df.to_csv('convergence_'+args.method+'_diff.csv')
        convergence_value_df.to_csv('convergence_'+args.method+'_value.csv')
