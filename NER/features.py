from liblinearutil import *
from collections import namedtuple


Row = namedtuple('Row', 'label pos word'.split())

# label ids
labels = ['O','B-PER', 'I-PER', 'B-LOC', 'I-LOC', 'B-ORG', 'I-ORG', 'PHIPOS', 'OMEGAPOS', 'UNKPOS']
label_dict = dict(zip(labels, list(range(len(labels)))))

f = open('train.txt')

line_array = [Row(*line.split()) for line in f if line.split()]

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
	word_list = list(unique_words) + pseudo_words
	word_feature_ids = list(range(len(word_list)))

	model_word = open('model.word', 'w')
	model_word.write()

#increments dict values starting from starting value
def incDictValues(d, starting_value):
	for k, v in d.items():
		v += starting_value
