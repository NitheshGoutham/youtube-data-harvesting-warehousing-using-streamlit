# youtube-data-harvesting-warehousing-using-streamlit
YouTube Data Harvesting and Warehousing using SQL and Streamlit

📘 Introduction

- The project about Building a simple dashboard or UI using Streamlit.
- Retrieve YouTube channel data with the help of YouTube API.
- Stored the data in SQL database(warehousing).
- Enabling querying of the data using SQL and Streamlit.

Domain : 📱 Social Media

🎨 Skills Takeaway :

Python scripting, Data Collection, Streamlit, API integration, Data Management using SQL

📘 Overview
🌾Data Harvesting:
- Utilizing the YouTube API to collect data such as video details, channel information, playlists, and comments.

📥 Data Storage:
- Setting up a local MySQL database .
- Creating tables to store the harvested YouTube data.
- Using SQL scripts to insert the collected data into the database.

📊 Data Analysis and Visualization:
- Developing a Streamlit application to interact with the SQL database.
- Performing analysis on the stored YouTube data

🛠 Technology and Tools
- Python 
- MYSQL
- Youtube API
- Streamlit

📚 Packages and Libraries

👉 from googleapiclient.discovery import build
👉 import mysql.connector
👉 import pandas as pd
👉 import streamlit as st
👉 from datetime import datetime,timedelta
👉 import json


📘 Features

📚 Data Collection:
The data collection process involved retrieving various data points from YouTube using the YouTube Data API. Retrieve channel information, videos details, playlists and comments.

💾 Database Storage:
- The collected YouTube data was transformed into pandas dataframes. 
- Before that, a new database and tables were created.
- With the help of SQL, the data was inserted into the respective tables.
- The database could be accessed and managed in the MySQL environment .

📋Data Analysis:
 - By using YouTube channel data stored in the MySQL database, performed MySQL queries to answer 10 questions about the YouTube channels.
 - When selecting a question, the results will be displayed in the Streamlit application in the form of tables.


📘 Usage

- Enter a YouTube channel ID or name in the input field in Data collection option from sidebar menu.
- Click the "Get Channel Details" button to fetch and display channel information.


Contact:


LINKEDIN : https://www.linkedin.com/in/nithesh-goutham-m-0b0514205/        
WEBSITE : https://digital-cv-using-streamlit.onrender.com/               
EMAIL: nithesgoutham2000@gmail.com
