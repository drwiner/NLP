from collections import namedtuple

EXCLUDE = 'is are be was were said have has had and or >comma >squote >rparen >lparen >period >minus >ampersand'.split()

Triple = namedtuple('Triple', ['X', 'path', 'Y'])
TDB = set()

test_text = open('corpus.txt')

paths = []
current_path = ''
current_x = None
in_path_tag = False
for line in test_text:
	line_split = line.split()
	t = line_split[0]
	lang = [s.lower() for s in line_split[2:]]
	if lang == '<eos':
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
				TDB.add(Triple(current_x, current_path, y))

			# flush path
			current_path = ''
		current_x = y
		continue

	elif t != 'NP' and in_path_tag:
		path_str = ' '.join(lang)
		current_path += path_str + ' '


print('check')

		# if in_path_tag is False and we spot a noun phraise, make True
		# if in_path_tag is True and we spot a noun phrase, then add triple + current_path to paths unless empty
		# if in_path_tag is False and we don't spot a noun phrase, move along
		# if in_path_tag is True and we don't spot a noun phrase, add lang to path, exclude all words in EXCLUDE

# extract sentences
# lowercase all words
# dependency path
# create triples