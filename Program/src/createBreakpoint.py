#Mingzhi Yu
#2/12/2018
#Team Entrainment Project
#This script batch transcripts of .xls and create the breakpoint
#of game by utterances

#Usage: python createBreakpoint -h (checkout the help mena)

import argparse
import pandas
import sys
import pandas as pd
import os
import csv
import __future__

EXCEL_PATH = '../../Corpus/Unstandardized_Excel/'

class BreakpointsCreator(object):

    def __init__(self,path=EXCEL_PATH):
        self.path = path


    #This function generate the breakpoint of one single file
    #Input: file name, the number of intervals
    #Return: a array [], the index is the nth interval, the value is the corresponding utterance ID
    def bp_single(self,filename,n_intervals):

        f_excel = pd.read_excel(self.path+filename)
        print "======Reading "+filename+"========="

        time_uttr_dic = {} # {utterance starting time: utterance number}
        for i in f_excel.index:
            time_uttr_dic[f_excel[u'Timestamp_Start'][i]] = i

        total_uttr = len(f_excel.index)
        duration = f_excel[u'Timestamp_End'][total_uttr-1]
        print "Duration of this audio: "+str(duration)

        len_interval = float(duration)/float(n_intervals)
        print "len of each interval: "+str(len_interval)

        utterance_byInterval = []
        keys = list(time_uttr_dic.keys())
        for n in range(1,int(n_intervals)+1):
            interval_stamp = n * len_interval
            #utterance_byInterval.append(interval_stamp)

            #Find the close time stamp
            closest_stamp = min(keys,key=lambda x:abs(x-interval_stamp))
            print "the close stamp is: "+str(closest_stamp)+" for interval "+str(interval_stamp)

            utterance_byInterval.append(time_uttr_dic[closest_stamp])

        return utterance_byInterval


    #This function iterate all the files under directory and generate the breakpoint for each file
    #Input: n_intervals
    #Return: nothing but saving a csv file that contains all the breakpoints
    def bp_all(self,n_intervals):

        team_breakpoints = {}

        for root, dirs, files in os.walk(self.path):

            for file in filter(lambda file: file.endswith('.xls'), files):

                team_Num = file[4:8]
                values = self.bp_single(file, n_intervals)
                team_breakpoints[team_Num] = values


        # with open('breakpoint_'+str(n_intervals)+'.csv','w') as output:
            # writer = csv.writer(output)
            # for key, value in team_breakpoints.items():
            #
            #     writer.writerow([key,value])
        pd.DataFrame.from_dict(data=team_breakpoints, orient='index').\
                to_csv('breakpoint_'+str(n_intervals)+'.csv', header=[str(x+1) for x in range(int(n_intervals))])









if __name__ == '__main__':

      bc = BreakpointsCreator()

      parser = argparse.ArgumentParser()
      parser.add_argument('-s', action='store',dest='file',
                          help='breakpoint for single file')
      parser.add_argument('-a', action='store_true',
                          help='breakpoint for all file')
      parser.add_argument('-n', action='store',dest='n_intervals',
                          help='the number of interval')

      args = parser.parse_args()

      if args.file:

          bc.bp_single(args.file, args.n_intervals)

      elif args.a:
          bc.bp_all(args.n_intervals)









