import spacy
print('loading english to spaCy')
nlp = spacy.load('en')
print('complete')

def noun_with_clause(clause):
	return nlp('he' + clause)

def is_capitalized(token):
	return token.orth_[0].isupper()

if __name__ == '__main__':
	with open('scene_sents.txt') as sst:
		for line in sst:
			# shot_text = line.split()[1]
			shot_text = ' '.join(line.split()[1:-1])
			clauses = shot_text.split(',')
			cs = [nlp(clauses[0])]
			if len(clauses) > 1:
				for c in clauses[1:]:
					cs.append(noun_with_clause(c))
			# now what? return here for scoring?