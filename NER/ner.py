#!/usr/bin/env python3

import sys
from features import process

for arg in sys.argv:
	print(arg, end=' ')
print('\n')

if len(sys.argv) != 4:
	print('not enough args')
else:
	print(type(sys.argv[3]), sys.argv[3])
	if str(sys.argv[3]) == 'all':
		print('all selected')
		#all = ['word', 'wordcap', 'poscon', 'lexcon', 'bothcon']
		process(sys.argv[1], sys.argv[2], ['word', 'wordcap', 'poscon', 'lexcon', 'bothcon'])
	else:
		print('processing ftype ' + str(sys.argv[3]))
		process(sys.argv[1], sys.argv[2], [sys.argv[3]])