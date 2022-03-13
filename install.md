# Installation

## Requirements

Python 3.9
didkit 0.3.0


## Install

mkdir gaiax  
cd gaiax  
python3 -m venv venv  
. venv/bin/activate  

pip install redis  
pip install Flask-Session  
pip install Flask[async]  
pip install didkit==0.3.0  
pip install Flask-QRcode  
pip install jwcrypto  
pip install pyjwt  
pip install gunicorn  

git clone https://github.com/TalaoDAO/gaiax.git  

## Run

python main.py
