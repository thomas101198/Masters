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
#goes back to 2014. Need to wrap the url in an if statement and then change the insert part into a function
URL = "https://www.pgatour.com/tournaments/2022/masters-tournament/R2018014/leaderboard"

driver = webdriver.Chrome()

# load page
driver.get(URL)

# get table
table = driver.find_element(By.CSS_SELECTOR, "table.chakra-table")
assert table, "table not found"

df = pd.read_html(driver.find_element(By.CSS_SELECTOR, "table.chakra-table").get_attribute('outerHTML'))[0]

df = df.drop(df.columns[12:], axis=1)

""" for col in df.columns:
    print(col) """

df2 = df.loc[:,"Unnamed: 2_level_0"]


# We needed to remove NaN values, where adverts or gaps appear in the tables. Then remove any 'names' larger than 4 words long as we were capturing a message about the cut. 
# Finally we want to remove the marker for amateur from the surname
existing_players = []
mycursor.execute('SELECT CONCAT(first_name," ",last_name) FROM Masters_Players') 
captured_players = mycursor.fetchall() 
for x in captured_players:
  existing_players.append(x[0])

# Need to fix the below as 'O'Meara' didnt insert due to escaped character
y = 0

for i in df2['Player']:
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

print("Total entries added:",y)
# The names are then useed to populate the player first name and last name column in the Masters_Players table. We can get the rest of the player info later

# df.to_sql(con=con, name='table_name_for_df', if_exists='replace', flavor='mysql')




