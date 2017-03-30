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

def noun_chunk_index_list(nchunks):
	indices = []
	index_chunk_dict = dict()
	for nchunk in nchunks:
		indices.extend(range(nchunk.start, nchunk.end))
		index_chunk_dict[nchunk.end] = nchunk #.root
	return indices, index_chunk_dict

symb_dict = dict()
symb_dict['\"'] = '>SQUOTE'
symb_dict['\''] = '>SQUOTE'
symb_dict['&'] = '>AMPERSAND'
symb_dict[','] = '>COMMA'
symb_dict['('] = '>LPAREN'
symb_dict[')'] = '>RPAREN'
symb_dict['-'] = '>MINUS'
symb_dict['--'] = '>MINUS'
symb_dict['.'] = '>PERIOD'


def parse_sent(sent):
	parse_list = []
	s_doc = sent_to_doc(sent)
	nchunks = list(s_doc.noun_chunks)
	nchunk_indices, nchunk_dict = noun_chunk_index_list(nchunks)
	for i, token in enumerate(sent):
		# if the index is a noun chunk, ignore, we will just insert all words between them? keep an origi
		if i in nchunk_indices:
			if i in nchunk_dict.keys():
				parse_list.append(nchunk_dict[i])
		else:
			if token.orth_ in symb_dict.keys():
				parse_list.append(symb_dict[token.orth_])
			else:
				parse_list.append(token)
	parse_list.append('<EOS')
	return parse_list


def parse_to_output(sents, file_name):
	# open the file name
	with open(file_name, 'w') as fn:
		for snt in sents:
			for elm in parse_sent(snt):
				if type(elm) is spacy.tokens.span.Span:
					fn.write('{} : {}'.format('NP', elm.orth_))
				elif type(elm) is str:
					fn.write('WORD : {}'.format(elm))
				else:
					fn.write('{} : {}'.format(elm.pos_, elm.orth_))
				fn.write('\n')


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
	output_name = 'movie_corpus.txt'
	parse_to_output(snts, output_name)
