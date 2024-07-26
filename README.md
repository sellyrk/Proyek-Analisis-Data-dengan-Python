# Mobike Rental Cycles
## Setup Environment - Anaconda
```
conda create --name main-ds python=3.11.4
conda activate main-ds
pip install matplotlib numpy pandas requests seaborn streamlit
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal
```
mkdir proyek_analisis_data_EDA
cd proyek_analisis_data_EDA
pipenv install
pipenv shell
pip install -r requirements.txt
```

## Run steamlit app
```
streamlit run dashboard.py