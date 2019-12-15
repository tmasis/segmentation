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
        line = '# ' + line + ' #'
        line = line.split()
        lines.append(line)
    corpus.close()
    
    return lines

def get_stress_utts():
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
        # Add utterance marker to beginning and end of each utterance
        line = '# ' + line + ' #'
        line = line.split()
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


def if_stress(phon, line, ngram, i):
    vow_i = i-1
    # Find the vowel in the syllable
    while '0' not in phon and '1' not in phon and '2' not in phon:
        vow_i -= 1
        phon = line[vow_i]
    
    # If word ends on a stressed syllable
    if ('1' in phon) or ('2' in phon):
        
        # Increase transition probability
        return ngram[line[i-1].strip('012')][line[i+1].strip('012')]+.01

    # If word ends on an unstressed syllable
    else:

        # Decrease transition probability
        return ngram[line[i-1].strip('012')][line[i+1].strip('012')]-.05


def test_bigram(ngram, lines):
    # For each utterance
    for line in lines:
        end = False     # Not at end of line

        # Instantiate first boundary
        b1 = line[0]                # Define first boundary
        p21 = ngram[b1][line[1].strip('012')] # Probability of first boundary
        index = 2                   # Now at index 2 in line
        current = 0                 # Current possible word boundary

        # Instantiate second boundary
        for i in range(index, len(line)):
            if line[i] == '+':
                b2 = line[i-1]              # Second boundary
                p32 = if_stress(b2, line, ngram, i) # Probability of second boundary
                index = i + 2
                current = i
                break

        # Third boundary
        new = 0     # Next possible word boundary
        while end == False:
            for i in range(index, len(line)):
                if line[i] == '+':
                    b3 = line[i-1]
                    p43 = if_stress(b3, line, ngram, i)
                    index = i + 2
                    new = i
                    break
                if line[i] == '#':
                    b3 = line[i-1]
                    p43 = ngram[b3.strip('012')][line[i]]
                    end = True  # At end of line
                    break
                    
            # Determine if a boundary should be inserted
            #print(p32)
            #print(p21)
            #print(p43)
            if p32 < p21 and p32 < p43:
                # Replace syllable boundary with word boundary
                line[current] = '#'

            # Second boundary is now first, and third bounda ry is now second
            # Continue to loop through line until end is reached
            p21 = p32
            p32 = p43
            current = new
                    
    return lines


corp = get_utts()
bigram = train_bigram(corp)
test_corp = get_stress_utts()
segmented = test_bigram(bigram, test_corp)

# Print the resulting segmentation
for line in segmented:
    line = ' '.join(line)
    print(line.strip('# '))
