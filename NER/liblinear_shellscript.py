#batch script for liblinear
import subprocess
import shlex

ftypes = ['word', 'wordcap', 'poscon', 'lexcon', 'bothcon']

def train():
	print('training')
	for ft in ftypes:
		print(ft)
		train_features = 'train.' + ft
		model = 'model.' + ft
		command = './train.exe -s 0' + train_features + ' ' + model
		subprocess.call(shlex.split(command))

def predict():
	print('predicting')

	for ft in ftypes:
		print(ft)
		test_features = 'test.' + ft
		model = 'model.' + ft
		predict = 'predict.' + ft
		acc = 'accuracy.txt'
		command = './predict.exe -s 0' + test_features + ' ' + model + ' ' + predict + ' > ' +  acc
		subprocess.call(shlex.split(command))