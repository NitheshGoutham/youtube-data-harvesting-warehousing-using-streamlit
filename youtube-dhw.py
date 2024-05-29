#Packages required
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import mysql.connector 
from mysql.connector import MySQLConnection
from mysql.connector import Error as MySQLError
import pandas as pd
import streamlit as st
from datetime import datetime,timedelta
import json

#API connection 
def Api_connect():
    api_key = "AIzaSyAtWk3x-JtRuLR8jUR_R23At8-6r4Yo648"
    api_service_name = "youtube"
    api_version = "v3"

    youtube = build(api_service_name, api_version, developerKey=api_key)
    return youtube

utube_call = Api_connect()

#SQL connection
mydb=mysql.connector.connect(host="localhost",
                                        user="root",
                                        password="Nith@2000",
                                        database="youtube",
                                        port="3306")
cursor=mydb.cursor()

#Get Channel Information
def Channel_Info(channel_id):

    cursor.execute("""CREATE TABLE IF NOT EXISTS channel_info (
                        channel_name VARCHAR(255),
                        channel_id VARCHAR(255) PRIMARY KEY,
                        subscribe INT,
                        views INT,
                        total_videos INT,
                        channel_description TEXT,
                        playlist_id VARCHAR(255)
                    )""")
    
    request = utube_call.channels().list(
        part="snippet,contentDetails,statistics",
        id=channel_id
    )
    response = request.execute()
    
    for item in response.get('items',[]):
        details = dict(Channel_Name= item['snippet']['title'],
            Channel_Id= item['id'],
            Subscribers= item['statistics']['subscriberCount'],
            Views= item['statistics']['viewCount'],
            Total_Videos= item['statistics']['videoCount'],
            Channel_Description= item['snippet']['description'],
            Playlist_Id=item['contentDetails']['relatedPlaylists']['uploads']
        )
    
        cursor.execute("INSERT INTO channel_info (channel_name, channel_id, subscribe, views, total_videos, channel_description, playlist_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (details['Channel_Name'], details['Channel_Id'], details['Subscribers'], details['Views'], details['Total_Videos'], details['Channel_Description'], details['Playlist_Id']))
        
        mydb.commit()
    return details

#Get Video Id
def Get_Video_Id(video_id):
    Video_ID=[]
    response=utube_call.channels().list(id=video_id,
                                    part='contentDetails').execute()

    Playlist_ID=response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    Next_Page_Token=None

    while True:
        request_1=utube_call.playlistItems().list(
                                                part='snippet',
                                                playlistId=Playlist_ID,
                                                maxResults=50,
                                                pageToken=Next_Page_Token).execute()
        for i in range(len(request_1['items'])):
            Video_ID.append(request_1['items'][i]['snippet']['resourceId']['videoId'])
        Next_Page_Token=request_1.get('nextPageToken')

        if Next_Page_Token is None:
            break
    
    return Video_ID


#Get Video Details
def parse_duration(duration_str):
    try:
        duration_seconds = int(duration_str[2:-1])
        return duration_seconds
    except ValueError:
        return None

def Get_Video_Details(Video_id):
    Video_List = []
    for v_id in Video_id:
        request = utube_call.videos().list(
            part="snippet,contentDetails,statistics",
            id=v_id
        )
        response = request.execute()

        cursor.execute("""CREATE TABLE IF NOT EXISTS video_details(
                    channel_name VARCHAR(255),
                    channel_id VARCHAR(255) ,
                    video_id VARCHAR(255) PRIMARY KEY ,
                    title TEXT,
                    tags TEXT,
                    thumbnail TEXT,
                    description TEXT,
                    published_date DATETIME,
                    duration TIME,
                    views BIGINT,
                    likes INT,
                    dislikes INT,
                    comments INT
                )"""
                        )

        for item in response['items']:
            Data = dict(
                channel_Name=item['snippet']['channelTitle'],
                Channel_Id= item['snippet']['channelId'],
                Video_Id= item['id'],
                Title= item['snippet']['title'],
                Tags= json.dumps(item.get('tags')),
                Thumbnail=json.dumps(item['snippet']['thumbnails']),
                Description=item['snippet'].get('description', ''),
                Publish_Date= item['snippet']['publishedAt'],
                Duration=item['contentDetails']['duration'],
                Views=item['statistics'].get('viewCount', 0),
                Likes= item['statistics'].get('likeCount', 0),
                Dislikes=item['statistics'].get('dislikeCount'),
                Comments= item['statistics'].get('commentCount', 0)
                )
            
            Video_List.append(Data)

            duration_seconds = parse_duration(Data['Duration'])
            if duration_seconds is not None:
                duration = timedelta(seconds=duration_seconds)
            else:
                duration = timedelta(seconds=0) 
            current_datetime = datetime.now()
            updated_datetime = current_datetime + duration
            sql_duration = updated_datetime.strftime('%Y-%m-%d %H:%M:%S')

            iso_datetime = Data['Publish_Date']
            parsed_datetime = datetime.fromisoformat(iso_datetime.replace('Z', '+00:00'))
            mysql_published_date = parsed_datetime.strftime('%Y-%m-%d %H:%M:%S')
            
        
        cursor.execute("INSERT INTO video_details(channel_name, channel_id, video_id, title ,tags ,thumbnail , description, published_date, duration, views, likes, dislikes, comments) VALUES (%s, %s, %s, %s, %s, %s,  %s, %s, %s, %s,%s,%s,%s)",
                (Data['channel_Name'], Data['Channel_Id'], Data['Video_Id'],Data['Title'],Data['Tags'], Data['Thumbnail'], Data['Description'],mysql_published_date, sql_duration, Data['Views'], Data['Likes'], Data['Dislikes'], Data['Comments']))
       
    
        mydb.commit()    
            
    return Video_List

#Get Comment Details
def get_comment_Details(get_Comment):
    comment_List=[]
    try:
        cursor.execute("""CREATE TABLE IF NOT EXISTS comment_details (
                            comment_id VARCHAR(255) PRIMARY KEY ,
                            video_id VARCHAR(255)  ,
                            comment_text TEXT,
                            author VARCHAR(255),
                            published_date DATETIME
                        )""")
        for Com_Det in get_Comment:
            request=utube_call.commentThreads().list(
                part="snippet",
                videoId=Com_Det,
                maxResults=50
            )
            response=request.execute()

            for item in response['items']:
                    Comment_Det=dict(Comment_ID=item['snippet']['topLevelComment']['id'],
                                    Video_Id=item['snippet']['topLevelComment']['snippet']['videoId'],
                                    Comment_Text=item['snippet']['topLevelComment']['snippet']['textDisplay'],
                                    Author_Name=item['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                                    Published_Date=item['snippet']['topLevelComment']['snippet']['publishedAt'])
                    
                    comment_List.append(Comment_Det)

                    iso_datetime = Comment_Det['Published_Date']
                    parsed_datetime = datetime.fromisoformat(iso_datetime.replace('Z', '+00:00'))
                    mysql_published_dates = parsed_datetime.strftime('%Y-%m-%d %H:%M:%S')

                    cursor.execute("INSERT INTO comment_details (comment_id, video_id, comment_text, author, published_date) VALUES (%s, %s, %s, %s,%s)",
                                (Comment_Det['Comment_ID'], Comment_Det['Video_Id'], Comment_Det['Comment_Text'], Comment_Det['Author_Name'],mysql_published_dates))
                    mydb.commit()
                    
    except Exception as e:
        print(f"Error: {e}")
        
    return comment_List

#get_playlist_details
def get_playlist_details(channel_id):
    Playlist_Data=[]
    try:
        cursor.execute("""CREATE TABLE IF NOT EXISTS playlist_details (
                            playlist_id VARCHAR(255),
                            title VARCHAR(255),
                            channel_id VARCHAR(255),
                            published_date DATETIME,
                            video_count INT
                        )""")
        Next_Page_Token=None

        while True:
            request=utube_call.playlists().list(
            part="snippet,contentDetails",
            channelId=channel_id,
            maxResults=50,
            pageToken=Next_Page_Token
        )
            response=request.execute()

            for item in response['items']:
                PlayList_Det=dict(Playlist_Id=item['id'],
                            Title= item['snippet']['title'],
                            Channel_Id=item['snippet']['channelId'],
                            Published_Date=item['snippet']['publishedAt'],
                            Video_Count=item['contentDetails']['itemCount']
                            )
            Playlist_Data.append(PlayList_Det)

            Next_Page_Token=response.get('nextPageToken')
            if Next_Page_Token is None:
                break

        iso_datetime = PlayList_Det['Published_Date']
        parsed_datetime = datetime.fromisoformat(iso_datetime.replace('Z', '+00:00'))
        mysql_published_datee = parsed_datetime.strftime('%Y-%m-%d %H:%M:%S')

        # Insert data into MySQL
        cursor.execute("INSERT INTO playlist_details (playlist_id, title, channel_id, published_date, video_count) VALUES (%s, %s, %s, %s, %s)",
        (PlayList_Det['Playlist_Id'], PlayList_Det['Title'], PlayList_Det['Channel_Id'], mysql_published_datee, PlayList_Det['Video_Count']))
        mydb.commit()
    except Exception as e:
        print(f"Error: {e}")

    return Playlist_Data

#Overall Function get details
def fetch_all_data(channel_id):
    channel_info = Channel_Info(channel_id)
    video_id=Get_Video_Id(channel_id)
    playlist_details = get_playlist_details(channel_id)
    video_details = Get_Video_Details(video_id)
    comment_details = get_comment_Details(video_id)

# Convert dict to DataFrames
    channel_df = pd.DataFrame([channel_info])
    video_df = pd.DataFrame(video_id)
    playlist_df = pd.DataFrame(playlist_details)
    video_detail_df = pd.DataFrame(video_details)
    comment_df = pd.DataFrame(comment_details)
    
    return {
        "channel_details": channel_df,
        "video_details": video_df,
        "comment_details": comment_df,
        "playlist_details": playlist_df,
        "video_data": video_detail_df
    }

# Streamlit page
def main():
    
    st.sidebar.header(':red[MENU]')
    option=st.sidebar.radio(":black[Select option]",['Home','Data Collection','Data Analysis'])
    with st.sidebar:
       
        st.write('-----')
        
        st.markdown(
    """
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0" />
    <style>
    .material-symbols-outlined {
        font-variation-settings:
        'FILL' 0,
        'wght' 400,
        'GRAD' 0,
        'opsz' 24;
    }
    </style>
    """,
    unsafe_allow_html=True
)
        st.markdown(
    """
    <div style="font-family: 'Material Symbols Outlined'; font-size: 48px;">
        <span class="material-symbols-outlined">Copyright</span>
    </div>
    """,
    unsafe_allow_html=True
    
)
        st.subheader(':black[2024-NG]')   

    if option=="Home":
            st.title(':red[You]Tube :red[Data Harvesting & Warehousing using SQL and Streamlit]')
            st.write('---')
            st.subheader(':red[Domain :] Social Media')
            st.subheader(':red[Overview :]')
            st.markdown('''In this project, I developed a sophisticated dashboard using Streamlit to retrieve and visualize YouTube channel data through the YouTube API. 
                        The data is warehoused in an SQL database, facilitating efficient querying and analysis.
                         This project enabled the visualization of data within the Streamlit app, uncovering valuable insights and trends in YouTube channel performance.''')
            st.subheader(':red[Skill Take Away :]')
            st.markdown(''' Python scripting,Data Collection,API integration,Data Management using SQL,Streamlit''')
            st.subheader(':red[About :]')
            st.markdown('''Hello! I'm Nithesh Goutham, a BE graduate with a strong interest in data science and analytics. Currently, I'm an IT professional with 2 years of experience, 
                        and I'm excited to share my first project: "YouTube Data Harvesting and Warehousing Using SQL and Streamlit." In this project, I delved into the world of YouTube data to extract meaningful insights.
                         This experience has fueled my passion for data-driven decision-making and enhanced my understanding of data extraction techniques and database management.''')
            st.subheader(':red[Contact:]')
            st.markdown('###### Email : nitheshgoutham2000@gmail.com')
            st.markdown('###### Github : https://github.com/NitheshGoutham')
            st.markdown('###### Website : https://digital-cv-using-streamlit.onrender.com/')
            st.markdown('###### Linkedin: https://www.linkedin.com/in/nithesh-goutham-m-0b0514205/')
           

    elif option=="Data Collection":
            st.header(':white[Data Collection and Upload]', divider= 'red')
            st.markdown('''
                - Enter channel ID in the input field.
                - Clicking the 'Get Channel Details' button will display an overview of youtube channel.
                ''')
            st.markdown('''
                :red[note:] ***you can get the channel ID :***
                open youtube - go to any channel - go to about - share channel - copy the channel ID''')
            st.write( "-----")
            channel_id = st.text_input("Enter Channel ID")

            if st.button("Get Channel Details"):
                with st.spinner('Extraction in progress...'):
                    try:
                        details = fetch_all_data(channel_id)
                        
                        st.subheader('Channel Details')
                        st.write(details["channel_details"])

                        st.subheader('Video Details')
                        st.write(details["video_data"])

                        st.subheader('Comment Details')
                        st.write(details["comment_details"])

                        st.subheader('Playlist Details')
                        st.write(details["playlist_details"])

                    except HttpError as e:
                        if e.resp.status == 403 and e.error_details[0]["reason"] == 'quotaExceeded':
                            st.error("API Quota exceeded. Please try again later.")
                        else:
                            st.error(f"An HTTP error occurred: {e}")
                    except ValueError as e:
                        st.error(f"{e}")
                    except MySQLError as e:
                        if '1062' in str(e): 
                    # Check if the error message contains the code for duplicate entry error
                            st.error("It's already exists, try with another URL")
                        else:
                            st.error(f"Database error: {e}")
                    except Exception as e:
                        st.error(f"Please ensure to give a valid channel ID. Error: {e}")
                    
            
    elif option == "Data Analysis":
        st.header("Data Analysis",divider= 'red')

        questions = [
                    "1. What are the names of all the videos and their corresponding channels?",
                    "2. Which channels have the most number of videos, and how many videos do they have?",
                    "3. What are the top 10 most viewed videos and their respective channels?",
                    "4. How many comments were made on each video, and what are their corresponding video names?",
                    "5. Which videos have the highest number of likes, and what are their corresponding channel names?",
                    "6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?",
                    "7. What is the total number of views for each channel, and what are their corresponding channel names?",
                    "8. What are the names of all the channels that have published videos in the year 2022?",
                    "9. What is the average duration of all videos in each channel, and what are their corresponding channel names?",
                    "10. Which videos have the highest number of comments, and what are their corresponding channel names?"
                    ]

        selected_questions = st.multiselect("Select questions to execute", questions)
        if st.button("Run Selected Queries"):

            for selected_question in selected_questions:
        
                if selected_question == questions[0]:
                    cursor.execute("SELECT channel_name,title FROM video_details")
                    data = cursor.fetchall()
                    df = pd.DataFrame(data, columns=['Channel Name', 'Title'])
                    st.write(df)

                        
                elif selected_question == questions[1]:
                    cursor.execute("SELECT channel_name, COUNT(*) as video_count FROM video_details GROUP BY channel_name ORDER BY video_count DESC")
                    data=cursor.fetchall()
                    df = pd.DataFrame(data, columns=['Channel Name', 'Counts'])
                    st.write(df)

                    
                elif selected_question == questions[2]:
                    cursor.execute("SELECT channel_name,title,views FROM video_details ORDER BY views DESC LIMIT 10")
                    data=cursor.fetchall()
                    df = pd.DataFrame(data, columns=['Channel Name', 'Title', 'Views'])
                    st.write(df)

                elif selected_question == questions[3]:
                    cursor.execute("SELECT title,comments FROM video_details")
                    data=cursor.fetchall()
                    df=df=pd.DataFrame(data, columns=['Title','Comments'])
                    st.write(df)

                elif selected_question == questions[4]:
                    cursor.execute("SELECT channel_name,MAX(likes) as max_likes FROM video_details GROUP BY channel_name")
                    data=cursor.fetchall()
                    df=pd.DataFrame(data, columns=['Channel_Name','Likes'])
                    st.write(df)

                elif selected_question == questions[5]:
                    cursor.execute("SELECT title, SUM(likes) as total_likes, SUM(dislikes) as total_dislikes FROM video_details GROUP BY title")
                    data=cursor.fetchall()
                    df=pd.DataFrame(data, columns=['Title','Likes','Dislikes'])
                    st.write(df)

                elif selected_question == questions[6]:
                    cursor.execute("SELECT channel_name, SUM(views) as total_views FROM video_details GROUP BY channel_name")
                    data=cursor.fetchall()
                    df = pd.DataFrame(data, columns=['Channel_Name', 'Views'])
                    st.write(df)

                elif selected_question == questions[7]:
                    cursor.execute("SELECT DISTINCT channel_name FROM video_details WHERE YEAR(published_date) = 2022;")
                    data=cursor.fetchall()
                    df = pd.DataFrame(data, columns=['Channel_Name'])
                    st.write(df)

                elif selected_question == questions[8]:
                    cursor.execute("SELECT channel_name, AVG(duration) AS avg_duration FROM video_details GROUP BY channel_name ")
                    data=cursor.fetchall()
                    df = pd.DataFrame(data, columns=['Channel_Name', 'Avg_Duration'])
                    st.write(df)

                elif selected_question == questions[9]:
                    cursor.execute("""SELECT title, channel_name, SUM(comments) as comments
                            FROM video_details 
                            GROUP BY title, channel_name 
                            ORDER BY comments DESC 
                            LIMIT 1
                        """)
                    data = cursor.fetchall()
                    df=pd.DataFrame(data,columns=['Title','Channel_Name','Comments'])
                    st.write(df)
                    
            
if __name__ == "__main__":
    main()
