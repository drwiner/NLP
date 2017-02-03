from liblinearutil import *
import sys

if len(sys.argv) != 3:
	print('missing arg')
else:
	train_text = sys.argv[0]
	test_text = sys.argv[1]
	classifier_type = sys.argv[2]
