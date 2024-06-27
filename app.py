# Import the 'Flask' class from the 'flask' library.
from flask import Flask, request
#We can access the environment variables from the .env file through load_env()
from dotenv import load_dotenv
import os
import psycopg2, psycopg2.extras

def get_db_connection():
    connection = psycopg2.connect(
    #    host='127.0.0.1',
       database='pets_db',
    #    user=os.environ['POSTGRES_USER'],
    #    password=os.environ['POSTGRES_PASSWORD']
    )
    return connection


load_dotenv()
# Initialize Flask
# We'll use the pre-defined global '__name__' variable to tell Flask where it is.
app = Flask(__name__)

# Define our route
# This syntax is using a Python decorator, which is essentially a succinct way to wrap a function in another function.
@app.route('/')
def home():
  return "Hello, world!"

#Here, at this URL Endpoint we are executing the function that creates the connection to our PostgreSQL Database and we execute a SELECT query from the pets Table
@app.route("/pets")
def index():
   try:
    # raise Exception("Applicaiton Error")
    connection = get_db_connection()
    #Here, we can modify our connection.cursor() with a cursor_factory option, so we can define the format of our query results --> Here, we are defining a JSON format for our query results
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM pets;")
    pets = cursor.fetchall()
    connection.close()
    return pets
   except:
      return "Application Error", 500

@app.route("/pets", methods=['POST'])
def create_pet():
    try:
        new_pet = request.json
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("INSERT INTO pets (name, age, breed) VALUES (%s, %s, %s) RETURNING *", (new_pet['name'], new_pet['age'], new_pet['breed']))
        created_pet = cursor.fetchone()
        connection.commit() #Commit changes to the database
        connection.close()
        return created_pet, 201
    except Exception as e:
       return str(e), 500

@app.route("/pets/<pet_id>", methods=['GET'])
def show_pet(pet_id):
    try:
       connection = get_db_connection()
       cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
       #Here, we added a comma to the value of (pet_id,) because it helps protect against SQL injection in parameterized queries
       cursor.execute("SELECT * FROM pets WHERE id = %s", (pet_id,))
       pet = cursor.fetchone()
       if pet is None:
          connection.close()
          return "Pet Not Found", 404
       connection.close()
       return pet, 200
    except Exception as e:
       return str(e), 500
# Run our application, by default on port 5000 --> We can change the port by assigning it inside the app.run() method with "port=<number>"
app.run(port=3000)
