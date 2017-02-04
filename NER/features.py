
class Row:

	def __init__(self, label, pos, word, prev_pos, prev_word):
		self.label = label
		self.pos = pos
		self.word = word
		self.prev_pos = prev_pos
		self.prev_word = prev_word

	def next(self, next_pos, next_word):
		self.next_pos = next_pos
		self.next_word = next_word


# label ids
labels = ['O','B-PER', 'I-PER', 'B-LOC', 'I-LOC', 'B-ORG', 'I-ORG']
label_dict = dict(zip(labels, list(range(1, len(labels) + 1))))

#remove these after testing
train_text = open('train.txt')
test_text  = open('test.txt')

###################### Train ###########################
line_array = []
new_sentence = True
beg = True

for line in train_text:
	row = line.split()
	if row:

		if new_sentence:
			#then new sentence
			new_sentence = False
			prev_pos, prev_wrd = 'OMEGAPOS', 'OMEGA'
			if not beg:
				#update end of last sentence
				line_array[-1].next('OMEGAPOS', 'OMEGA')

			else:
				beg = False

		else:
			#middle/last of sentence, update end of last
			line_array[-1].next(row[1], row[2])
			prev_pos, prev_wrd = line_array[-1].pos, line_array[-1].word

		line_array.append(Row(label=row[0], pos=row[1], word=row[2], prev_pos=prev_pos, prev_word=prev_wrd))
	else:
		#last is end of sentence, there is no row here
		new_sentence = True

line_array[-1].next('OMEGAPOS', 'OMEGA')

prev_pos_set = {row.prev_pos for row in line_array}.union('UNKPOS', 'OMEGAPOS', 'PHIPOS')
next_pos_set = {row.next_pos for row in line_array}.union('UNKPOS', 'OMEGAPOS', 'PHIPOS')
prev_word_set = {row.prev_word for row in line_array}.union('UNKWORD', 'OMEGA', 'PHI')
next_word_set = {row.next_word for row in line_array}.union('UNKWORD', 'OMEGA', 'PHI')
train_words = {line.word for line in line_array}
train_pos = {line.pos for line in line_array}

###################### Test ###########################

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
			#then new sentence
			new_sentence = False
			prev_pos, prev_wrd = 'OMEGAPOS', 'OMEGA'
			if not beg:
				#update end of last sentence
				line_array_test[-1].next('OMEGAPOS', 'OMEGA')

			else:
				beg = False

		else:
			#middle/last of sentence

			# update last's next_pos, next_word
			r_pos, r_word = row[1], row[2]
			if r_pos not in next_pos_set:
				r_pos = 'UNKPOS'
			if r_word not in next_word_set:
				r_word = 'UNKWORD'
			line_array_test[-1].next(r_pos, r_word)

			# update last's prev_pos, prev_word
			prev_pos, prev_wrd = line_array_test[-1].pos, line_array_test[-1].word
			if prev_pos not in prev_pos_set:
				prev_pos = 'UNKPOS'
			if prev_wrd not in prev_word_set:
				prev_wrd = 'UNKWORD'

		line_array_test.append(Row(label=row[0], pos=row[1], word=row[2], prev_pos=prev_pos, prev_word=prev_wrd))

	else:
		# last is end of sentence, there is no row here
		new_sentence = True
line_array_test[-1].next('OMEGAPOS', 'OMEGA')

######################## IDs ################################
# word ids
index = len(train_words)+1
word_dict = dict(zip(train_words, list(range(1, index))))
word_dict.update({'UNKWORD': index})

# cap id
binary_cap_id = max(word_dict.values()) + 1
last = binary_cap_id + 1

def makeIDs(items, last, unkpos=False, unkword=False):
	start = last
	end = len(items) + start + 1
	idd = dict(zip(items, list(range(start, end))))
	if unkpos:
		idd.update({'UNKPOS': end}); end += 1
	if unkword:
		idd.update({'UNKWORD': end}); end += 1

	return idd, end

pseudo_pos = {'OMEGAPOS', 'PHIPOS', 'UNKPOS'}
# prev_pos ids
prev_pos_dict, last = makeIDs({row.prev_pos for row in line_array}.union(pseudo_pos), last, unkpos=True)
#prev_pos_test_dict, last = makeIDs({row.prev_pos for row in line_array_test}.union(pseudo_pos), last, unkpos=True)
# next_pos ids
next_pos_dict, last = makeIDs({row.next_pos for row in line_array}.union(pseudo_pos), last, unkpos=True)
#next_pos_test_dict, last = makeIDs({row.next_pos for row in line_array_test}.union(pseudo_pos), last, unkpos=True)

pseudo_words = {'OMEGA', 'PHI', 'UNKWORD'}
# prev_word ids
prev_word_dict, last = makeIDs({row.word for row in line_array}.union(pseudo_words), last, unkword=True)
# next_word ids
next_word_dict, last = makeIDs({row.next_word for row in line_array}.union(pseudo_words), last, unkword=True)


def toFeat(row, feat_type):

	feats = []
	feats.append(word_dict[row.word])
	if feat_type is not 'word':
		if row.word.istitle():
			feats.append(binary_cap_id)

		if feat_type is 'poscon' or feat_type is 'bothcon':

			feats.append(prev_pos_dict[row.prev_pos])
			feats.append(next_pos_dict[row.next_pos])

		if feat_type is 'lexcon' or feat_type is 'bothcon':

			feats.append(prev_word_dict[row.prev_word])
			feats.append(next_word_dict[row.next_word])

	feature_str = str(label_dict[row.label]) + ' '
	for f in feats:
		feature_str += str(f) + ':1 '

	return feature_str + '\n'

# debug message
print('Found {} training instances with {} distinct words and {} distinct POS tags'.format(len(line_array), len(train_words), len(train_pos)))
print('Found {} test instances'.format(len(line_array_test)))

def generateFeatures(ftype):
	print(ftype)
	train = open('train.' + str(ftype), 'w')
	test = open('test.' + str(ftype), 'w')

	for line in line_array:
		train.write(toFeat(line, ftype))
	train.close()

	for line in line_array_test:
		test.write(toFeat(line, ftype))
	test.close()

generateFeatures('word')
generateFeatures('wordcap')
generateFeatures('poscon')
generateFeatures('lexcon')
generateFeatures('bothcon')