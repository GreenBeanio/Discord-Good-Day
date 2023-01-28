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
directory_path = (
    str(Path().resolve()) + "\Data\\"
)  # Get the location to store the files
file_path = directory_path + "data.json"

discord_token = ""  # Variable for discord token
# endregion Variables
# region Initializing
# Load envrionment variables
load_dotenv()
discord_token = os.getenv("DISCORD_TOKEN")
# Make direcotry if it doesn't exist
if os.path.exists(directory_path) == False:
    os.mkdir(directory_path)
# Make file if it doesn't exist
if os.path.exists(file_path) == False:
    new_file = open(file_path, "x")
    new_file.close()
# Load json
with open(file_path) as inputfile:
    # Try to open the json file, and if it's blank/broken pass
    try:
        good_days = json.load(inputfile)
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
                            f"\U0001F913 <@{user}> has the following \U0001F913 :\
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
                    # Checks the leaderbaord
                    #### Make a leader board!!! Using the stats for days, current streak, and top streak
                    ### Just have it be a diferent section in the json file probably. Store top 3 maybe
                    # Send the message
                    #### Probably want to make this fancy
                    await message.channel.send("Not made yet")
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
        # If just checking if the current streak is accurate
        else:
            # Checking if a streak was lost
            if last_good_day != day and last_good_day != str(yesterday):
                # The streak was lost
                good_days[user]["Streaks"]["Current Streak"] = 0
        # Saving json
        with open(file_path, "w") as outputfile:
            json.dump(good_days, outputfile, sort_keys=False, indent=4)


# Setting the bots intentions
intents = discord.Intents.default()
intents.message_content = True
# Starting and conencting the bot
client = Good_Day_Bot(
    intents=intents,
    activity=discord.Game(name=f"\U0001F62D Nobody Is Having A Good Day \U0001F62D"),
)
client.run(discord_token)
