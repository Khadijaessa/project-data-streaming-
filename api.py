#importing required library
import boto3
import csv
import io
import json
import toml #library to load my configuration files
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests

app = FastAPI()
current_line = 0  #To keep track of the current row so  it is initially set to zero
app_config = toml.load('config.toml') #loading aws configuration files
access_key = app_config['s3']['keyid'] #getting access key id from config.toml file
secret_access_key = app_config['s3']['keysecret'] #getting access key secrets from config.toml file
s3 = boto3.client('s3' , aws_access_key_id=access_key, aws_secret_access_key=secret_access_key) #access s3 high level api to interact with s3


triggered = False


"""
Defining API endpoints using the @app.get() decorator
"""

@app.get("/", response_class=HTMLResponse)
async def root():

    return """
        <!DOCTYPE html>
        <html>
          <head>
            <meta charset="UTF-8">
            <title>Hi,Welcome to movies trending data API</title>
            <style>
              body {
                background-color: #F5F5F5;
                font-family: Times, serif;
              }
              #container {
                width: 80%;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #FFFFFF;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
              }
              h1 {
                color: #800080; /* Couleur mauve */
                text-align: center;
                transition: transform 0.3s ease;
              }
              h1:hover {
              transform: scale(1.2);
              }
	      p {
                color: #000000;
                font-size: 18px;
                line-height: 1.5;
                margin: 20px 0;
              }
            </style>
          </head>
          <body>
            <div id="container">
              <h1>Hi Welcome to movies rating data API</h1>
	      <p>Veuillez ajouter `/docs` à l'adresse IP pour accéder à l'interface swagger</p>
            </div>
          </body>
        </html>
    """

@app.get("/rating")
async def get_line():
    """
    This api reads the CSV file from the last row to the first row, which makes it easier to retrieve the latest data .
    Note: the stock data from csv file  has the oldest data at the bottom
    """

    """
     global current_line is a global variable that keeps track of the current line that has been retrieved from the CSV file
    """
    global current_line
    obj = s3.get_object(Bucket='stream-movies-bucket', Key='ratings.csv')

    """
    io.StringIO is used to parse the CSV data obtained from S3. The CSV data is read from S3 as a binary string using obj['Body'].read().
    This binary string is then decoded into a UTF-8 string using the decode() method.
    This decoded string is then passed to io.StringIO to create a file-like object that can be read using the csv.reader() method.
    """
    file = io.StringIO(obj['Body'].read().decode('utf-8'))
    reader = csv.reader(file)
    header = next(reader)
    lines = [row for row in reader] #list compression of all the rows in the csv file
    try:
        line = lines[len(lines) - 1 - current_line]  #expression calculates the index of the line to be retrieved from the lines list, which contains all the lines of the CSV file.
        result = {header[i]: line[i] for i in range(len(header))}
        current_line += 1   # keeps track of the current row in the csv file
        return result
    except IndexError:
        current_line = 0
        return {"error": "end of file"}

@app.get("/line1/{line_number}")
async def get_line_by_number(line_number: int):
    """
    optional api for trouble shooting
    API retrieves the stock data for a specific row by passing the row number as a parameter
    """
    obj = s3.get_object(Bucket='stream-movies-bucket', Key='ratings.csv')

    """
    io.StringIO is used to parse the CSV data obtained from S3. The CSV data is read from S3 as a binary string using obj['Body'].read().
    This binary string is then decoded into a UTF-8 string using the decode() method.
    This decoded string is then passed to io.StringIO to create a file-like object that can be read using the csv.reader() method.
    """
    file = io.StringIO(obj['Body'].read().decode('utf-8'))
    reader = csv.reader(file)
    header = next(reader)
    lines = [row for row in reader]
    try:
        line = lines[len(lines) - 1 - line_number]
        result = {header[i]: line[i] for i in range(len(header))}
        return result
    except IndexError:
        return {"error": "line not found"}

if __name__ == "__main__":

    """
    the program starts the FastAPI server using app.run(port=8000) on port 8000.
    The API can be accessed by sending HTTP requests to the endpoints at
    """
    app.run(port=8000)