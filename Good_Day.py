#!/usr/bin/env python3
# region Import Modules
import discord
from discord.ext import tasks
import asyncio
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
        # Starting with a Daily Refresh
        await self.Daily_Refresh()
        # Wating until midnight tomorrow to start the loop (if it isn't already running somehow)
        if not self.Daily_Refresh_Loop.is_running():
            # Getting time until midnight
            time_until_midnight = await self.Time_Until_Midnight()
            # Waiting until midnight
            await asyncio.sleep(time_until_midnight.total_seconds())
            # Start a refresh loop
            await self.Daily_Refresh_Loop.start()

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
                        await self.Update_Stats(
                            user=str(user),
                            day=await self.Get_Today(output_string=False),
                            update=False,
                        )
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

                # Check the first 12 for the "!leaderboard" command
                elif message.content[0:12] == "!leaderboard":
                    # Initailize the leaderboard if it is empty
                    if len(leader_board) == 0:
                        await self.update_leaderboard(user="")
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
                            \nDo "!time" to see times\nDo "!help" to see commands\nRemember to say "Good Day!"',
                    )
                # Check uptime
                elif message.content[0:7] == "!uptime":
                    # Calculate Timedelta of Time from Start
                    uptime_delta = (
                        await self.Get_Today(output_string=False) - start_time
                    )
                    # Convert into string
                    elapsed = await self.Timedelta_To_String(
                        timedelta=uptime_delta, include_day=True
                    )
                    await message.channel.send(
                        f"\U0001F607 I have been tracking Good Days for {elapsed}! \U0001F607"
                    )
                # Getting times for debug purposes
                elif message.content[0:5] == "!time":
                    # Converting today into a string (Doing this separately for timezone)
                    today_string = datetime.datetime.strftime(
                        await self.Get_Today(output_string=False),
                        "%Y-%m-%d %H:%M:%S %Z",
                    )
                    # Getting time until Midnight
                    time_until_midnight = await self.Time_Until_Midnight()
                    # Convert into string
                    time_until_string = await self.Timedelta_To_String(
                        timedelta=time_until_midnight, include_day=False
                    )
                    # Message times for debugging purposes
                    output = str(
                        f"Today: {today_string}\nTime Until Tomorrow: {time_until_string}"
                    )
                    await message.channel.send(output)
            # If it's not a command check for and record good days
            elif "day" in str(message.content).lower():
                if "good" in str(message.content).lower():
                    # Update the activity for the user having a good day, even if they already did it today
                    await self.update_presence(user=message.author.name)
                    # Update the data on their good day status
                    today = await self.Get_Today(output_string=False)
                    await self.Check_User_Days(user=str(message.author.id), day=today)

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
    async def Check_User_Days(self, user, day):
        # Have to have good_days be global
        global good_days
        # Get today as a string (instead of calling the function again)
        day_string = datetime.datetime.strftime(
            day,
            "%Y-%m-%d",
        )
        # If the user already has had good days
        if user in good_days:
            # If today hasn't already been coutned as a good day
            if day_string not in good_days[user]["Days"].values():
                # Get how many days they've done
                had_days = len(good_days[user]["Days"])
                # Add the new day
                good_days[user]["Days"][f"Day {had_days+1}"] = day_string
                # Add to their stats
                await self.Update_Stats(user=user, day=day, update=True)
        # If the user is new
        else:
            # Add the new user, day, and empty data
            good_days[user] = {
                "Stats": {"Good Days": 0, "Last Good Day": day_string},
                "Streaks": {"Top Streak": 0, "Current Streak": 0},
                "Days": {"Day 1": day_string},
            }
            # Add to their stats
            await self.Update_Stats(user=user, day=day, update=True)

    ### Check the users stats
    async def Update_Stats(self, user, day, update):
        # Have to have good_days be global
        global good_days
        # Getting last good day
        last_good_day = good_days[user]["Stats"]["Last Good Day"]
        # Getting yesterdays date
        yesterday_string = await self.Get_Yesterday(day=day, output_string=True)
        # Get today as a string (instead of calling the function again)
        day_string = datetime.datetime.strftime(
            day,
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
            elif last_good_day != day_string and last_good_day != str(yesterday_string):
                good_days[user]["Streaks"]["Current Streak"] = 0
            # Updating days
            good_days[user]["Stats"]["Good Days"] += 1
            good_days[user]["Stats"]["Last Good Day"] = day_string
            # Update the leaderboard
            await self.update_leaderboard(user=user)
        # If just checking if the current streak is accurate
        else:
            # Checking if a streak was lost
            if last_good_day != day_string and last_good_day != str(yesterday_string):
                # The streak was lost
                good_days[user]["Streaks"]["Current Streak"] = 0
        # Saving json
        with open(user_file_path, "w") as outputfile:
            json.dump(good_days, outputfile, sort_keys=False, indent=4)

    ### Check the leaderboard
    async def update_leaderboard(self, user):
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
                                # If second place and first place isn't them then set them to third place
                                if (
                                    leader_board[y]["Second Place"]["User"] != user
                                    and leader_board[y]["First Place"]["User"] != user
                                ):
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
                                # If second place and first place isn't them then set them to third place
                                if (
                                    leader_board[y]["Second Place"]["User"] != user
                                    and leader_board[y]["First Place"]["User"] != user
                                ):
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
                            # If second place and first place isn't them then set them to third place
                            if (
                                leader_board[y]["Second Place"]["User"] != user
                                and leader_board[y]["First Place"]["User"] != user
                            ):
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
                    # If you aren't breaking your own highscore
                    if leader_board[y]["Second Place"]["User"] != user:
                        # If you aren't in first place add yourself (Prevents double placement)
                        if leader_board[y]["First Place"]["User"] != user:
                            # Move second place to third
                            leader_board[y]["Third Place"] = leader_board[y][
                                "Second Place"
                            ]
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

    ### Getting Today
    async def Get_Today(self, output_string):
        # Getting Today's Time
        today = ""
        if using_timezone == True:
            today = datetime.datetime.today().astimezone(time_zone)
        else:
            today = datetime.datetime.today().astimezone()
        # Convert to string if output_string is true
        if output_string == True:
            today = datetime.datetime.strftime(
                today,
                "%Y-%m-%d",
            )
        # Return Today
        return today

    ### Getting Yesterday
    async def Get_Yesterday(self, day, output_string):
        # Getting Yesterday
        yesterday = ""
        if using_timezone == True:
            yesterday = day - datetime.timedelta(days=1)
            yesterday = datetime.datetime.combine(
                yesterday, datetime.datetime.min.time()
            ).astimezone(time_zone)
        else:
            yesterday = day - datetime.timedelta(days=1)
            yesterday = datetime.datetime.combine(
                yesterday, datetime.datetime.min.time()
            ).astimezone()
        # Convert to string if output_string is true
        if output_string == True:
            yesterday = datetime.datetime.strftime(
                yesterday,
                "%Y-%m-%d",
            )
        # Return Yesterday
        return yesterday

    ### Get Tomorrow
    async def Get_Tomorrow(self, day, output_string):
        # Getting Tomorrow
        tomorrow = ""
        if using_timezone == True:
            tomorrow = day + datetime.timedelta(days=1)
            tomorrow = datetime.datetime.combine(
                tomorrow, datetime.datetime.min.time()
            ).astimezone(time_zone)
        else:
            tomorrow = day + datetime.timedelta(days=1)
            tomorrow = datetime.datetime.combine(
                tomorrow, datetime.datetime.min.time()
            ).astimezone()
        # Convert to string if output_string is true
        if output_string == True:
            tomorrow = datetime.datetime.strftime(
                tomorrow,
                "%Y-%m-%d",
            )
        # Return Tomorrow
        return tomorrow

    ### Daily Refresh Loop to Check Users and Leaderboard every day at midnight
    @tasks.loop(hours=24)
    async def Daily_Refresh_Loop(self):
        # Run the refresh
        await self.Daily_Refresh()

    ### Daily Refresh
    async def Daily_Refresh(self):
        # Update all users and the leaderboard
        for x in good_days:
            # Update the users stats
            await self.Update_Stats(
                user=str(x), day=await self.Get_Today(output_string=False), update=False
            )
            # Updating the leaderboard
            await self.update_leaderboard(user=x)
        # Update the presence to no one is having a good day :^(
        await self.update_presence(user="")

    ### Convert Timedelta into String
    async def Timedelta_To_String(self, timedelta, include_day):
        # Convert to seconds in int
        time_seconds = int(timedelta.total_seconds())
        # Convert into times with meaning
        elapsed_days, remainder_days = divmod(time_seconds, 86400)
        elapsed_hours, remainder_minutes = divmod(remainder_days, 3600)
        elapsed_minutes, elapsed_seconds = divmod(remainder_minutes, 60)
        # Format into a string
        if include_day == True:
            elapsed_string = str(
                f"{elapsed_days} Days, {elapsed_hours} Hours, {elapsed_minutes} Minutes, and {elapsed_seconds} Seconds"
            )
        else:
            elapsed_string = str(
                f"{elapsed_hours} Hours, {elapsed_minutes} Minutes, and {elapsed_seconds} Seconds"
            )
        # Returning the string
        return elapsed_string

    ### Calculate Time Until Midnight
    async def Time_Until_Midnight(self):
        # Get today
        today = await self.Get_Today(output_string=False)
        # Calculate Timedelta of Time until Midnight
        time_until_midnight = (
            await self.Get_Tomorrow(today, output_string=False) - today
        )
        return time_until_midnight


# Setting the bots intentions
intents = discord.Intents.default()
intents.message_content = True
# Starting and conencting the bot
client = Good_Day_Bot(
    intents=intents,
    activity=discord.Game(name=f"\U0001F62D Nobody Is Having A Good Day \U0001F62D"),
)
client.run(discord_token)
