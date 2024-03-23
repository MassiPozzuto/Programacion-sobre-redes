import mysql.connector as mysql
import sys
import re
import traceback
import datetime
import os

class Database():
  def log(self, parsename, detail):
    if not os.path.exists(path="log" + "/"):
      os.makedirs(name="log" + "/")

    path = "log/" + parsename + ".log"

    if os.path.isfile(path) is not True:
      f = open(path, "w")
      f.close()

    with open(path, "a") as f:
      f.write("Hora:" + str(datetime.datetime.now()) + "\n")
      f.write(str(detail) + "\n")
      f.write("\n")

    def __init__(self):
      self.server = "127.0.0.1"
      self.database = "users_data"
      self.username = "root"
      self.password = ""

      if self.password is None:
        self.password = ""

      self.conn = mysql.connect(user = self.username, password = self.password, host = self.server, database = self.database)
      self.cursor = self.conn.cursor(dictionary = True)

    def commit(self):
      self.conn.commit()

def QueryDb(self, query):
  contador = 0
  while True:
    contador += 1
    try:
      self.cursor.execute(query)
      
      if "SELECT" in query or "select" in query:
        result = self.cursor.fetchall()
        #self.conn.commit()
        return result
      else:
        #self.conn.commit()
        return True
      break
    except:
      text = traceback.format_exc() + "\n"
      text += query + "\n"
      self.log("DB", text)
      try:
        self.conn = mysql.connect(user = self.username, password = self.password, host = self.server, database = self.database)
        self.cursor = self.conn.cursor(dictionary = True)
      except:
        text = traceback.format_exc() + "\n"
        text = query + "\n"
        self.log("DBLOG", text)
      
      if contador == 3:
        break
    
  return None
  
def cerrarConexion(self):
  self.cursor.close()
  self.conn.close()

