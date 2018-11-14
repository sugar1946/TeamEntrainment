#Mingzhi Yu
#4/15/2018
from __future__ import division
from RandomGenerator import RandomGenerator
from LIWC_score_eachPlayer import LIWC_perTeam
import textProcessingUtil_new as util
import editdistance as ed
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import numpy as np
import random
import copy
import argparse
import glob
import pickle
import os
from collections import defaultdict
from scipy.stats import gaussian_kde, norm, entropy,ttest_ind,normaltest,ks_2samp
import gensim
from gensim.models import Word2Vec
from nltk.tokenize import sent_tokenize, word_tokenize

FILES = glob.glob('../../Corpus/Standardized/*.txt')

SAMPLE_SIZE = 30
SAMPLE_DIVISION = 7
STEP_SIZE = 5
WINDOW_SIZE = 20
WINDOW_DISTANCE = 4
LIWC_N_category = 8
EMBEDDING_MODEL = None

KL_THRESHOLD = 2

LINEAR_SPACE = np.linspace(-5, 5, 50)



class TDiff(object):

    def __init__(self, tdiff_method, spk_token_LIWCscore_dict, spk_token_index, windowSize=WINDOW_SIZE):
        self.windowSize = windowSize
        self.spk_token_LIWCscore_dict = spk_token_LIWCscore_dict
        self.spk_token_index = spk_token_index
        # print tdiff_method
        self.tdiff_method = tdiff_method
        # self.embedding = gensim.models.Word2Vec.load('embedding')

    # u1: utterance 1 (tokens)
    # u2: utterance 2 (tokens)
    def compare_utter_pair(self, lotokens1, lotokens2):


        # print "=========u1======="
        # print lotokens1
        # print "=========u2========"
        # print lotokens2
        # print "==========edit distance====="
        # Minimum Distance
        distance = ed.eval(lotokens1, lotokens2)

        # Word embedding cosine
        # distance = self.embedding.similarity(lotokens1,lotokens2)


        # print float(distance)

        return float(distance)


    def compare_utter_tdiff(self, loutters):

        # print self.tdiff_method

        if 'editDistance' in self.tdiff_method:

            return self.compare_utter_tdiff_editDistance(loutters)

        elif 'LIWC' in self.tdiff_method:

            return self.compare_utter_tdiff_LIWC(loutters, self.spk_token_LIWCscore_dict, self.spk_token_index)

    def compare_utter_tdiff_LIWC(self, loutters, spk_token_LIWCscore_dict, spk_token_index):

        liwc = LIWC_perTeam()

        if 'unweighted' in self.tdiff_method:

            return liwc.TDiff_unweighted(LIWC_N_category, loutters, spk_token_LIWCscore_dict, spk_token_index)

        elif 'weighted' in self.tdiff_method:

            return liwc.TDiff_weighted(LIWC_N_category, loutters, spk_token_LIWCscore_dict, spk_token_index)

        else:

            raise ValueError('The TDiff method does not exist')


    # loutters :[(spk1,u1),(spk2,u2)]
    def compare_utter_tdiff_editDistance(self, loutters):

        # print "======All utterances====="
        # print loutters

        spks = set([utter[0] for utter in loutters])
        spk_dict = defaultdict(lambda: [])
        for spk, utter in loutters:
            spk_dict[spk].append(utter)

        # print "=======spk_dict"
        # print spk_dict

        pair_dict = defaultdict(lambda: 0)
        for spk1 in spk_dict:
            for spk_2 in spk_dict:
                if spk1 != spk_2:

                    total_utterPair = 0
                    distance_spk1spk2 = 0
                    for u1 in spk_dict[spk1]:

                        distance_u1u2all = 0
                        for u2 in spk_dict[spk_2]:
                            # print "=======Utterance Difference====="
                            # print spk1, u1
                            # print spk_2, u2
                            # print ed.eval(u1,u2)
                            distance_u1u2all += ed.eval(u1, u2)
                            total_utterPair += 1

                            # print distance_u1u2all

                        distance_spk1spk2 += distance_u1u2all

                    # print "======distance_spk1spk2======"
                    # print distance_spk1spk2
                    # print "======Total utter Pair======"
                    # print total_utterPair
                    distance_spk1spk2 = distance_spk1spk2 / total_utterPair
                    pair_dict[str(spk1)+str(spk_2)] = distance_spk1spk2

                    # print '=======Pair Dict====s'
                    # print pair_dict

        # print "======Pair dict======="
        # print pair_dict
        sum_diff = (sum([pair_dict[pair] for pair in pair_dict]) / 2) # divided by 2 because the pair has been repeated
        number_pairs = len(pair_dict) / 2
        tdiff =   sum_diff/ number_pairs
        #
        # print "===========tdiff========"
        # print float(tdiff)
        return float(tdiff)

    def compare_utter_convergence(self, loutter1, loutter2):

        tdiff_1 = self.compare_utter_tdiff(loutter1)
        tdiff_2 = self.compare_utter_tdiff(loutter2)
        # print "=========Tdiff_1, Tdiff_2==========="
        # print tdiff_1, tdiff_2
        # print "=====convergence====="
        # print tdiff_1-tdiff_2

        return (tdiff_1-tdiff_2)





