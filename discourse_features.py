import spacy
nlp = spacy.load('en')

doc = nlp('A large tornado damaged 12 homes in Alabama yesterday. Several people were also hurt by the massive tornado. The injured people were taken to the hospital. The tornado hit central Huntsville near the hospital. Huntsville did not get enough early warning of the tornado to flee.')
print('check')