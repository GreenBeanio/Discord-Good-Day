#!/usr/bin/env python3
# region Import Modules
import discord
from discord.ext import tasks
import os
from dotenv import load_dotenv
import json
from pathlib import Path
import datetime
import zoneinfo

# endregion Import Modules
# region Variables
good_days = {}  # Used to load and store data about the good days
leader_board = {}  # Used to load and store the leaderboards
directory_path = (
    str(Path().resolve()) + "/Data/"
)  # Get the location of the directory and files
user_file_path = directory_path + "users.json"  # Path the the user information
leaderboard_file_path = directory_path + "leaderboard.json"  # Path to the leaderboards
discord_token = ""  # Variable for discord token
# endregion Variables
# region Initializing
# Load envrionment variables
load_dotenv()
discord_token = str(os.getenv("DISCORD_TOKEN"))
time_zone_string = str(os.getenv("TIME_ZONE"))
using_timezone = False  # Used for noting if a timezone is being used or local
time_zone = ""  # Used for storing the timezone
start_time = datetime.datetime  # Used for storing the start time to calculate uptime
if time_zone_string != "":
    using_timezone = True  # Set true if there is a timezone, if not leave false
    time_zone = zoneinfo.ZoneInfo(
        time_zone_string
    )  # Set a timezone if there is one, if not leave as an empty string
if using_timezone == True:
    start_time = datetime.datetime.today().astimezone(
        time_zone
    )  # Get start time with timezone if using a specific timezone
