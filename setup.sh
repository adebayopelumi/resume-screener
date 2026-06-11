#!/bin/bash
set -e

echo "Creating conda environment..."
conda create -n resume-screener python=3.10 -y
conda activate resume-screener

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Downloading spaCy model..."
python -m spacy download en_core_web_sm

echo "Done! Run: streamlit run app.py"
