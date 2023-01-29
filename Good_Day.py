#!/usr/bin/env python3
# region Import Modules
import discord
import os
from dotenv import load_dotenv
import json
from pathlib import Path
import datetime

# endregion Import Modules
# region Variables
good_days = {}  # Used to load and store data about the good days
leader_board = {}  # Used to load and store the leaderboards
directory_path = (
    str(Path().resolve()) + "\Data\\"
)  # Get the location of the directory and files
user_file_path = directory_path + "users.json"  # Path the the user information
leaderboard_file_path = directory_path + "leaderboard.json"  # Path to the leaderboards
discord_token = ""  # Variable for discord token
# endregion Variables
# region Initializing
# Load envrionment variables
load_dotenv()
discord_token = os.getenv("DISCORD_TOKEN")
# Make direcotry if it doesn't exist
if os.path.exists(directory_path) == False:
    os.mkdir(directory_path)
# Make user file if it doesn't exist
if os.path.exists(user_file_path) == False:
    new_file = open(user_file_path, "x")
    new_file.close()
# Load the user data from json
with open(user_file_path) as inputfile:
    # Try to open the json file, and if it's blank/broken pass
    try:
        good_days = json.load(inputfile)
    except:
        pass
# Make leaderboard file if it doesn't exist
if os.path.exists(leaderboard_file_path) == False:
    new_file = open(leaderboard_file_path, "x")
    new_file.close()
# Load the leaderboard data from json
with open(leaderboard_file_path) as inputfile:
    # Try to open the json file, and if it's blank/broken pass
    try:
        leader_board = json.load(inputfile)
    except:
        pass
