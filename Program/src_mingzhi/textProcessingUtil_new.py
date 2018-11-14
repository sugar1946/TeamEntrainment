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
fillers = ['laughs', 'ta', 'tss', 'umm', 'hmm', 'mmm', 'mm', 'hm','hhhmm',
           'tsss', 'tt', 'ttt', 'opp', 'op','ah', 'ahh', 'ahhh', 'uh', 'uhh',
           'mmhmm', 'ha', 'ooo', 'oo', 'mhmm', 'ch', 'mhm', 'oops','em','eh',
           'mk', 'mmk', 'ttt', 'tt', 'umm', 'em', 'ee', 'hmmm', 'nnmm',
           'nnhmm', 'ehhh', 'oop', 'mmhm' ,'oh', 'aw'  ]

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
    #punct = "?!.,:')(-;"
    #Mingzhi's processed for LIWC
    text = re.sub(r"[\?|\!|\.|\,|\:|\;]", ' ', line)
    #textlist =  word_tokenize(text)

    text = re.sub(r"'", ' ', text)
    #text = re.sub(r"[/?/!/./,/:/'/)/(-/;]", '', text)
    textlist = text.split()

    return textlist

def define_speaker(sent_list):
    #return tuple with speaker number as first element, and tokenized string as second
    #print sent_list[0]
    try:
        speaker_sent = (int(sent_list[0]), sent_list[1:])
    except:
        pass
    #print (speaker_sent)
    return speaker_sent
def stem(tokenized_line):
    return [ps.stem(w) for w in tokenized_line] 

def overallprocess(line):
    preprocessed_line = preprocess(line)
    tokenized_line = tokenize(preprocessed_line)
    tokenized_line = remove_fillers(tokenized_line)
    #line_no_stopwords =  remove_stopwords(tokenized_line)
    stemmed_line = stem(tokenized_line)
    
    return stemmed_line


    
def overallprocess_lines(transcript_lines):
        processed_lines = []
        for line in transcript_lines:
            if len(line) < 2:
                print "the length of the transcript_line is 2"
                continue
            speaker_sent = define_speaker(line)
            processed_line = overallprocess(speaker_sent[1])
            speaker_sent1 = (speaker_sent[0] , processed_line)
            #add all processed lines to new list
            if len(processed_line) > 0 :
                processed_lines.append(speaker_sent1)
        return processed_lines