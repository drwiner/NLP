#!/usr/bin/env python3

#batch script for liblinear
import subprocess

ftypes = ['word', 'wordcap', 'poscon', 'lexcon', 'bothcon']

def train():
	print('training')
	for ft in ftypes:
		print(ft)
		train_features = 'train.' + ft
		model = 'model.' + ft
		command = './train.exe -s 0 ' + train_features + ' ' + model
		print(command)
		subprocess.call(command, shell=True)

def predict():
	print('predicting')

	for ft in ftypes:
		print(ft)
		test_features = 'test.' + ft
		model = 'model.' + ft
		predict = 'predict.' + ft
		acc = 'accuracy_' + ft + '.txt'
		command = './predict.exe ' + test_features + ' ' + model + ' ' + predict + ' > ' + acc
		print(command)
		subprocess.call(command, shell=True)

train()
predict()