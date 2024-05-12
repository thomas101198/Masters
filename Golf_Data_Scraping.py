import pandas as pd
from bs4 import BeautifulSoup
import requests

data = {
  "calories": [420, 380, 390],
  "duration": [50, 40, 45]
}

df = pd.DataFrame(data, index = ["day1", "day2", "day3"])




URL = "https://www.flashscore.co.uk/golf/pga-tour/masters-tournament-2023/" 
r = requests.get(URL) 

soup = BeautifulSoup(r.content, 'html5lib') # If this line causes an error, run 'pip install html5lib' or install html5lib 
""" print(soup.prettify()) """ 

mydivs = soup.find_all("title", {"class": "Click for player card!"}) 
print(mydivs)