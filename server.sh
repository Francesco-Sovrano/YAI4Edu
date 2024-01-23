#!/bin/bash

# MY_DIR="`python3 -c "import os; print(os.path.split(os.path.realpath('$0'))[0])"`"
# cd $MY_DIR

# PyClean
(find ./ -name __pycache__ -type d | xargs rm -r) && (find ./ -name *.pyc -type f | xargs rm -r)

cd yai4edu_interface
echo 'Running YAI4Edu server..'
source .env/bin/activate

python3 server.py 8015 &> _yai4edu.log &
disown

deactivate
cd ..

cd user_study_interface
echo 'Running EVAL server..'
source .env/bin/activate

python3 server.py 8017 &> _eval.log &
disown

deactivate
cd ..

# Run OKE Server
cd library_server
echo 'Running OKE server..'
source .env/bin/activate

python3 server.py 8019 clause_amr_edu fb &> out.log &
disown
python3 server_bva.py 8021 amr_edu fb &> out_bva.log &
disown

deactivate
cd ..
