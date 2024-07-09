import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium import webdriver
from pandas.io import sql
import mysql.connector
from numpy import NaN
import requests
import datetime

mydb = mysql.connector.connect(
  host = "sql8.freesqldatabase.com",
  user = "sql8718181",
  password = "xyvp7AygTF",
  database = "sql8718181"
)

mycursor = mydb.cursor()
driver = webdriver.Chrome()

X_API_KEY = "da2-gsrx5bibzbb4njvhl7t37wqyl4"

YEAR = 20230
PAST_RESULTS_ID = "R2014014"

# prepare the payload
payload = {
    "operationName": "TournamentPastResults",
    "variables": {
        "tournamentPastResultsId": PAST_RESULTS_ID,
        "year": YEAR
    },
    "query": "query TournamentPastResults($tournamentPastResultsId: ID!, $year: Int) {\n  tournamentPastResults(id: $tournamentPastResultsId, year: $year) {\n    id\n    players {\n      id\n      position\n      player {\n        id\n        firstName\n        lastName\n        shortName\n        displayName\n        abbreviations\n        abbreviationsAccessibilityText\n        amateur\n        country\n        countryFlag\n        lineColor\n      }\n      rounds {\n        score\n        parRelativeScore\n      }\n      additionalData\n      total\n      parRelativeScore\n    }\n    rounds\n    additionalDataHeaders\n    availableSeasons {\n      year\n      displaySeason\n    }\n    winner {\n      id\n      firstName\n      lastName\n      totalStrokes\n      totalScore\n      countryFlag\n      countryName\n      purse\n      points\n    }\n  }\n}"
}

# post the request
page = requests.post("https://orchestrator.pgatour.com/graphql", json=payload, headers={"x-api-key": X_API_KEY})

# check for status code
page.raise_for_status()

# get the data
data = page.json()["data"]["tournamentPastResults"]["players"]


payload1 = {"operationName":"Player",
            "variables":{
            "playerId":"46970"},
            "query":"query Player($playerId: ID!) {\n  player(id: $playerId) {\n    bioLink\n    countryFlag\n    country\n    displayName\n    firstName\n    id\n    lastName\n    playerBio {\n      deceased\n      deceasedDate\n      age\n      birthplace {\n        countryCode\n        country\n        city\n        state\n        stateCode\n      }\n      born\n      bornAccessibilityText\n      degree\n      careerEarnings\n      family\n      graduationYear\n      heightImperial\n      heightImperialAccessibilityText\n      heightMeters\n      overview\n      personal\n      playsFrom {\n        city\n        country\n        countryCode\n        state\n        stateCode\n      }\n      pronunciation\n      residence {\n        city\n        country\n        state\n        countryCode\n        stateCode\n      }\n      school\n      social {\n        type\n        url\n      }\n      turnedPro\n      weightImperial\n      weightKilograms\n      websiteURL\n      exemptions {\n        tour\n        description\n        expirationDate\n      }\n    }\n    rank {\n      rank\n      statName\n    }\n    owgr\n  }\n}"}
# post the request
page1 = requests.post("https://orchestrator.pgatour.com/graphql", json=payload1, headers={"x-api-key": X_API_KEY})

# check for status code
page1.raise_for_status()

# get the data
data1 = page1.json()["data"]["player"]["playerBio"]

birthplace = data1["birthplace"]["countryCode"]
height = data1["heightMeters"]
dob = datetime.datetime.strptime(data1["born"],'%b %d, %Y').strftime('%Y-%m-%d')

print(birthplace, height,dob)
quit()
def load_data(URL):
  driver.implicitly_wait(10)
  driver.get(URL)
  dob = driver.find_element(By.ID,"tabs-:rf:--tabpanel-6")
  print(dob)

for i in data:
  c = i["player"]["displayName"].split(" ", 1)[0]
  b = i["player"]["displayName"].split(" ", 1)[1]
  a = i["player"]["id"]
  url = f"https://www.pgatour.com/player/{a}/{b}-{c}/bio" 
  load_data(url)
  print(i["player"]["displayName"])
  print(i["player"]["country"])


def load_data(URL,y):
  driver.get(URL)
  table = driver.find_element(By.CSS_SELECTOR, "table.chakra-table")
  assert table, "table not found"
  df = pd.read_html(driver.find_element(By.CSS_SELECTOR, "table.chakra-table").get_attribute('outerHTML'))[0]
  df = df.drop(df.columns[12:], axis=1)
  df2 = df.loc[:,"Unnamed: 2_level_0"]
  upload_data(df2,y)

def upload_data(players,b):
  existing_players = []
  mycursor.execute('SELECT CONCAT(first_name," ",last_name) FROM Masters_Players') 
  captured_players = mycursor.fetchall() 
  for x in captured_players:
    existing_players.append(x[0])
  
  y = 0

  for i in players['Player']:
    if type(i) == str:
      if len(i.split()) <= 4:
        i = i.replace("(a)","")
        if i not in existing_players:
          try:

            param1 =  i.split(" ", 1)[0]
            param2 = i.split(" ", 1)[1]

            cursor = mydb.cursor()
            cursor.execute("""INSERT INTO Masters_Players (first_name,last_name) VALUES (%s,%s)""", (param1, param2))
            mydb.commit()
            print(cursor.rowcount, "Record inserted successfully into Laptop table")
            cursor.close()
            y += 1
          except mysql.connector.Error as error:
            print("Failed to insert record into Laptop table {}".format(error))
  print("Total players added:",y,"Year:",b)

#These are the two variables we neeed to change
start_year = (2014)
end_year = (2024)

url = ""

for a in range(start_year,end_year+1):
  url = f"https://www.pgatour.com/tournaments/2022/masters-tournament/R{a}014/leaderboard" 
  load_data(url,a)






# We needed to remove NaN values, where adverts or gaps appear in the tables. Then remove any 'names' larger than 4 words long as we were capturing a message about the cut. 
# Finally we want to remove the marker for amateur from the surname








