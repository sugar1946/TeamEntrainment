
import os

top_dir = '/Volumes/litman/Transcriptions/Game1_text_transcripts/half_verified/Standardized/Text'


def main():

	corpus = open('Team0000.txt', 'a')
	for root, dirs, files in os.walk(top_dir):
		#print ("hello world 39")
		for file in filter(lambda file: file.endswith('.txt'), files):

			text = open(os.path.join(root, file), 'r+').read()+'\n'
			corpus.write(text)
			
	corpus.close()

main()
	
