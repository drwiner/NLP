from collections import namedtuple, Counter, defaultdict
from math import log2, sqrt
from clockdeco import clock

EXCLUDE = 'is are be was were said have has had and or >comma >squote >rparen >lparen >period >minus >ampersand'.split()

Triple = namedtuple('Triple', ['X', 'path', 'Y'])

# TStream (triple stream) - collects all triple instances
TStream = []

# distinct_filtered_Tinstances - distinct triples after minfreq
distinct_filtered_Tinstances = list()

# all_words - all words that appear in X or Y in distinct_filtered_Tinstances
all_words = dict()

# distinct_filtered_Pinstances - the set of paths after minfreq
distinct_filtered_Pinstances = set()

# distinct_unfiltered_Pinstances
distinct_unfiltered_Pinstances = set()

# word_freq - count of times a word appears in slot X or Y for distinct_filtered_Tinstances
word_freq = dict()

# triple_database - Triple Database - collection of triple instances by path
triple_database = defaultdict(dict)


def cleanLine(line):
	return ' '.join(line.split()) + ' '

def readCorpus(corpus_text):
	current_path = ''
	current_x = None
	in_path_tag = False
	for line in corpus_text:
		line_split = line.split()
		t = line_split[0]
		lang = [s.lower() for s in line_split[2:]]
		if lang[0] == '<eos':
			in_path_tag = False
			current_x = None
			# end whatever path was going on
			current_path = ''
			continue

		if t == 'NP' and not in_path_tag:
			in_path_tag = True
			current_x = lang[-1]
			continue

		elif t == 'NP' and in_path_tag:
			y = lang[-1]
			if current_path:
				# add triple if not a 1 excluded word path
				cp = current_path.split()
				if len(cp) > 1 or cp[0] not in EXCLUDE:

					# append Triple to the triple stream
					####################################
					TStream.append(Triple(current_x, current_path, y))
					####################################

				# flush path
				current_path = ''
			current_x = y
			continue

		elif t != 'NP' and in_path_tag:
			path_str = ' '.join(lang)
			current_path += path_str + ' '

def apply_MinfreqFilter(min_freq):

	global  TStream, \
			distinct_filtered_Tinstances, \
			distinct_filtered_Pinstances, \
			filtered_Tinstances, \
			distinct_unfiltered_Pinstances

	PCounter = Counter([t.path for t in TStream])
	distinct_unfiltered_Pinstances = set(PCounter.keys())
	distinct_filtered_Pinstances = set(p for p in distinct_unfiltered_Pinstances if PCounter[p] >= min_freq)

	# TCounter = Counter(TStream)
	filtered_Tinstances = [t for t in TStream if PCounter[t.path] >= min_freq]
	distinct_filtered_Tinstances = set(filtered_Tinstances)

	print('Found {} distinct paths, {} after minfreq filtering'.format(len(distinct_unfiltered_Pinstances), len(distinct_filtered_Pinstances)))
	print('Found {} path instances, {} after minfreq filtering'.format(len(TStream), len(filtered_Tinstances)))

	return len(distinct_unfiltered_Pinstances), len(distinct_filtered_Pinstances), len(TStream), len(filtered_Tinstances)

# Entry = namedtuple('Entry', ['word', 'count'=0, 'mi'])
class Entry:
	def __init__(self, path=None, slot=None, word=None):
		self.path = path
		self.slot = slot
		self.word = word
		self.count = 0
		self.mi = None

	def __hash__(self):
		return hash(self.path ^ self.slot ^ self.word)

	def update(self, path, slot, word):
		if self.word is None:
			self.word = word
		if self.slot is None:
			self.slot = slot
		if self.path is None:
			self.path = path
		self.count += 1


def getWordFillers(path, slot_pos):
	return set(trip._asdict()[slot_pos] for trip in distinct_filtered_Tinstances if trip.path == path)


def loadDatabase():
	# distinct_filtered_Tinstances used for all_words, |*, X, *| and |*, Y, *|
	all_words['X'] = set(t.X for t in distinct_filtered_Tinstances)
	all_words['Y'] = set(t.Y for t in distinct_filtered_Tinstances)

	# Triple database


	# step 1 - add entries
	for path in distinct_filtered_Pinstances:

		## Triple Database by-path
		path_db = triple_database[path]

		# database for each path has library of 'entries'
		path_db['X'] = defaultdict(Entry)
		pdbx = path_db['X']

		path_db['Y'] = defaultdict(Entry)
		pdby = path_db['Y']

		words_for_path_at_x = getWordFillers(path,'X')
		words_for_path_at_y = getWordFillers(path,'Y')

		#for each word in path at x, record count
		for word in words_for_path_at_x:
			pdbx[word].update(path, 'X', word)

		for word in words_for_path_at_y:
			pdby[word].update(path, 'Y', word)

	# count of times a word appears in slot X or Y for distinct_filtered_Tinstances
	print('scoring word freqs')
	word_freq_x, word_freq_y = dict(), dict()
	for word in all_words['X']:
		word_freq_x[word] = sum(1 for trip in filtered_Tinstances if trip.X == word)
	for word in all_words['Y']:
		word_freq_y[word] = sum(1 for trip in filtered_Tinstances if trip.Y == word)
	word_freq['X'] = word_freq_x
	word_freq['Y'] = word_freq_y

