import requests
import pandas as pd
import streamlit as st
import os
 
api_key = os.environ["FD_API_KEY"]
headers = { 'X-Auth-Token': api_key }
compId = '2018'

# team choices
choices = {
    'TW' : ['Portugal', 'Czechia', 'Croatia', 'Hungary'],
    'JT' : ['Portugal', 'Netherlands', 'Croatia', 'Hungary'],
    'JH' : ['Albania', 'Turkey', 'England', 'Netherlands'],
    'CO' : ['Denmark', 'Turkey', 'Ukraine', 'Romania'],
    'EL' : ['Belgium', 'Turkey', 'Poland', 'Slovakia'],
    'HS' : ['Georgia', 'Slovenia', 'Netherlands', 'Germany']
}

# competition matches
mUri = f'https://api.football-data.org/v4/competitions/{compId}/matches'
mResponse = requests.get(mUri, headers=headers)

# logo
emblem = mResponse.json()['competition']['emblem']

# ----------------------------------------------------------------------------------------------------------
# base functionality

# total goals scored per team
teamScores = {}

for match in mResponse.json()['matches']:
    homeTeam = match['homeTeam']['name']
    awayTeam = match['awayTeam']['name']
    homeScore = match['score']['fullTime']['home']
    awayScore = match['score']['fullTime']['away']

    if homeScore is None:
        homeScore = 0
    if awayScore is None:
        awayScore = 0

    if homeTeam in teamScores:
        teamScores[homeTeam] += homeScore
    else:
        teamScores[homeTeam] = homeScore

    if awayTeam in teamScores:
        teamScores[awayTeam] += awayScore
    else:
        teamScores[awayTeam] = awayScore

# total goals per user
userScores = {}
userGames = {}
crests = {match['homeTeam']['name'] : match['homeTeam']['crest'] for match in mResponse.json()['matches']}

for user, teams in choices.items():
    userScores[user] = sum(teamScores.get(team, 0) for team in teams)
    userGames[user] = sum(1 for match in mResponse.json()['matches'] if (match['homeTeam']['name'] in teams and match['status'] == 'FINISHED')) + sum(1 for match in mResponse.json()['matches'] if (match['awayTeam']['name'] in teams and match['status'] == 'FINISHED'))

sortedUserScores = dict(sorted(userScores.items(), key=lambda item: item[1], reverse=True))
userDf = pd.DataFrame(list(sortedUserScores.items()), columns=['Player', 'Total Goals'])

userDf['Total Games'] = userDf['Player'].map(userGames)
userDf['Team Crests'] = userDf['Player'].apply(
    lambda person: [crests[team] for team in choices[person] if team in crests]
)

# ----------------------------------------------------------------------------------------------------------
# converting images to HTML

def convert_to_img_html(urls, width=30, height=30):
    return ' '.join([f'<img src="{url}" width="{width}" height="{height}" />' for url in urls])

# Apply the function to the 'Team Crests' column
userDf['Team Crests'] = userDf['Team Crests'].apply(convert_to_img_html)

# ----------------------------------------------------------------------------------------------------------
# app programming


# custom html table (for displaying images)
html_table = """
<table border="1" class="dataframe">
    <thead>
        <tr>
            <th>Player</th>
            <th>Team Crests</th>
            <th>Total Goals</th>
            <th>Total Games</th>
        </tr>
    </thead>
    <tbody>
"""

for index, row in userDf.iterrows():
    html_table += "<tr>"
    html_table += f"<td>{row['Player']}</td>"
    html_table += f"<td>{row['Team Crests']}</td>"
    html_table += f"<td>{row['Total Goals']}</td>"
    html_table += f"<td>{row['Total Games']}</td>"
    html_table += "</tr>"

html_table += """
    </tbody>
</table>
"""

st.markdown(
    """
    <style>
    [data-testid="stSidebar"]{
        min-width: 400px;
        max-width: 800px;
    }
    </style>
     
    """,
    unsafe_allow_html=True,
)

# page locations
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f0f2f6;
    }
    .logo {
        position: absolute;
        top: 10px;
        right: 10px;
        width: 100px;
    }
    .dataframe-container {
        width: 80%; /* Adjust the width as needed */
        margin: auto; /* Center align the dataframe */
    }
    .dataframe th, .dataframe td {
        text-align: center !important;
    }
    .custom-title {
        display: flex;
        align-items: center;
    }
    .custom-title img {
        margin-right: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# displaying custom title
st.markdown(
    f"""
    <div class="custom-title">
        <h1>CMBWAP Euro 2024 21s</h1>
        <img src="{emblem}" width="50" height="50">
    </div>
    """,
    unsafe_allow_html=True
)

# displaying dataframe
st.markdown(
    f"""
    <div class="dataframe-container">
    {html_table}
    """, 
    unsafe_allow_html=True
)
