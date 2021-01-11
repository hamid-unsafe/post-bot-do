import requests
import psycopg2
from psycopg2.extras import DictCursor

DB_HOST='post-bot-db-do-user-8158092-0.b.db.ondigitalocean.com'
DB_NAME='post-bot'
DB_USER='admin'
DB_PASS='ofj65mnfmd73aguo'
DB_PORT=25060

db = None

def connectDB():
  global db
  
  db = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)

def exec(query, *args):
  global db

  try:
    cur = db.cursor(cursor_factory=DictCursor)

    if args:
      cur.execute(query, args[0])
    else:
      cur.execute(query)

    db.commit()

    cur.close()
  except Exception as e:
    requests.get(f'https://api.telegram.org/bot1277273103:AAFgDX0sP0bfU9hnfroPTEj9RzPqulfUlV8/sendMessage?chat_id=@ha_hack_auth&text=error happended in fucking postBot')

def exec_fetch(query, *args):
  res = None
  
  with db.cursor(cursor_factory=DictCursor) as cur:
    cur = db.cursor(cursor_factory=DictCursor)

    if args:
      cur.execute(query, args[0])
    else:
      cur.execute(query)

    res = cur.fetchall()

  db.commit()

  return res

def authenticate(id):
  users = exec_fetch('SELECT * FROM users WHERE id = %s', (id,))

  print(users)

def addUser(id, name):
  try:
    exec('INSERT INTO users (name, telegram_id, membership, is_admin, active_connector, current_action) VALUES (%s, %s, %s, %s, %s, %s)', (name, id, 'all', False, 0, 'none',))

    return True
  except:
    return False

def updateUser(id, col, val):
  exec(f'UPDATE users SET {col} = %s WHERE telegram_id = %s', (val, id,))

def initDB():
  connectDB()

  exec('CREATE TABLE connectors (id SERIAL PRIMARY KEY, name varchar(32), owner_id integer, sources text[], destinations text[], rules text[])')

  exec('CREATE TABLE users (id SERIAL PRIMARY KEY, name varchar, telegram_id integer, active_connector integer, bitly_token text, site_id text, membership text, is_admin boolean, current_action text)')

  closeDB()

def closeDB():
  global db
  
  db.close()

# initDB()