class Generate_distribution():

    def __init__(self, processed_line_generic, processed_line_random, spk_token_LIWCscore_dict, spk_token_index, window=WINDOW_SIZE):
        self.processed_line_generic = processed_line_generic
        self.processed_line_random = processed_line_random
        self.spk_token_LIWCscore_dict = spk_token_LIWCscore_dict
        self.spk_token_index = spk_token_index
        self.window = window
        self.KL_generic_random = 0
        self.KL_random_generic = 0
        self.game_length = len(self.processed_line_generic)

        global SAMPLE_SIZE
        SAMPLE_SIZE = int(self.game_length / SAMPLE_DIVISION)

        print "=========SAMPLE SIZE====="
        print SAMPLE_SIZE



    # input is processed lines [(spk1,u1),(spk2,u2)...]
    def sampling(self,processed_lines):

        # print "=======The Window Size======="
        # print self.window

        i = random.randint(0, len(processed_lines)-self.window)
        # print "i: " + str(i)
        lo_utter_1 = [processed_lines[i + x] for x in range(self.window)]

        r = range(0, i - WINDOW_DISTANCE) + range(i + 1 + WINDOW_DISTANCE, len(processed_lines)-self.window)
        # print "====The range of r======"
        # print r
        j = random.choice(r)
        j = random.randint(0, len(processed_lines) - self.window)
        # print "j: " + str(j)


        lo_utter_2 = [processed_lines[j + y] for y in range(self.window)]



        # print "======First window======"
        # print lo_utter_1
        # # "=======convergence here is temporarily set as absolute value"
        # # convergence = abs(lo_utter_1 - lo_utter_2)
        # print lo_utter_2 #,convergence
        # print "======Second window======"
        # print lo_utter_2
        return (lo_utter_1,lo_utter_2)

    def main(self, windowSize, tdiff_method):

        tdiff = TDiff(tdiff_method, self.spk_token_LIWCscore_dict, self.spk_token_index, windowSize)
        self.window = windowSize


        s = SAMPLE_SIZE
        # for generic dialogue

        samples_generic = []
        while s != 0:

            print "======= Generic : Num. Sample======"
            print str(SAMPLE_SIZE - s)
            lo_utter_1, lo_utter_2 = self.sampling(self.processed_line_generic)

            spks_1 = set([u[0] for u in lo_utter_1])
            spks_2 = set([u[0] for u in lo_utter_2])

            # print "======len(spks_1), len(spks_2)===="
            # print len(spks_1), len(spks_2)

            if len(spks_1) > 1 and len(spks_2) > 1:
                s -= 1
                x = tdiff.compare_utter_convergence(lo_utter_1, lo_utter_2)
                samples_generic.append(x)

        # xprint "========sample_generic======"
        # print len(samples_generic)

        s = SAMPLE_SIZE
        # for random dialogue
        samples_random = []
        while s != 0:
            print "======= Random : Num. Sample======"
            print str(SAMPLE_SIZE - s)
            lo_utter_1, lo_utter_2 = self.sampling(self.processed_line_random)

            spks_1 = set([u[0] for u in lo_utter_1])
            spks_2 = set([u[0] for u in lo_utter_2])

            # print "======168====="
            # print lo_utter_2, lo_utter_1

            if len(spks_1) > 1 and len(spks_2) > 1:
                s -= 1
                x = tdiff.compare_utter_convergence(lo_utter_1, lo_utter_2)
                samples_random.append(x)

        # print "========sample_random======"
        # print len(samples_random)
        #
        # print "========sample_generic======"
        # print samples_generic

        # return (samples_generic,samples_random)
        self.samples_generic = samples_generic
        self.samples_random = samples_random
        generic_distribution = gaussian_kde(samples_generic)
        random_distribution = gaussian_kde(samples_random)
        # print "========Distributions======="
        # print generic_distribution, random_distribution


        # print "=======Plot==========="
        # # Plot the true distribution
        # # Estimating the pdf and plotting
        #
        # xt = plt.xticks()[0]
        # xmin, xmax = min(xt), max(xt)
        # lnspc = np.linspace(-20, 20, len(samples_generic))
        #
        # plt.plot(lnspc, generic_distribution(lnspc), 'r', label="KDE generic",color='blue')
        # plt.plot(lnspc, random_distribution(lnspc), 'r', label="KDE random",color='red')
        # # plt.hist([samples_random,samples_generic],bins=30, normed=True,label=['random','generic'])
        # # plt.hist(samples_generic, bins=30, normed=True,label='generic')
        # # plt.plot(x, norm.pdf(x, mu, stdv), label="parametric distribution", color="red")
        # plt.legend()
        # # plt.title("Returns: parametric and estimated pdf")
        # plt.show()

        print "========KL divergence======="
        self.generic_distribution = generic_distribution
        self.random_distribution = random_distribution

        min_x =  max(min(samples_generic),min(samples_random))
        max_x = min(max(samples_generic),max(samples_random))
        # global LINEAR_SPACE
        lnspc = np.linspace(min_x, max_x, 100)
        # LINEAR_SPACE = lnspc

        ent = entropy(generic_distribution.pdf(LINEAR_SPACE), random_distribution.pdf(LINEAR_SPACE))
        # print ent
        self.KL_generic_random = ent
        self.KL_random_generic = entropy(random_distribution.pdf(LINEAR_SPACE), generic_distribution.pdf(LINEAR_SPACE))

        print "-----------generic distribution-----------"
        print generic_distribution.pdf(LINEAR_SPACE)

        print "-----------random distribution-----------"
        print random_distribution.pdf(LINEAR_SPACE)

        print "generic_random "+str(self.KL_generic_random)
        print "random_generic " + str(self.KL_random_generic)






