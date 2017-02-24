from collections import namedtuple, Counter, defaultdict
from math import log2, sqrt
from clockdeco import clock
from itertools import product as iterprod

EXCLUDE = 'is are be was were said have has had and or >comma >squote >rparen >lparen >period >minus >ampersand'.split()

Triple = namedtuple('Triple', ['X', 'path', 'Y'])
TDB = []

def cleanLine(line):
	return ' '.join(line.split()) + ' '

corpus_text = open('corpus.txt')

paths = []
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
				TDB.append(Triple(current_x, current_path, y))

			# flush path
			current_path = ''
		current_x = y
		continue

	elif t != 'NP' and in_path_tag:
		path_str = ' '.join(lang)
		current_path += path_str + ' '

C = Counter([trip.path for trip in TDB])		
path_instances_after_minfreq = set([k for k,v in C.items() if v > 1])
#C = Counter(TDB) #giving me distinct triples, not distinct paths
print('check')
triple_instances = TDB
unique_triples = set(TDB)
unique_paths = path_instances_after_minfreq

# all words per slot
all_words = dict()
all_words['X'] = set(trip.X for trip in unique_triples)
all_words['Y'] = set(trip.Y for trip in unique_triples)

# Entry = namedtuple('Entry', ['word', 'count'=0, 'mi'])
class Entry:
	def __init__(self, path=None, slot=None, word=None):
		self.path = path
		self.slot = slot
		self.word = word
		self.count = 0
		self.mi = None
	def update(self, path, slot, word):
		if self.word is None:
			self.word = word
		if self.slot is None:
			self.slot = slot
		if self.path is None:
			self.path = path
		self.count += 1


def getWordFillers(path, slot_pos):
	return set(trip._asdict()[slot_pos] for trip in triple_instances if trip.path == path)

triple_database = defaultdict(dict)
for path in unique_paths:
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

print('scoring word freqs')
word_freq_x, word_freq_y, word_freq = dict(), dict(), dict()
for word in all_words['X']:
	word_freq_x[word] = sum(1 for trip in triple_instances if trip.X == word)
for word in all_words['Y']:
	word_freq_y[word] = sum(1 for trip in triple_instances if trip.Y == word)
word_freq['X'] = word_freq_x
word_freq['Y'] = word_freq_y

# @clock
def MI(path, slot_pos, word):

	wf = word_freq[slot_pos]
	pdb = triple_database[path][slot_pos]

	psw = pdb[word].count
	if psw == 0:
		return 0

	_s_ = len(all_words[slot_pos])
	if _s_ == 0:
		return 0

	ps_ = len(pdb.keys())
	if ps_ == 0:
		return 0

	_sw = wf[word]
	if _sw == 0:
		return 0

	return log2((psw * _s_) / (ps_ * _sw))

print('scoring MI')

for path in triple_database.keys():
	print(path)
	tdpx = triple_database[path]['X']
	tdpy = triple_database[path]['Y']

	for word, entry in tdpx.items():
		entry.mi = MI(entry.path, entry.slot, entry.word)
	for word, entry in tdpy.items():
		entry.mi = MI(entry.path, entry.slot, entry.word)

print('check here')

# @clock
def pathSim(p1, p2):
	slot_x_sim = slotSim(p1, p2, 'X')
	print('slot-x sim : ' + str(slot_x_sim))
	slot_y_sim = slotSim(p1,p2,'Y')
	print('slot-y-sim : ' + str(slot_y_sim))
	print('pathsim: ' + str(slot_x_sim * slot_y_sim))
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


test_text = open('test.txt')
test_paths = [cleanLine(line) for line in test_text]
import operator
tp_sim_score_dict = dict()
for tp in test_paths:
	print(tp)
	path_test = dict()
	for p in unique_paths:
		print('comparing test-path ' + tp + ' to path: ' + p)
		ps = pathSim(tp,p)
		print(ps)
		path_test[p] = ps
	# now, get the top 5:
	top_5 = list(reversed(sorted(path_test.items(), key=operator.itemgetter(1))))[0:5]
	tp_sim_score_dict[tp] = top_5

print('look')
print(tp_sim_score_dict)