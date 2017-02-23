from collections import namedtuple, Counter

EXCLUDE = 'is are be was were said have has had and or >comma >squote >rparen >lparen >period >minus >ampersand'.split()

Triple = namedtuple('Triple', ['X', 'path', 'Y'])
TDB = []

test_text = open('corpus.txt')

paths = []
current_path = ''
current_x = None
in_path_tag = False
for line in test_text:
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

C = Counter(TDB) #giving me distinct triples, not distinct paths
print('check')
