from collections import namedtuple
from liblinearutil import train as tr
from liblinearutil import svm_read_problem
from liblinearutil import save_model

Row = namedtuple('Row', 'label pos word'.split())

# label ids
labels = ['O','B-PER', 'I-PER', 'B-LOC', 'I-LOC', 'B-ORG', 'I-ORG', 'PHIPOS', 'OMEGAPOS', 'UNKPOS']
label_dict = dict(zip(labels, list(range(len(labels)))))

#remove these after testing
train_text = open('train.txt')
test_text  = open('test.txt')

line_array = [Row(*line.split()) for line in train_text if line.split()]

# word ids
unique_words = {line.word for line in line_array}
word_dict = dict(zip(unique_words, list(range(len(unique_words)))))

# pos ids
unique_pos = {line.pos for line in line_array}
pos_dict = dict(zip(unique_pos, list(range(len(unique_pos)))))

# debug message
print('Found {} training instances with {} distinct words and {} distinct POS tags'.format(len(line_array), len(unique_words), len(unique_pos)))

#pseudo feature ids only added for certain models
pseudo_words = ['PHI', 'OMEGA', 'UNKWORD']
pseudo_dict = dict(zip(pseudo_words, list(range(len(pseudo_words)))))


def wordFeatures():
	# word_list = list(unique_words)
	# word_feature_ids = list(range(len(word_list)))

	features_word = open('features.word', 'w')

	encountered = set()
	for line in line_array:
		if line.word not in encountered:
			features_word.write(str(label_dict[line.label]) + ' ' + str(word_dict[line.word]) + ':1\n')
		else:
			encountered.add(line.word)

	features_word.close()
	p, q = svm_read_problem('features.word')
	model = tr(p,q, '-s 0')
	save_model('word_predictions.txt', model)
	print('ok')


#increments dict values starting from starting value
def incDictValues(d, starting_value):
	for k, v in d.items():
		v += starting_value

# def train(text_file, model, params):
# 	prob_y, prob_x = svm_read_problem(model)
#

wordFeatures()