# endregion Initializing
# Class for the Good Day bot
class Good_Day_Bot(discord.Client):
    # When the bot connects to Discord
    async def on_ready(self):
        print(f"{self.user.name} Bot: connected to the server")

    # When someone sends a message in the server
    async def on_message(self, message):
        # Don't respond to yourself
        if message.author != self.user:
            ### Debug Information
            # message_information = {
            #    "Server": message.guild,
            #    "User": message.author,
            #    "Message": message.content,
            #    "Mentions": message.mentions,
            #    "Channel": message.channel,
            # }
            # print(message_information)
            # Check if the input is a command, by checkign the first letter for a "!"
            if message.content[0:1] == "!":
                # Check the first 5 for the "!days" command
                if message.content[0:5] == "!days":
                    # Variable for the user to checl
                    user = ""
                    # Check player names stats
                    if len(message.content) == 5:
                        # If the string is only "!days" get themselves
                        user = str(message.author.id)
                    else:
                        # If the string has more attempt to get the mention
                        split_message = str(message.content).split(
                            " ", 2
                        )  # 0 is the command, 1 is the name, 2 is whatever else could follow
                        user = split_message[1][
                            2:-1
                        ]  # User should be the only thing in the first split, and remvoing discord @ characters <@id>
                    # If they have had a good day
                    if str(user) in good_days:
                        # Updating the streak, just in case they haven't been having good days and updating it
                        today = datetime.datetime.strftime(
                            datetime.date.today(), "%Y-%m-%d"
                        )
                        self.Update_Stats(str(user), str(today), False)
                        # Writing the information
                        day_number = good_days[user]["Stats"]["Good Days"]
                        last_day = good_days[user]["Stats"]["Last Good Day"]
                        top_streak = good_days[user]["Streaks"]["Top Streak"]
                        current_streak = good_days[user]["Streaks"]["Current Streak"]
                        await message.channel.send(
                            f"\U0001F913 <@{user}> has the following: \U0001F913\
                                \n\U0001F975 They've had {day_number} Good Days! \U0001F975\
                                \n\U0001F92F Their Last Good Day was {last_day}! \U0001F92F\
                                \n\U0001F973 Their Top Streak was {top_streak}! \U0001F973\
                                \n\U0001F60E Their Current Streak is {current_streak}! \U0001F60E"
                        )
                    else:
                        # Send message that they've never had a good day :(
                        await message.channel.send(
                            "\U0001F62D I'm so sorry. They have never had a good day \U0001F62D"
                        )

                # Check the first 5 for the "!lead" command
                elif message.content[0:5] == "!lead":
                    # Initailize the leaderboard if it is empty
                    if len(leader_board) == 0:
                        self.update_leaderboard("")
                    # Getting the message text
                    message_text = ""  # Used for storing the result
                    for x in leader_board:
                        message_text += f"\n-------------------------------------------------\
                        \n{x}\
                        \n-------------------------------------------------"
                        for y in ["First Place", "Second Place", "Third Place"]:
                            # If the user isn't empty
                            if leader_board[x][y]["User"] != "Empty":
                                # HaHa Emoji
                                emoji = ""
                                if y == "First Place":
                                    emoji = "\U0001F438"
                                elif y == "Second Place":
                                    emoji = "\U0001F98E"
                                elif y == "Third Place":
                                    emoji = "\U0001F422"
                                message_text += f'\n{y}: {emoji} <@{leader_board[x][y]["User"]}> with {leader_board[x][y][x]} days! {emoji}'
                            else:
                                message_text += (
                                    f"\n{y}: \U0001F614 No \U0001F635 One \U0001F631"
                                )
                    message_text += (
                        f"\n-------------------------------------------------"
                    )
                    # Send message
                    await message.channel.send(message_text)
                # Check the first 5 for the "!help" command
                elif message.content[0:5] == "!help":
                    # Gives instructions
                    await message.channel.send(
                        'Do "!days" to see your stats\nDo "!days @user" to see their stats\nDo "!lead" to see the leaderboard\nRemember to say "Good Day!',
                    )
            # If it's not a command check for and record good days
            elif "day" in str(message.content).lower():
                if "good" in str(message.content).lower():
                    # Update the activity for the user having a good day, even if they already did it today
                    await self.update_presence(message.author.name)
                    # Update the data on their good day status
                    today = datetime.datetime.strftime(
                        datetime.date.today(), "%Y-%m-%d"
                    )
                    self.Check_User_Days(str(message.author.id), str(today))

    # Updates who is having a good day
    async def update_presence(self, user=""):
        activity = ""
        if user != "":
            activity = discord.Game(
                name=f"\U0001F629 {user} Is Having A Good Day! \U0001F629"
            )
        else:
            activity = discord.Game(
                name=f"\U0001F629 Nobody Is Having A Good Day \U0001F62D"
            )
        await self.change_presence(activity=activity)

    # Checking Dictionary
    def Check_User_Days(self, user, day):
        # Have to have good_days be global
        global good_days
        # If the user already has had good days
        if user in good_days:
            # If today hasn't already been coutned as a good day
            if day not in good_days[user]["Days"].values():
                # Get how many days they've done
                had_days = len(good_days[user]["Days"])
                # Add the new day
                good_days[user]["Days"][f"Day {had_days+1}"] = day
                # Add to their stats
                self.Update_Stats(user, day, True)
        # If the user is new
        else:
            # Add the new user, day, and empty data
            good_days[user] = {
                "Stats": {"Good Days": 0, "Last Good Day": day},
                "Streaks": {"Top Streak": 0, "Current Streak": 0},
                "Days": {"Day 1": day},
            }
            # Add to their stats
            self.Update_Stats(user, day, True)

    ### Check the users stats
    def Update_Stats(self, user, day, update):
        # Have to have good_days be global
        global good_days
        # Getting yesterdays date
        last_good_day = good_days[user]["Stats"]["Last Good Day"]
        yesterday = datetime.datetime.strptime(
            day, "%Y-%m-%d"
        ).date() - datetime.timedelta(days=1)
        # If a good day has been done and need updated
        if update == True:
            # Update the Streaks
            # If today was right after the last good day then increase the streak
            if last_good_day == str(yesterday):
                # Increasign the streak
                good_days[user]["Streaks"]["Current Streak"] += 1
                # Check if it's their new top streak
                if int(good_days[user]["Streaks"]["Current Streak"]) > int(
                    good_days[user]["Streaks"]["Top Streak"]
                ):
                    good_days[user]["Streaks"]["Top Streak"] += 1
            # Checking if a streak was lost
            # If the last good day isn't today or yesterday (they haven't said good day yet) then they lose their streak
            elif last_good_day != day and last_good_day != str(yesterday):
                good_days[user]["Streaks"]["Current Streak"] = 0
            # Updating days
            good_days[user]["Stats"]["Good Days"] += 1
            good_days[user]["Stats"]["Last Good Day"] = day
            # Update the leaderboard
            self.update_leaderboard(user)
        # If just checking if the current streak is accurate
        else:
            # Checking if a streak was lost
            if last_good_day != day and last_good_day != str(yesterday):
                # The streak was lost
                good_days[user]["Streaks"]["Current Streak"] = 0
        # Saving json
        with open(user_file_path, "w") as outputfile:
            json.dump(good_days, outputfile, sort_keys=False, indent=4)

    ### Check the leaderboard
    def update_leaderboard(self, user):
        # Have to have leader_board be global
        global leader_board
        # If the leaderboard is empty create it
        if len(leader_board) == 0:
            # Create an empty leaderboard
            leader_board["Good Days"] = {
                "First Place": {"User": "Empty", "Good Days": "0"},
                "Second Place": {"User": "Empty", "Good Days": "0"},
                "Third Place": {"User": "Empty", "Good Days": "0"},
            }
            leader_board["Top Streak"] = {
                "First Place": {"User": "Empty", "Top Streak": "0"},
                "Second Place": {"User": "Empty", "Top Streak": "0"},
                "Third Place": {"User": "Empty", "Top Streak": "0"},
            }
            leader_board["Current Streak"] = {
                "First Place": {"User": "Empty", "Current Streak": "0"},
                "Second Place": {"User": "Empty", "Current Streak": "0"},
                "Third Place": {"User": "Empty", "Current Streak": "0"},
            }
            # initialize the leaderboard if their are users in the list if not then leave as is
            if len(good_days) != 0:
                # For every user check their stats
                for x in good_days:
                    # Getting the variables
                    user_stats = {
                        "Good Days": int(good_days[x]["Stats"]["Good Days"]),
                        "Top Streak": int(good_days[x]["Streaks"]["Top Streak"]),
                        "Current Streak": int(
                            good_days[x]["Streaks"]["Current Streak"]
                        ),
                    }
                    # Checking leaderboards in each category
                    for y in ["Good Days", "Top Streak", "Current Streak"]:
                        # If the user is higher than the first place replace it and move the old first place down to second place
                        if user_stats[y] > int(leader_board[y]["First Place"][y]):
                            # Move second place to third
                            leader_board[y]["Third Place"] = leader_board[y][
                                "Second Place"
                            ]
                            # Move first place to second
                            leader_board[y]["Second Place"] = leader_board[y][
                                "First Place"
                            ]
                            # Move to to first place
                            leader_board[y]["First Place"] = {
                                "User": x,
                                y: user_stats[y],
                            }
                        # If the user is higher than the second place replace it and move the old second place down to third place
                        elif user_stats[y] > int(leader_board[y]["Second Place"][y]):
                            # Move second place to third
                            leader_board[y]["Third Place"] = leader_board[y][
                                "Second Place"
                            ]
                            # Move to second place
                            leader_board[y]["Second Place"] = {
                                "User": x,
                                y: user_stats[y],
                            }
                        # If the user is higher than the third place replace it and boot the old second place from the leaderboard
                        elif user_stats[y] > int(leader_board[y]["Third Place"][y]):
                            # Move to third place
                            leader_board[y]["Third Place"] = {
                                "User": x,
                                y: user_stats[y],
                            }
        # If the leaderboard exists then check it with the user name as long as the user name wasn't empty
        if user != "":
            # Getting the variables
            user_stats = {
                "Good Days": int(good_days[user]["Stats"]["Good Days"]),
                "Top Streak": int(good_days[user]["Streaks"]["Top Streak"]),
                "Current Streak": int(good_days[user]["Streaks"]["Current Streak"]),
            }
            # Checking leaderboards in each category
            for y in ["Good Days", "Top Streak", "Current Streak"]:
                # If the user is higher than the first place replace it and move the old first place down to second place
                if user_stats[y] > int(leader_board[y]["First Place"][y]):
                    # If you aren't breaking your own highscore add yourself
                    if leader_board[y]["First Place"][y] != user:
                        # Move second place to third
                        leader_board[y]["Third Place"] = leader_board[y]["Second Place"]
                        # Move first place to second
                        leader_board[y]["Second Place"] = leader_board[y]["First Place"]
                        # Move to to first place
                        leader_board[y]["First Place"] = {
                            "User": user,
                            y: user_stats[y],
                        }
                    # If you are breaking your own highscore then update only yourself
                    else:
                        leader_board[y]["First Place"] = {
                            "User": user,
                            y: user_stats[y],
                        }
                # If the user is higher than the second place replace it and move the old second place down to third place
                elif user_stats[y] > int(leader_board[y]["Second Place"][y]):
                    # If you aren't breaking your own highscore add yourself
                    if leader_board[y]["Second Place"][y] != user:
                        # Move second place to third
                        leader_board[y]["Third Place"] = leader_board[y]["Second Place"]
                        # Move to second place
                        leader_board[y]["Second Place"] = {
                            "User": user,
                            y: user_stats[y],
                        }
                    # If you are breaking your own highscore then update only yourself
                    else:
                        leader_board[y]["Second Place"] = {
                            "User": user,
                            y: user_stats[y],
                        }
                # If the user is higher than the third place replace it and boot the old second place from the leaderboard
                elif user_stats[y] > int(leader_board[y]["Third Place"][y]):
                    # Move to third place (No need to check if updating youself because it gets replaced either way)
                    leader_board[y]["Third Place"] = {
                        "User": user,
                        y: user_stats[y],
                    }
        # Save to json
        with open(leaderboard_file_path, "w") as outputfile:
            json.dump(leader_board, outputfile, sort_keys=False, indent=4)


# Setting the bots intentions
intents = discord.Intents.default()
intents.message_content = True
# Starting and conencting the bot
client = Good_Day_Bot(
    intents=intents,
    activity=discord.Game(name=f"\U0001F62D Nobody Is Having A Good Day \U0001F62D"),
)
client.run(discord_token)
