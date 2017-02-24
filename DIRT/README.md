
//Instructions 

// install corenlp python wrapper in virtual environment
python3 -m virtualenv ve
source ve/bin/activate.csh
pip install pycorenlp

// starts server
java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer

