import spacy
print('loading english to spaCy')
nlp = spacy.load('en')

def read_corpus(file_name):
	print('reading')
	raw_doc = ''
	for line in open(file_name):
		sp = line.split()
		raw_doc += ' '.join(wrd.strip() for wrd in sp if wrd != '\n')
		raw_doc += ' '
	return nlp(raw_doc)

def sent_to_doc(sent):
	raw = ''
	for token in sent:
		raw += token.orth_ + ' '
	return nlp(raw)

def parse_sent(sent):
	s_doc = sent_to_doc(sent)
	for i, token in sent:
		# if the index is a noun chunk, ignore, we will just insert all words between them? keep an origi
		pass


def get_sentences(docu):
	print('getting sentences')
	sents = []
	for span in docu.sents:
		sents.append([doc[i] for i in range(span.start, span.end)])
	return sents

if __name__ == '__main__':
	file_name = 'combo.txt'
	print('formatting corpus: {}'.format(file_name))
	doc = read_corpus(file_name)
	snts = get_sentences(doc)
	print('check ehre')