# @clock
def MI(path, slot_pos, word):

	wf = word_freq[slot_pos]
	pdb = triple_database[path][slot_pos]

	# the number of times this entry is noted
	psw = pdb[word].count
	if psw == 0:
		return 0

	# number of word elements appearing at slot (must be a path >= minfreq)
	_s_ = len(all_words[slot_pos])
	if _s_ == 0:
		return 0

	# number of unique word entries in this path's slot
	ps_ = len(pdb.keys())
	if ps_ == 0:
		return 0

	# the number of times the word appears at slot position
	_sw = wf[word]
	if _sw == 0:
		return 0

	return log2((psw * _s_) / (ps_ * _sw))


def updateMI():
	print('scoring MI')
	for path in triple_database.keys():
		# print(path)
		tdpx = triple_database[path]['X']
		tdpy = triple_database[path]['Y']

		for word, entry in tdpx.items():
			entry.mi = MI(entry.path, entry.slot, entry.word)
		for word, entry in tdpy.items():
			entry.mi = MI(entry.path, entry.slot, entry.word)


# @clock
def pathSim(p1, p2):
	slot_x_sim = slotSim(p1, p2, 'X')
	# print('slot-x sim : ' + str(slot_x_sim))
	slot_y_sim = slotSim(p1,p2,'Y')
	# print('slot-y-sim : ' + str(slot_y_sim))
	# print('pathsim: ' + str(slot_x_sim * slot_y_sim))
	if slot_x_sim * slot_y_sim < 0:
		return 0
	return sqrt(slot_x_sim * slot_y_sim)

# @clock
def slotSim(p1, p2, slot_pos):
	wd1 = triple_database[p1][slot_pos]
	wd2 = triple_database[p2][slot_pos]

	pd1 = set(wd1.keys())
	pd2 = set(wd2.keys())

	n_score = 0
	for word in pd1.intersection(pd2):
		n_score += wd1[word].mi + wd2[word].mi
	if n_score == 0:
		return 0


	d_score_1, d_score_2 = 0, 0
	for word in pd1:
		d_score_1 += wd1[word].mi
	for word in pd2:
		d_score_2 += wd2[word].mi
	d_score = d_score_1 + d_score_2
	if d_score == 0:
		return 0


	return n_score/d_score


import sys
for arg in sys.argv:
	print(arg, end=' ')
print('\n')
# if __name__ == '__main__':

corpus_text = open('corpus.txt')
output_text = open('output.txt', 'w')

#### Load TStream ####
readCorpus(corpus_text)

#### Apply MinFreq####
dp, dmf, pi, pimf = apply_MinfreqFilter(5)

output_text.write('Found {} distinct paths, {} after minfreq filtering.\n'.format(dp, dmf))
output_text.write('Found {} path instances, {} after minfreq filtering.\n'.format(pi, pimf))

#### Load Triple Databse (as in paper)
loadDatabase()
# update Mutual Information once all data is loaded
updateMI()


### read in comparison tests
test_text = open('test.txt')
test_paths = [cleanLine(line) for line in test_text]
import operator
tp_sim_score_dict = dict()
for tp in test_paths:
	# print(tp)
	path_test = dict()
	for p in distinct_filtered_Pinstances:
		ps = pathSim(tp,p)
		path_test[p] = ps
	# now, get the top 5:
	top_5 = list(reversed(sorted(path_test.items(), key=operator.itemgetter(1))))[0:5]

	tp_sim_score_dict[tp] = top_5
	output_text.write('\n')
	output_text.write('MOST SIMILAR RULES FOR: {}\n'.format(tp))
	output_text.write('1. {}\t\t\t{}\n'.format(top_5[0][0], top_5[0][1]))
	output_text.write('2. {}\t\t\t{}\n'.format(top_5[1][0], top_5[1][1]))
	output_text.write('3. {}\t\t\t{}\n'.format(top_5[2][0], top_5[2][1]))
	output_text.write('4. {}\t\t\t{}\n'.format(top_5[3][0], top_5[3][1]))
	output_text.write('5. {}\t\t\t{}\n'.format(top_5[4][0], top_5[4][1]))

# print('look')
print(tp_sim_score_dict)

