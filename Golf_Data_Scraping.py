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

mycursor.execute('SELECT CONCAT(first_name," ",last_name) FROM Masters_Players') 
captured_players = mycursor.fetchall() 

# Need to fix the below as 'O'Meara' didnt insert due to escaped character


for i in df2['Player']:
  if type(i) == str:
    if len(i.split()) <= 4:
      i = i.replace("(a)","")
      if i not in captured_players[0]:
        try:
          mySql_insert_query = """INSERT INTO Masters_Players (first_name,last_name) 
                            VALUES 
                           ('""" + i.split(" ", 1)[0] + """','""" + i.split(" ", 1)[1] + """')"""

          cursor = mydb.cursor()
          cursor.execute(mySql_insert_query)
          mydb.commit()
          print(cursor.rowcount, "Record inserted successfully into Laptop table")
          cursor.close()

        except mysql.connector.Error as error:
          print("Failed to insert record into Laptop table {}".format(error))


# The names are then useed to populate the player first name and last name column in the Masters_Players table. We can get the rest of the player info later

# df.to_sql(con=con, name='table_name_for_df', if_exists='replace', flavor='mysql')




