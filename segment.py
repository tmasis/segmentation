import sys
import re
from collections import defaultdict


def get_utts():
    # First argument is corpus as a txt file; opens corpus
    corpusf = sys.argv[1]
    corpus = open(corpusf,"r")

    # Format the training data
    # lines is a list of lists, where each inner list is all the tokens
    #  in an utterance
    lines = []
    for line in corpus:
        # Replace word boundaries with syllable boundaries
        line = re.sub('#','+',line)
        # Remove stress marks
        line = re.sub('[0-2]','',line)
        # Add utterance marker to beginning and end of each utterance
        line = line.rstrip()
        line = line.split(' + ')
        line.insert(0,'#')
        line.append('#')
        lines.append(line)
    corpus.close()
    
    return lines

def train_bigram(lines):
    # Instantiate variables used to train bigram
    counts = defaultdict(int)
    bicounts = defaultdict(lambda: defaultdict(int))
    bigram = defaultdict(lambda: defaultdict(float))
    
    for line in lines:  # For each utterance
        for i in range(len(line)-1):
            # Every time you see a unigram, increase its count
            counts[line[i]] += 1
            # Every time you see a bigram, increase its count
            bicounts[line[i]][line[i+1]] += 1

    for phon1 in counts:
        for phon2 in counts: # For each bigram
            # bigram stores the probability of each bigram in a dict of dicts
            bigram[phon1][phon2] = bicounts[phon1][phon2]/float(counts[phon1])

    return bigram 


def test_bigram(ngram, lines):
    newlines = []
    # For each utterance
    for line in lines:
        newline = [line[0]]
        # For each syllable in the line
        for i in range(len(line)-3):
            newline.append(line[i+1])
            s1 = line[i]        #First syllable
            s2 = line[i+1]
            s3 = line[i+2]
            s4 = line[i+3]

            p21 = ngram[s1][s2]
            p32 = ngram[s2][s3]
            p43 = ngram[s3][s4]

            # Determine if a boundary should be inserted
            if p32 < p21 and p32 < p43:
                # Replace syllable boundary with word boundary
                newline.append('#')
            else:
                newline.append('+')
        newline.append(line[-2])
        newline.append(line[-1])
        newlines.append(newline)


    return newlines
       



corp = get_utts()
bigram = train_bigram(corp)
segmented = test_bigram(bigram, corp)

# Print the resulting segmentation
for line in segmented:
    line = ' '.join(line)
    line = line.strip('# ')
    print(line.strip('\n'))


