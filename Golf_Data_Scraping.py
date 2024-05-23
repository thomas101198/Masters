import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from pandas.io import sql
import mysql.connector

mydb = mysql.connector.connect(
  host = "sql8.freesqldatabase.com",
  user = "sql8705870",
  password = "dHBiujZhFa",
  database = "sql8705870"
)

mycursor = mydb.cursor()
driver = webdriver.Chrome()

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