class Main():

    def __init__(self, file, tag, tdiff):
        self.file = file
        self.tag = tag
        self.tdiff = tdiff
        self.game_name=os.path.basename(file)[:8]
        self.processed_file()


    def processed_file(self):

        with open(self.file, "r+") as f:

            print "=======Process File " + self.game_name + "======"
            l = [line for line in f.readlines() if line != '\n']

            # processed line has the structure [(spk1,[tokens]),(spk1,[tokens]),(spk3,[tokens])]
            processed_lines_generic = util.overallprocess_lines(l)
            print "Total number of utterances: " + str(len(processed_lines_generic))
            self.game_utterance = len(processed_lines_generic)


            spk_tokens_pair_LIWCscore_dict = 'output_timeInterval_study/' + str(self.tag) + '/object/' + self.game_name \
                                              + '_spk_tokens_pair_LIWCscore_dict.p'
            all_sentences = 'output_timeInterval_study/' + str(self.tag) + '/object/' + self.game_name \
                                             + '_all_sentences.p'


            if os.path.isfile(spk_tokens_pair_LIWCscore_dict) and os.path.isfile(all_sentences):
                self.spk_tokens_pair_LIWCscore_dict = pickle.load(open(spk_tokens_pair_LIWCscore_dict,'r+'))
                self.all_sentences = pickle.load(open(all_sentences,'r'))

            else:

                i = 0
                self.spk_tokens_pair_LIWCscore_dict = defaultdict()
                self.all_sentences = defaultdict()
                for processed_line in processed_lines_generic:

                    print i
                    # print processed_line
                    text = ' '.join(processed_line[1])
                    print (processed_line[0],text)

                    self.all_sentences[(processed_line[0],text)] = i


                    liwc = LIWC_perTeam()

                    text = ' '.join(processed_line[1])

                    self.spk_tokens_pair_LIWCscore_dict[i] = liwc.LIWC_score_text(LIWC_N_category, text)

                    i += 1

                pickle.dump(self.all_sentences, open(all_sentences,'w'))
                pickle.dump(self.spk_tokens_pair_LIWCscore_dict, open(spk_tokens_pair_LIWCscore_dict,'w'))

            # print self.all_sentences
            # print self.spk_tokens_pair_LIWCscore_dict



            # for spk_tokens_pair in processed_lines_generic:
            # #
            #      spk_tokens_pair_dict[spk_tokens_pair] = liwc.LIWC_score_text(LIWC_N_category, text)

            # global EMBEDDING_MODEL
            # EMBEDDING_MODEL = gensim.models.Word2Vec(all_sentences, size=100, min_count=1)
            # EMBEDDING_MODEL.save('embedding')
            # print "=============The generic file========="
            # print processed_lines_generic
            self.processed_lines_generic = processed_lines_generic

        rg = RandomGenerator(self.file)
        processed_lines_random = rg.generator()
        self.processed_lines_random = processed_lines_random

        # print "========The generic conversation======"
        # for u in self.processed_lines_generic:
        #     print u
        # print self.processed_lines_generic
        # print "========The random conversation======="
        # for w in self.processed_lines_random:
        #     print w
        # print self.processed_lines_random

    def main(self):

        windowSize = WINDOW_SIZE

        print "======Start to generate the distribution======"
        gd = Generate_distribution(self.processed_lines_generic, self.processed_lines_random, self.spk_tokens_pair_LIWCscore_dict, \
                                   self.all_sentences)

        gd.main(windowSize, self.tdiff)


        current_KL = 0
        prev_KL = 0
        early_stopping_count = 0
        best_KL = 0
        best_gd = copy.deepcopy(gd)

        while (early_stopping_count < 2) and (current_KL < float('Inf')): #(current_KL < KL_THRESHOLD ) and (windowSize <= self.game_utterance / 2) and (early_stopping_count < 3):# and (windowSize <= self.game_utterance / 2): #(((current_KL - prev_KL) >= 0) and and gd.KL_generic_random: #and windowSize <= 50:
            print "==========WINDOW SIZE======="
            print str(windowSize)
            print "KL: " + str(gd.KL_generic_random) + ", " + str(gd.KL_random_generic)
            windowSize = windowSize + STEP_SIZE
            gd.main(windowSize, self.tdiff)
            prev_KL = current_KL
            current_KL = gd.KL_generic_random

            # print current_KL - prev_KL
            print "----current kl, prev_kl------"
            print current_KL, prev_KL

            if best_KL <= current_KL:
                best_gd = copy.deepcopy(gd)
                best_KL = current_KL

            if (current_KL - prev_KL) < 0:
                 early_stopping_count += 1

                 # if best_KL <= prev_KL:
                 #     best_gd = copy.deepcopy(gd)
                 #     best_KL = prev_KL
                     #
                     # best_KL = max(prev_KL, best_KL)
                     # best_windowSize = windowSize - STEP_SIZE
                     # best_gd_samples_generic = gd.samples_generic
                     # best_gd_samples_random = gd.samples_random

            else:
                 early_stopping_count = 0

            print '------early_stopping_count-------'
            print early_stopping_count

            print "------gd, best_gd-------"
            print gd.KL_generic_random, gd.window
            print best_gd.KL_generic_random, best_gd.window


        print "=======normal test ======"

        print "generic: "+str(normaltest(best_gd.samples_generic))
        print "random: "+str(normaltest(best_gd.samples_random))

        print "========KS test (for non-parametric)========"
        t2, p2 = ks_2samp(best_gd.samples_generic, best_gd.samples_random)
        print("ks = " + str(t2))
        print("p = " + str(2 * p2))
        ttest = (t2, 2 * p2)

        print "=====Stop to converge===="
        print "Window Size: "+str(best_gd.window)
        print "KL: "+str(best_KL)# + ", " + str(gd.KL_random_generic)
        print "KS test: " + str(ttest)

        # lnspc = np.linspace(-20, 20, SAMPLE_SIZE)


        fig = plt.figure()
        fig.suptitle(self.game_name, fontsize=20)
        plt_1 = fig.add_subplot(221)
        plt_1.plot(LINEAR_SPACE, gd.generic_distribution.pdf(LINEAR_SPACE), 'r', label="PDF generic", color='green')
        plt_1.plot(LINEAR_SPACE, gd.random_distribution.pdf(LINEAR_SPACE), 'r', label="PDF random", color='red')
        plt_1.legend(loc='lower center', bbox_to_anchor=(0.5, -0.4),
          fancybox=True, shadow=True, ncol=5)
        # fig1.show()

        # plt_2 = fig.add_subplot(222)
        # plt_2.plot(LINEAR_SPACE, gd.generic_distribution(LINEAR_SPACE), 'r', label="KDE generic", color='green')
        # plt_2.plot(LINEAR_SPACE, gd.random_distribution(LINEAR_SPACE), 'r', label="KDE random", color='red')
        # plt_2.legend(loc='lower center', bbox_to_anchor=(0.5, -0.05),
        #               fancybox=True, shadow=True, ncol=5)

        # fig2 = plt.figure(2)
        plt_2 = fig.add_subplot(222)
        plt_2.hist(gd.samples_generic, bins=30, color='green', alpha = 0.3, normed=True,label='generic')
        plt_2.hist(gd.samples_random, bins=30, color='red', alpha = 0.3,normed=True, label='random')
        # plt.hist(samples_generic, bins=30, normed=True,label='generic')
        # plt.plot(x, norm.pdf(x, mu, stdv), label="parametric distribution", color="red")
        plt_2.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
          fancybox=True, shadow=True, ncol=5)
        # plt.title("Returns: parametric and estimated pdf")
        # fig2.show()

        fig.savefig('output_timeInterval_study/' + str(self.tag) + '/' + self.game_name)

        # plt.show()


        return (self.game_name, windowSize, gd.KL_generic_random, gd.KL_random_generic, ttest[0],ttest[1])


        # raw_input()









if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('-f', action='store', dest='file',
                        help='calculate for a file. If you do not specify a file, then all the files under \
                        default directory will be counted')
    parser.add_argument('-t', action='store', dest='tag',
                        help='tag for the date')
    parser.add_argument('tdiff', action='store',
                       help='choose from editDistance, LIWC_unweighted, LIWC_weighted')


    args = parser.parse_args()
    print args

    if args.tag:

        path = 'output_timeInterval_study/' + args.tag

        if not os.path.exists(path):
            os.makedirs(path)
            os.makedir(path + '/object/')

    if (args.file):

        main = Main(args.file, args.tag, args.tdiff)
        main.main()

    else:

        output_csv = open("output_timeInterval_study/" + args.tag +"/game_window_KL_" + args.tdiff + '.csv', 'w+')
        for f in FILES:
            main = Main(f, args.tag, args.tdiff)
            # output_var = main.main()
            return_list = list(main.main())
            return_list.append(main.game_utterance)
            return_list = [str(x) for x in return_list]
            # game_utterances = main.game_utterance
            #
            output_csv.write(",".join(return_list) + '\n')

            # output_csv.write("hello" + '\n')


        output_csv.close()








