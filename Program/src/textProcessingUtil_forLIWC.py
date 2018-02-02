'''
Created on Feb 21, 2017

@author: zara
'''
# utility functions to pre-process the text such as stemming, tokenization, standardization, and stop word removal

from nltk import word_tokenize, FreqDist
from nltk.stem import PorterStemmer
import re, pickle
import sys, os
import glob, csv, re
#import pandas
from nltk.corpus import stopwords

ps = PorterStemmer()
stoplist = stopwords.words('english')
fillers = ['laughs', 'ta', 'tss', 'um', 'hmm', 'mmm', 'mm', 'hm','hhhmm',
           'tsss', 'tt', 'ttt', 'opp', 'op','ah', 'ahh', 'ahhh', 'uh', 'uhh',
           'mmhmm', 'ha', 'ooo', 'oo', 'mhmm', 'ch', 'mhm', 'mmk','em','eh',
           'mk', 'mmk', 'ttt', 'tt', 'umm', 'em', 'ee', 'hmmm', 'nnmm',
           'nnmhh', 'ehhh', 'oop', 'mmhm'  ]

#Mingzhi commented out the old version on 12/3
#to get a better result for LIWC

# def preprocess(line):
#     #delete (--)
#     text = line.replace('(--)', '')
#     #delete words adjoined by hyphen
#     hyphen_words = re.findall(r'-', line)
#     for h in hyphen_words:
#         #print text
#         text = text.replace(h, h[:-1])
#     #return string in all lower case
#     return text.lower()

def preprocess(line):
    #delete (--)
    text = line.replace('(--)', '')
    text = text.replace('...', ' ')
    text = text.replace('(', '')
    text = text.replace(')', '')

    
    #delete words adjoined by hyphen and ' as indicator of incomplete
    #if len(text.split('\'')) > 1:
    #    print line
    regex = re.compile(r'\b(\w+\-)(\W|\Z)', re.S)
    text = regex.sub(lambda m: m.group().replace('-',"",1), text)
    
    regex = re.compile(r'\b(\w+\')(\W|\Z)', re.S)
    text = regex.sub(lambda m: m.group().replace('\'',"",1), text)
    
    regex = re.compile(r'(\W|\A)(\'\w+)(\W|\Z)', re.S)
    text = regex.sub(lambda m: m.group().replace('\'',"",1), text)
    #if len(hyphen_words) >0:
    #for h in hyphen_words:
    #    print h[0]
    #    text = text.replace(h[0]+[h], h[:-1]+' ')
    #return string in all lower case
    return text.lower()

def remove_stopwords(tokens):
    words = [word for word in tokens if not word in stoplist]
    #print words
    return words
def remove_fillers(tokens):
    terms = [w for w in tokens if not w in fillers]
    return terms

def tokenize(line):
    #tokenize sentences
##    text = word_tokenize(line)
##    #delete puntuation
    punct = "?!.,:')(-;"
    # text = re.sub(r"'", ' ', line)
    text = re.sub(r"[/?/!/./,/:/)/(-/;]", ' ', line)
    textlist = text.split()
    return textlist

def define_speaker(sent_list):
    #return tuple with speaker number as first element, and tokenized string as second
    try:
        speaker_sent = (int(sent_list[0]), sent_list[1:])
        return speaker_sent

    except ValueError:
        print "Encountering Error!"
        print "Trying to print out sent_list"
        print sent_list


def stem(tokenized_line):
    return [ps.stem(w) for w in tokenized_line] 

def overallprocess(line):
    preprocessed_line = preprocess(line)
    # print "====preprocess====="
    # print preprocessed_line
    tokenized_line = tokenize(preprocessed_line)
    # print "===tokenized_line===="
    # print tokenized_line
    tokenized_line = remove_fillers(tokenized_line)
    # print "====filtered tokenized_line====="
    # print tokenized_line
    
    #Mingzhi modify this for repeating Gonozale's experiment

    #line_no_stopwords =  remove_stopwords(tokenized_line)

    #stemmed_line = stem(tokenized_line)
    
    return tokenized_line


# Return structure a list of [(spk,[word tokens])]
def overallprocess_lines(transcript_lines):
        processed_lines = []
        # print transcript_lines
        for line in transcript_lines:
            # print line
            try:
                speaker_sent = define_speaker(line)
                processed_line = overallprocess(speaker_sent[1])
                speaker_sent1 = (speaker_sent[0], processed_line)
                #add all processed lines to new list
                # print "======new utterance======"
                # print line
                processed_lines.append(speaker_sent1)
                # print speaker_sent1
            except:

                print "Encountered Error!"
                print "Trying to print out the line and transcript_lines"
                print line
                # print transcript_lines
                print speaker_sent
                # print speaker_sent[0],speaker_sent[1]
                # print processed_line
                # print speaker_sent1


        return processed_lines

def debugging():

    f = open("Team0000.txt", "r")
    text = f.readlines()
    # print "======print text====="
    # print text

    processed_lines = overallprocess_lines(text)

    # print processed_lines

# debugging()
