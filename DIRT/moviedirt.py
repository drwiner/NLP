# the DIRT algorithm (Lin and Pantel, 2001, ACM)
# Written by DAVID WINER
# Do not take without permission - drwiner@cs.utah.edu

from collections import namedtuple, Counter, defaultdict
from math import log2, sqrt

EXCLUDE = 'is are be was were said have has had and or >comma >squote >rparen >lparen >period >minus >ampersand'.split()

Triple = namedtuple('Triple', ['X', 'path', 'Y'])

# TStream (triple stream) - collects all triple instances
TStream = []

# distinct_filtered_Tinstances - distinct triples after minfreq
distinct_filtered_Tinstances = set()

# filtered Tinstances
filtered_Tinstances = list()

# distinct_filtered_Pinstances - the set of paths after minfreq
distinct_filtered_Pinstances = set()

# distinct_unfiltered_Pinstances
distinct_unfiltered_Pinstances = set()

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
		# , unfiltered_words

	PCounter = Counter([t.path for t in TStream])
	distinct_unfiltered_Pinstances = set(PCounter.keys())
	distinct_filtered_Pinstances = set(p for p in distinct_unfiltered_Pinstances if PCounter[p] >= min_freq)

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
		self.count = 1
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

def loadDatabase():

	# For each filtered triple instance:
	for x, path, y in filtered_Tinstances:
		if path is None:
			print('here')
		## Triple Database by-path (default dict, so creates dict at key [path] or reference existing)
		path_db = triple_database[path]
		if 'X' not in path_db.keys():
			path_db['X'] = dict()
		pdbx = path_db['X']

		if x in pdbx.keys():
			pdbx[x].count += 1
		else:
			pdbx[x] = Entry(path, 'X', x)

		if 'Y' not in path_db.keys():
			path_db['Y'] = dict()
		pdby = path_db['Y']

		if y in pdby.keys():
			pdby[y].count += 1
		else:
			pdby[y] = Entry(path, 'Y', y)

# @clock
def MI(path, slot_pos, word):

	pdb = triple_database[path][slot_pos]

	# |p,s,w|
	psw = pdb[word].count
	if psw == 0:
		return 0

	# |*, s, *|
	_s_ = 0
	for p in triple_database.keys():
		for w in triple_database[p][slot_pos].keys():
			_s_ += triple_database[p][slot_pos][w].count
	if _s_ == 0:
		return 0

	# |p, s, *|
	ps_ = sum(pdb[word].count for word in pdb.keys())
	if ps_ == 0:
		return 0

	# |*, s, w|
	_sw = 0
	for p in triple_database.keys():
		if word in triple_database[p][slot_pos].keys():
			_sw += triple_database[p][slot_pos][word].count
	if _sw == 0:
		return 0

	if (psw * _s_) < 0:
		return 0
	if (ps_ * _sw) < 0:
		return 0
	mi = log2((psw * _s_) / (ps_ * _sw))
	if mi < 0:
		return 0
	return mi


def updateMI():

	for path in triple_database.keys():

		tdpx = triple_database[path]['X']
		tdpy = triple_database[path]['Y']

		for entry in tdpx.values():
			entry.mi = MI(entry.path, entry.slot, entry.word)
		for entry in tdpy.values():
			entry.mi = MI(entry.path, entry.slot, entry.word)


# @clock
def pathSim(p1, p2):
	slot_x_sim = slotSim(p1, p2, 'X')
	slot_y_sim = slotSim(p1, p2, 'Y')

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

if __name__ == '__main__':
	for arg in sys.argv:
		print(arg, end=' ')
	print('\n')

	if len(sys.argv) != 4 and len(sys.argv) > 1:
		print('must have 3 args')
		raise AssertionError
	elif len(sys.argv) == 1:
		# for testing
		min_freq = 5
		corpus_text = open('corpus.txt')
		test_text = open('test.txt')
	else:
		min_freq = int(sys.argv[-1])
		corpus_text = open(str(sys.argv[1]))
		test_text = open(str(sys.argv[2]))

	#### Load TStream ####
	readCorpus(corpus_text)

	#### Apply MinFreq####
	dp, dmf, pi, pimf = apply_MinfreqFilter(min_freq)

	output_text = open('output.txt', 'w')
	output_text.write('Found {} distinct paths, {} after minfreq filtering.\n'.format(dp, dmf))
	output_text.write('Found {} path instances, {} after minfreq filtering.\n'.format(pi, pimf))

	#### Load Triple Databse (as in paper)
	loadDatabase()
	# update Mutual Information once all data is loaded
	updateMI()

	### read in comparison tests
	test_paths = [cleanLine(line) for line in test_text]
	import operator

	# tp_sim_score_dict = dict()
	for tp in test_paths:
		if tp == ' ' or tp == '\n':
			continue
		path_test = dict()
		for p in distinct_filtered_Pinstances:
			if tp not in triple_database.keys():
				continue
			ps = pathSim(tp, p)
			path_test[p] = ps

		# now, get the top 5:
		ranked_list = list(reversed(sorted(path_test.items(), key=operator.itemgetter(1))))
		# tp_sim_score_dict[tp] = top_5
		output_text.write('\n')
		output_text.write('MOST SIMILAR RULES FOR: {}\n'.format(tp))
		if tp not in triple_database.keys():
			output_text.write('This phrase is not in the triple database.\n')
		else:
			for i in range(len(ranked_list)):
				if i > 4:
					if ranked_list[i] != ranked_list[-1]:
						break
				p, score = ranked_list[i]
				if score > 0:
					output_text.write(str(i+1) + '. %s %24.12f\n' % (p, score))
				else:
					break

