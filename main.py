from pathlib import Path
import kagglehub, os, pandas as pd

path = Path(kagglehub.dataset_download("davidcariboo/player-scores")) #Path to dataset as Path type
files = os.listdir(path)
# print(files)
# file = input("Select the file you would like to work with - numbers 0 through " + str(len(files)-1) + ": ")

players = pd.read_csv(path/"players.csv") 

def Tests(data):
    data.head()
    data.shape
    data.columns
    data.dtypes
    data.info()
    #Basic info on the db we work with
#Tests(players)

