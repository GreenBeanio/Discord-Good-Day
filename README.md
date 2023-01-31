# Discord Good Day Bot

## What it does

It will track when someone says "Good Day".

## Reason for Creation

I like to say "Good Day" or something along those lines in discord everyday. This bot is a little gimmick I made as an inside joke. It will sit in the background and record who has been having and wishing the most good days.

## Commands
- !days
    - Return the user's "Good Day" stats.
- !days @USER
    - Returns the user in the @'s "Good Day" stats.
- !lead
    - Returns a leaderboard of the server's "Good Day" stats.
- !help
    - Lists the commands available.

## What you will need
- Python 3.9+
- Discord Bot Token
- IANA Time Zone (Optional)
- Docker (Optional)

## Setting up the Script

- In the .env file put your discord bot token in the quotes.
- Either enter an IANA Time Zone (Ex: "America/New_York") or leave an empty string. If it is left as an empty string it will use the local time zone of the system hosting the script.
- Remove the "blank" from "blank.env" so that it's just ".env"

## Running the Python Script
### Windows
- Initial Run
    - cd /your/folder
    - python3 -m venv env
    - call env/Scripts/activate.bat
    - python3 -m pip install -r requirements.txt
    - python3 Good_Day.py
- Running After
    - cd /your/folder
    - call env/Scripts/activate.bat && python3 Good_Day.py
### Linux
- Initial Run
    - cd /your/folder
    - python3 -m venv env
    - source env/bin/activate
    - python3 -m pip install -r requirements.txt
    - python3 Good_Day.py
- Running After
    - cd /your/folder
    - source env/bin/activate && python3 Good_Day.py

## Using Docker if Desired
- Set up the scrpt as you would've before
- Get into the directory
    - cd /your/folder
- Build the docker image
    - docker build -t discord_good_day
- Run the docker image as a container
    - docker run discord_good_day
- To stop the docker container
    - Get the docker name
        - docker ps
            - Copy the container ID or the container name
    - Stop the container (with what you copied)
        - docker stop copied_container
- To start back up that container (with what you copied)
    - docker start copied_container
- To delete the container if you need to (with what you copied)
    - docker rm copied_container
