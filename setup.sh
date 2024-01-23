#!/bin/bash

MY_DIR="`python3 -c "import os; print(os.path.realpath('$1'))"`"
cd $MY_DIR

# Configure EVAL server
cd user_study_interface
echo 'Setting up EVAL server..'
virtualenv .env -p python3.7
source .env/bin/activate
pip install -U pip
pip install -U setuptools wheel twine
pip install  --use-deprecated=legacy-resolver -r requirements.txt
cd ..

# Configure YAI server
cd yai4edu_interface
echo 'Setting up EVAL server..'
virtualenv .env -p python3.7
source .env/bin/activate
pip install -U pip
pip install -U setuptools wheel twine
pip install  --use-deprecated=legacy-resolver -r requirements.txt
cd ..

# Configure OKE server
cd library_server
echo 'Setting up OKE server..'
virtualenv .env -p python3.7
source .env/bin/activate
pip install -U pip
pip install -U setuptools wheel twine
echo 'Install QuAnsX'
pip install  --use-deprecated=legacy-resolver -e ./packages/quansx
echo 'Install KnowPy'
pip install  --use-deprecated=legacy-resolver -e ./packages/knowpy/package
# cd .env/lib
# git clone https://github.com/huggingface/neuralcoref.git
# cd neuralcoref
# pip install  --use-deprecated=legacy-resolver -r requirements.txt
# pip install  --use-deprecated=legacy-resolver -e .
# cd ..
# cd ../..
pip install  --use-deprecated=legacy-resolver -r requirements.txt
python3 -m spacy download en_core_web_trf
python3 -m spacy download en_core_web_md
python3 -m spacy download en_core_web_sm
python3 -m nltk.downloader stopwords punkt averaged_perceptron_tagger framenet_v17 wordnet brown omw-1.4
cd ..
