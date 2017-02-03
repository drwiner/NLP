from collections import namedtuple

#Row = namedtuple('Row', 'label pos word'.split())

class Row:

	def __init__(self, label, pos, word, prev_pos, prev_word):
		self.label = label
		self.pos = pos
		self.word = word
		self.prev_pos = prev_pos
		self.prev_word = prev_word
		# self.next_pos = None
		# self.next_word = None

	def next(self, next_pos, next_word):
		self.next_pos = next_pos
		self.next_word = next_word

# label ids
labels = ['O','B-PER', 'I-PER', 'B-LOC', 'I-LOC', 'B-ORG', 'I-ORG']
label_dict = dict(zip(labels, list(range(1, len(labels) + 1))))

#remove these after testing
train_text = open('train.txt')
test_text  = open('test.txt')

line_array = []
new_sentence = True
beg = True

for line in train_text:
	row = line.split()
	if row:

		if new_sentence:
			#then new sentence, don't update last
			new_sentence = False
			if not beg:
				beg = False
				line_array[-1].next('OMEGAPOS', 'OMEGA')
			n_pos, n_wrd = ('PHIPOS', 'PHI')

		else:
			#middle sentence
			line_array[-1].next(row[1], row[2])
			n_pos, n_wrd = (line_array[-1].pos, line_array[-1].word)

		line_array.append(Row(row[0], row[1], row[2], n_pos, n_wrd))

	else:
		#last is end of sentence, there is no row here
		new_sentence = True

train_words = {line.word for line in line_array}
train_pos = {line.pos for line in line_array}
line_array_test = []
new_sentence = True
beg = True

for line in test_text:
	row = line.split()
	if row:
		if row[1] not in train_pos:
			row[1] = 'UNKPOS'
		if row[2] not in train_words:
			row[2] = 'UNKWORD'

		if new_sentence:
			# then new sentence, don't update last
			new_sentence = False
			if not beg:
				beg = False
				line_array_test[-1].next('OMEGAPOS', 'OMEGA')
			n_pos, n_wrd = ('PHIPOS', 'PHI')

		else:
			# middle sentence
			line_array_test[-1].next(row[1], row[2])
			n_pos, n_wrd = (line_array_test[-1].pos, line_array_test[-1].word)

		line_array_test.append(Row(row[0], row[1], row[2], n_pos, n_wrd))

	else:
		# last is end of sentence, there is no row here
		new_sentence = True

#line_array = [Row(*line.split()) for line in train_text if line.split()]
#line_array_test = [Row(*line.split()) for line in test_text if line.split()]

# word ids
#train_words = {line.word for line in line_array}
index = len(train_words)+1
word_dict = dict(zip(train_words, list(range(1, index))))
word_dict.update({'UNKWORD': index})
#test_words = {line.word for line in line_array_test} - train_words
#word_dict.update(dict(zip(test_words, list(range(index, index + len(test_words))))))

# cap id
binary_cap_id = max(word_dict.values()) + 1
last = binary_cap_id

def makeIDs(items, last):
	start = last + 1
	end = len(items) + start + 1
	return dict(zip(items, list(range(start, end)))), end

# prev_word ids
prev_word_dict, last = makeIDs({row.prev_word for row in line_array}, last)

# next_word ids
next_word_dict, last = makeIDs({row.next_word for row in line_array}, last)

# prev_pos ids
prev_pos_dict, last = makeIDs({row.prev_pos for row in line_array}, last)

# next_pos ids
next_pos_dict, last = makeIDs({row.next_pos for row in line_array}, last)


# pos ids
#train_pos = {line.pos for line in line_array}
start = binary_cap_id + 1
end = len(train_pos) + start + 1
pos_dict = dict(zip(train_pos, list(range(start, end))))
#test_pos = {line.pos for line in line_array} - train_pos
#pos_dict.update(dict(zip(test_pos, list(range(index, index + len(test_pos))))))


# debug message
print('Found {} training instances with {} distinct words and {} distinct POS tags'.format(len(line_array), len(train_words), len(train_pos)))
print('Found {} test instances'.format(len(line_array_test)))


def wordFeatures():

	train_word = open('train.word', 'w')
	test_word = open('test.word', 'w')

	encountered = set()
	for line in line_array:
		if line.word not in encountered:
			train_word.write(str(label_dict[line.label]) + ' ' + str(word_dict[line.word]) + ':1\n')
		else:
			encountered.add(line.word)

	train_word.close()

	encountered = set()
	for line in line_array_test:
		if line.word not in encountered:
			test_word.write(str(label_dict[line.label]) + ' ' + str(word_dict[line.word]) + ':1\n')
		else:
			encountered.add(line.word)

	test_word.close()

def wordcapFeatures():
	train_wordcap = open('train.wordcap', 'w')
	test_wordcap = open('test.wordcap', 'w')

	# wordcap ids
	binary_cap_id = max(word_dict.values()) + 1

	encountered = set()
	for line in line_array:
		if line.word not in encountered:
			if line.word.istitle():
				train_wordcap.write(str(label_dict[line.label]) + ' ' + str(word_dict[line.word]) + ':1' + ' ' + str(binary_cap_id) + ':1\n')
			else:
				train_wordcap.write(str(label_dict[line.label]) + ' ' + str(word_dict[line.word]) + ':1\n')
		else:
			encountered.add(line.word)

	train_wordcap.close()

	encountered = set()
	for line in line_array_test:
		if line.word not in encountered:
			if line.word.istitle():
				test_wordcap.write(str(label_dict[line.label]) + ' ' + str(word_dict[line.word]) + ':1' + ' ' + str(binary_cap_id) + ':1\n')
			else:
				test_wordcap.write(str(label_dict[line.label]) + ' ' + str(word_dict[line.word]) + ':1\n')
		else:
			encountered.add(line.word)

	test_wordcap.close()

def posconFeatures():
	train_poscon = open('train.poscon', 'w')
	test_poscon = open('test.poscon', 'w')

	# wordcap ids
	binary_cap_id = max(word_dict.values()) + 1
	#cap_dict = dict(zip(word_dict.keys(), list(range(index, index + len(word_dict)))))

	# pseudo ids
	pseduo_labels = ['PHIPOS', 'OMEGAPOS', 'UNKPOS', 'prev-PHIPOS', 'prev-OMEGAPOS', 'prev-UNKPOS', 'next-PHIPOS', 'next-OMEGAPOS', 'next-UNKPOS']
	pseudo_words = ['PHI', 'OMEGA', 'UNKWORD', 'prev-PHI', 'prev-OMEGA', 'prev-UNKWORD', 'next-PHI', 'next-OMEGA', 'next-UNKWORD']

	pseudo_dict = dict(zip(pseudo_words, list(range(1, len(pseudo_words) + 1))))
	# poscon ids


#increments dict values starting from starting value
def incDictValues(d, starting_value):
	for k, v in d.items():
		v += starting_value


#wordFeatures()
wordcapFeatures()