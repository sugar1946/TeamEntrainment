# Mingzhi Yu
# 4/15/2018

import textProcessingUtil_new as util
import argparse
import glob
import random
import copy

FILES = glob.glob('../../Corpus/Standardized/*.txt')

class RandomGenerator(object):

    def __init__(self, file):
        self.file = file

    def generator(self):

        with open(self.file, "r+") as f:

            l = [line for line in f.readlines() if line != '\n']

            # processed line has the structure [(spk1,[tokens]),(spk1,[tokens]),(spk3,[tokens])]

            processed_lines = util.overallprocess_lines(l)

            # print "=============The generic file========="
            # print processed_lines
            #
            # print "=============Shuffle the order========"
            random_permutation = copy.deepcopy(processed_lines)
            random.shuffle(random_permutation)
            # print random_permutation

        return random_permutation


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('-f', action='store', dest='file',
                        help='calculate for a file')

    args = parser.parse_args()
    print args

    if args.file:

        randomGen = RandomGenerator(args.file)
        new_file = randomGen.generator()

    else:

        for f in FILES:
            randomGen = RandomGenerator(f)
            new_file = randomGen.generator()






