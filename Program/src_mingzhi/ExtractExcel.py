from xml.etree import ElementTree as ET
import glob

CORPUS_PATH = '../../Corpus/Game1_working_corpus_xml/Team2301_Transcription_Game1_verified_ZR_segmented.xml'


class XMLParser():

    def read_file(self):

        for f in glob.glob(CORPUS_PATH):

            print f
            with open(f,'r+') as file:

                lines = file.readlines()

                for l in lines:
                    if 'segment' in l:
                         print l

if __name__ == '__main__':

    xmlparser = XMLParser()
    xmlparser.read_file()


