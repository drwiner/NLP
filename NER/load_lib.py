from liblinearutil import *



f = open('train.txt')

class wordRow:
	def __init__(self, row_list):
		if len(row_list) == 3:
			self.label = row_list[0]
			self.pos = row_list[1]
			self.word = row_list[2]
		else:
			print('row_list too small', row_list)

	def __repr__(self):
		return str(self.label + ' ' + self.pos + ' ' + self.word)
	#	return str(self.label), str(self.pos), str(self.word)


line_array = [wordRow(line.split()) for line in f if line.split()]

unique_words = {line.word for line in line_array}

print('ok')