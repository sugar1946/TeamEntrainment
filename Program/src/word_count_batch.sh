#!/bin/bash
for i in /Volumes/litman/Transcriptions/Game1_text_transcripts/half_verified/Standardized/Text/*.txt
do
    python word_category_counter.py $i
    #str1="${i##*/}"
    #echo $str1
    #python word_category_counter.py $str1
done