else:
    start_time = (
        datetime.datetime.today().astimezone()
    )  # Get start time with local timezone if using a specfic timezone
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
        # Printing a log message
        print(f"{self.user.name} Bot: connected to the server")
        # Getting tomorrows midnight
        tomorrow = self.Get_Midnight()
        # Wating until midnight tomorrow to start the loop (if it isn't already running somehow)
        if not self.Daily_Refresh.is_running():
            await discord.utils.sleep_until(tomorrow)
            # Start a rerfresh loop
            await self.Daily_Refresh.start()

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
                    # Variable for the user to check
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
                        today_string = ""
                        if using_timezone == True:
                            today = datetime.datetime.today().astimezone(time_zone)
                            today_string = datetime.datetime.strftime(
                                today,
                                "%Y-%m-%d",
                            )
                        else:
                            today = datetime.datetime.today().astimezone()
                            today_string = datetime.datetime.strftime(today, "%Y-%m-%d")
                        self.Update_Stats(str(user), str(today_string), False)
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

                # Check the first 5 for the "!leaderboard" command
                elif message.content[0:12] == "!leaderboard":
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
                        'Do "!days" to see your stats\nDo "!days @user" to see their stats\nDo "!leaderboard" to see the leaderboard\nDo "!uptime" to see how long the bot has been running\
                            \nDo "!time" to see times\nDo "!help" to see commands\nRemember to say "Good Day!',
                    )
                # Check uptime
                elif message.content[0:7] == "!uptime":
                    # Get current time
                    current_time = ""
                    if using_timezone == True:
                        current_time = datetime.datetime.today().astimezone(time_zone)
                    else:
                        current_time = datetime.datetime.today().astimezone()
                    elapsed = await self.uptime(current_time)
                    await message.channel.send(
                        f"\U0001F607 I have been tracking Good Days for {elapsed}! \U0001F607"
                    )
                elif message.content[0:5] == "!time":
                    # Getting Today's Time
                    today = ""
                    yesterday = ""
                    if using_timezone == True:
                        today = datetime.datetime.today().astimezone(time_zone)
                        yesterday_1 = today - datetime.timedelta(days=1)
                        yesterday = datetime.datetime.combine(
                            yesterday_1, datetime.datetime.min.time()
                        ).astimezone(time_zone)
                        # today_string = datetime.datetime.strftime(today,"%Y-%m-%d",)
                    else:
                        today = datetime.datetime.today().astimezone()
                        yesterday = datetime.datetime.combine(
                            yesterday_1, datetime.datetime.min.time()
                        ).astimezone()
                        # today_string = datetime.datetime.strftime(today, "%Y-%m-%d")
                    tomorrow = self.Get_Midnight()
                    # Print times for debugging purposes
                    print(f"Today: {today} | Today Type: {type(today)}")
                    print(f"Yesterday: {yesterday} | Yesterday Type: {type(yesterday)}")
                    print(f"Midnight: {tomorrow} | Midnight Type: {type(tomorrow)}")

            # If it's not a command check for and record good days
            elif "day" in str(message.content).lower():
                if "good" in str(message.content).lower():
                    # Update the activity for the user having a good day, even if they already did it today
                    await self.update_presence(message.author.name)
                    # Update the data on their good day status
                    today_string = ""
                    if using_timezone == True:
                        today = datetime.datetime.today().astimezone(time_zone)
                        today_string = datetime.datetime.strftime(
                            today,
                            "%Y-%m-%d",
                        )
                    else:
                        today = datetime.datetime.today().astimezone()
                        today_string = datetime.datetime.strftime(today, "%Y-%m-%d")
                    self.Check_User_Days(str(message.author.id), str(today_string))

    # Updates who is having a good day
    async def update_presence(self, user=""):
        activity = ""
        if user != "":
            activity = discord.Game(
                name=f"\U0001F629 {user} Is Having A Good Day! \U0001F629"
            )
        else:
            activity = discord.Game(
                name=f"\U0001F62D Nobody Is Having A Good Day \U0001F62D"
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
        yesterday = datetime.datetime.strptime(day, "%Y-%m-%d") - datetime.timedelta(
            days=1
        )
        yesterday_string = datetime.datetime.strftime(
            yesterday,
            "%Y-%m-%d",
        )
        # If a good day has been done and need updated
        if update == True:
            # Update the Streaks
            # If today was right after the last good day then increase the streak
            if last_good_day == str(yesterday_string):
                # Increasign the streak
                good_days[user]["Streaks"]["Current Streak"] += 1
                # Check if it's their new top streak
                if int(good_days[user]["Streaks"]["Current Streak"]) > int(
                    good_days[user]["Streaks"]["Top Streak"]
                ):
                    good_days[user]["Streaks"]["Top Streak"] += 1
            # Checking if a streak was lost
            # If the last good day isn't today or yesterday (they haven't said good day yet) then they lose their streak
            elif last_good_day != day and last_good_day != str(yesterday_string):
                good_days[user]["Streaks"]["Current Streak"] = 0
            # Updating days
            good_days[user]["Stats"]["Good Days"] += 1
            good_days[user]["Stats"]["Last Good Day"] = day
            # Update the leaderboard
            self.update_leaderboard(user)
        # If just checking if the current streak is accurate
        else:
            # Checking if a streak was lost
            if last_good_day != day and last_good_day != str(yesterday_string):
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
        elif user != "":
            # Getting the variables
            user_stats = {
                "Good Days": int(good_days[user]["Stats"]["Good Days"]),
                "Top Streak": int(good_days[user]["Streaks"]["Top Streak"]),
                "Current Streak": int(good_days[user]["Streaks"]["Current Streak"]),
            }
            # Checking leaderboards in each category
            for y in ["Good Days", "Top Streak", "Current Streak"]:
                # region Prevent Double Pleacement (Very convoluted)
                # If the user is in first place already
                if leader_board[y]["First Place"]["User"] == user:
                    # If there current score is less than the score on the board, remove them
                    if user_stats[y] < int(leader_board[y]["First Place"][y]):
                        # Move second place to first
                        leader_board[y]["First Place"] = leader_board[y]["Second Place"]
                        # Move third place to second
                        leader_board[y]["Second Place"] = leader_board[y]["Third Place"]
                        # Getting third place
                        # Set third place to empty to start
                        leader_board[y]["Third Place"] = {
                            "User": "Empty",
                            y: "0",
                        }
                        # Look through every user
                        for z in good_days:
                            # Getting their score
                            good_day_stats = {
                                "Good Days": int(good_days[z]["Stats"]["Good Days"]),
                                "Top Streak": int(
                                    good_days[z]["Streaks"]["Top Streak"]
                                ),
                                "Current Streak": int(
                                    good_days[z]["Streaks"]["Current Streak"]
                                ),
                            }
                            # Checking if their score is below or equal to second place and their score is higher than third place
                            if good_day_stats[y] <= int(
                                leader_board[y]["Second Place"][y]
                            ) and good_day_stats[y] > int(
                                leader_board[y]["Third Place"][y]
                            ):
                                # If second place isn't them then set them to third place
                                if leader_board[y]["Second Place"]["User"] != user:
                                    leader_board[y]["Third Place"] = {
                                        "User": z,
                                        y: good_day_stats[y],
                                    }
                # If the user is in second place already
                if leader_board[y]["Second Place"]["User"] == user:
                    # If there current score is less than the score on the board, remove them
                    if user_stats[y] < int(leader_board[y]["Second Place"][y]):
                        # Move third place to second
                        leader_board[y]["Second Place"] = leader_board[y]["Third Place"]
                        # Getting third place
                        # Set third place to empty to start
                        leader_board[y]["Third Place"] = {
                            "User": "Empty",
                            y: "0",
                        }
                        # Look through every user
                        for z in good_days:
                            # Getting their score
                            good_day_stats = {
                                "Good Days": int(good_days[z]["Stats"]["Good Days"]),
                                "Top Streak": int(
                                    good_days[z]["Streaks"]["Top Streak"]
                                ),
                                "Current Streak": int(
                                    good_days[z]["Streaks"]["Current Streak"]
                                ),
                            }
                            # Checking if their score is below or equal to second place and their score is higher than third place
                            if good_day_stats[y] <= int(
                                leader_board[y]["Second Place"][y]
                            ) and good_day_stats[y] > int(
                                leader_board[y]["Third Place"][y]
                            ):
                                # If second place isn't them then set them to third place
                                if leader_board[y]["Second Place"]["User"] != user:
                                    leader_board[y]["Third Place"] = {
                                        "User": z,
                                        y: good_day_stats[y],
                                    }
                # If the user is in third place already
                if leader_board[y]["Third Place"]["User"] == user:
                    # Getting third place
                    # Set third place to empty to start
                    leader_board[y]["Third Place"] = {
                        "User": "Empty",
                        y: "0",
                    }
                    # Look through every user
                    for z in good_days:
                        # Getting their score
                        good_day_stats = {
                            "Good Days": int(good_days[z]["Stats"]["Good Days"]),
                            "Top Streak": int(good_days[z]["Streaks"]["Top Streak"]),
                            "Current Streak": int(
                                good_days[z]["Streaks"]["Current Streak"]
                            ),
                        }
                        # Checking if their score is below or equal to second place and their score is higher than third place
                        if good_day_stats[y] <= int(
                            leader_board[y]["Second Place"][y]
                        ) and good_day_stats[y] > int(
                            leader_board[y]["Third Place"][y]
                        ):
                            # If second place isn't them then set them to third place
                            if leader_board[y]["Second Place"]["User"] != user:
                                leader_board[y]["Third Place"] = {
                                    "User": z,
                                    y: good_day_stats[y],
                                }
                # endregion Prevent Double Pleacement
                # region Progress Leaderboard
                # If the user is higher than the first place replace it and move the old first place down to second place
                if user_stats[y] > int(leader_board[y]["First Place"][y]):
                    # If you aren't breaking your own highscore add yourself
                    if leader_board[y]["First Place"]["User"] != user:
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
                    # If you aren't breaking your own highscore add yourself & you aren't in first place (Prevents double placement)
                    if (
                        leader_board[y]["Second Place"]["User"] != user
                        and leader_board[y]["First Place"]["User"] != user
                    ):
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
                    # Move to third place if you aren't in first or second place (Prevents double placement)
                    if (
                        leader_board[y]["Second Place"]["User"] != user
                        and leader_board[y]["First Place"]["User"] != user
                    ):
                        leader_board[y]["Third Place"] = {
                            "User": user,
                            y: user_stats[y],
                        }
            # endregion Progress Leaderboard
        # Save to json
        with open(leaderboard_file_path, "w") as outputfile:
            json.dump(leader_board, outputfile, sort_keys=False, indent=4)

    ### Get Next Midnight
    def Get_Midnight(self):
        midnight = ""
        if using_timezone == True:
            today = datetime.datetime.today().astimezone(time_zone)
            tomorrow = today + datetime.timedelta(days=1)
            midnight = datetime.datetime.combine(
                tomorrow, datetime.datetime.min.time()
            ).astimezone(time_zone)

        else:
            today = datetime.datetime.today().astimezone()
            tomorrow = today + datetime.timedelta(days=1)
            midnight = datetime.datetime.combine(
                tomorrow, datetime.datetime.min.time()
            ).astimezone()
        return midnight

    ### Daily Refresh to Check Users and Leaderboard every day at midnight
    @tasks.loop(hours=24)
    async def Daily_Refresh(self):
        # Update all users and the leaderboard
        for x in good_days:
            # Update the users stats
            today_string = ""
            if using_timezone == True:
                today = datetime.datetime.today().astimezone(time_zone)
                today_string = datetime.datetime.strftime(
                    today,
                    "%Y-%m-%d",
                )
            else:
                today = datetime.datetime.today().astimezone()
                today_string = datetime.datetime.strftime(today, "%Y-%m-%d")
            self.Update_Stats(str(x), str(today_string), False)
            # Updating the leaderboard
            self.update_leaderboard(x)
        # Update the presence to no one is having a good day :^(
        await self.update_presence("")

    ### Calculating the uptime
    async def uptime(self, current_time):
        # Makes a timedelta
        uptime_delta = current_time - start_time
        # Convert it into an int
        uptime_seconds = int(uptime_delta.total_seconds())
        # Convert into times with meaning
        elapsed_days, remainder_days = divmod(uptime_seconds, 86400)
        elapsed_hours, remainder_minutes = divmod(remainder_days, 3600)
        elapsed_minutes, elapsed_seconds = divmod(remainder_minutes, 60)
        # Format into a string
        elapsed_string = str(
            f"{elapsed_days} Days, {elapsed_hours} Hours, {elapsed_minutes} Minutes, and {elapsed_seconds} Seconds"
        )
        return elapsed_string


# Setting the bots intentions
intents = discord.Intents.default()
intents.message_content = True
# Starting and conencting the bot
client = Good_Day_Bot(
    intents=intents,
    activity=discord.Game(name=f"\U0001F62D Nobody Is Having A Good Day \U0001F62D"),
)
client.run(discord_token)
