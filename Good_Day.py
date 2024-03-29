#!/usr/bin/env python3
# region Import Modules
import discord
from discord.ext import tasks, commands
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
# Load environment variables
load_dotenv()
discord_token = str(os.getenv("DISCORD_TOKEN"))
time_zone_string = str(os.getenv("TIME_ZONE"))
time_zone = ""  # Used for storing the timezone
start_time = ""  # Used for storing the start time to calculate uptime
# If using a specifed timezone
if time_zone_string != "":
    # Setting the time zone to the one from the env file
    time_zone = zoneinfo.ZoneInfo(time_zone_string)
else:
    # Setting the time zone to be the local time zone
    time_zone = datetime.datetime.now().astimezone().tzinfo
# Get start time using the selected time zone
start_time = datetime.datetime.today().astimezone(time_zone)
# Make directory if it doesn't exist
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
class Good_Day_Bot(commands.Bot):

    ### Init to use commands inside the class
    def __init__(self, command_prefix, intents, activity):
        commands.Bot.__init__(
            self,
            command_prefix=command_prefix,
            intents=intents,
            activity=activity,
        )
        # Activate the commands
        self.add_commands()

    # When the bot connects to Discord
    async def on_ready(self):
        # Printing a log message
        print(f"{self.user.name} Bot: connected to the server")
        # Starting with a Daily Refresh
        await self.Daily_Refresh()
        # Waiting until midnight tomorrow to start the loop (if it isn't already running somehow)
        if not self.Daily_Refresh_Loop.is_running():
            # Getting time until midnight
            time_until_midnight = await self.Time_Until_Midnight()
            # Waiting until midnight
            await asyncio.sleep(time_until_midnight.total_seconds())
            # Start a refresh loop
            await self.Daily_Refresh_Loop.start()

    ### When someone sends a message in the server
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
            # If the user says "good day" in their message
            if "good day" in str(message.content).lower():
                # Update the activity for the user having a good day, even if they already did it today
                await self.update_presence(user=message.author.name)
                # Update the data on their good day status
                today = await self.Get_Today(output_string=False)
                await self.Check_User_Days(user=str(message.author.id), day=today)
        # Have to add this for on_message to work with commands
        await self.process_commands(message)

    ### Implementing Commands
    def add_commands(self):
        # Add the command for getting the days
        @self.command(name="days", help="Get's the amount of days a user has had.")
        async def days(ctx):
            # Variable for the user to check
            user = ""
            # Check player names stats
            if len(ctx.message.content) == 5:
                # If the string is only "!days" get themselves
                user = str(ctx.author.id)
            else:
                # If the string has more attempt to get the mention
                split_message = str(ctx.message.content).split(
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
                await ctx.channel.send(
                    f"\U0001F913 <@{user}> has the following: \U0001F913\
                                \n\U0001F975 They've had {day_number} Good Days! \U0001F975\
                                \n\U0001F92F Their Last Good Day was {last_day}! \U0001F92F\
                                \n\U0001F973 Their Top Streak was {top_streak}! \U0001F973\
                                \n\U0001F60E Their Current Streak is {current_streak}! \U0001F60E"
                )
            else:
                # Send message that they've never had a good day :(
                await ctx.channel.send(
                    "\U0001F62D I'm so sorry. They have never had a good day \U0001F62D"
                )

        # Add the command for leaderboard
        @self.command(name="leaderboard", help="Get's the leaderboard.")
        async def leaderboard(ctx):
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
            message_text += f"\n-------------------------------------------------"
            # Send message
            await ctx.message.channel.send(message_text)

        # Add the command to get the uptime
        @self.command(name="uptime", help="Get's the uptime of the server.")
        async def uptime(ctx):
            # Calculate Timedelta of Time from Start
            uptime_delta = await self.Get_Today(output_string=False) - start_time
            # Convert into string
            elapsed = await self.Timedelta_To_String(
                timedelta=uptime_delta, include_day=True
            )
            await ctx.message.channel.send(
                f"\U0001F607 I have been tracking Good Days for {elapsed}! \U0001F607"
            )

        # Add the command to get the time
        @self.command(name="time", help="Get's the time of the server.")
        async def time(ctx):
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
            await ctx.message.channel.send(output)

        # Add the custom help command
        @self.command(name="help+", help="Get's more help information.")
        async def help_(ctx):
            # Gives instructions
            await ctx.message.channel.send(
                'Do "!days" to see your stats.\nDo "!days @user" to see their stats.\nDo "!leaderboard" to see the leaderboard.\nDo "!uptime" to see how long the bot has been running.\
                            \nDo "!time" to see times.\nDo "!debug" to see debug information.\nDo "!help" to see commands.\nDo "!help+" for more in-depth command information.\nRemember to say "Good Day!"',
            )

        # Add the debug command
        @self.command(name="debug", help="Debug information.")
        async def debug(ctx):
            # Get debug information
            server_debug = f"{ctx.message.guild}\n{ctx.message.guild.id}"
            channel_debug = f"{ctx.message.channel}\n{ctx.message.channel.id}"
            user_debug = f"{ctx.message.author}\n{ctx.message.author.id}"
            message_debug = f"{ctx.message.content}"
            mention_debug = f"{ctx.message.mentions}"
            # Make a string to return
            print_string = (
                f"===============\nDebug\n===============\n"
                f"Server\n---------------\n{server_debug}\n"
                f"===============\nChannel\n---------------\n{channel_debug}\n"
                f"===============\nUser\n---------------\n{user_debug}\n"
                f"===============\nMessage\n---------------\n{message_debug}\n"
                f"===============\nMentions\n---------------\n{mention_debug}\n==============="
            )
            # Gives instructions
            await ctx.message.channel.send(print_string)

    ### Updates who is having a good day
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

    ### Checking Dictionary
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
            # If today hasn't already been counted as a good day (could maybe use just the last value [-1])
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
                # Increasing the streak
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

    ### Check for an update leaderboard scores
    async def Check_Scores(self, user, user_stats, place, activity, mode):
        # Have to have leader_board be global
        global leader_board
        # If first place
        if place == "First":
            # If breaking your own score
            if mode == "Own":
                # Replace yourself in first place
                leader_board[activity]["First Place"] = {
                    "User": user,
                    activity: user_stats[activity],
                }
            # If breaking someone else's score
            elif mode == "Other":
                # Move second place to third
                leader_board[activity]["Third Place"] = leader_board[activity][
                    "Second Place"
                ]
                # Move first place to second
                leader_board[activity]["Second Place"] = leader_board[activity][
                    "First Place"
                ]
                # Move to to first place
                leader_board[activity]["First Place"] = {
                    "User": user,
                    activity: user_stats[activity],
                }
            # If you lost your own score
            elif mode == "Lost":
                # Move second place to first
                leader_board[activity]["First Place"] = leader_board[activity][
                    "Second Place"
                ]
                # Move third place to second place
                leader_board[activity]["Second Place"] = leader_board[activity][
                    "Third Place"
                ]
                # Get a new third place
                await self.Check_Scores("N/A", "N/A", "New Third", activity, "N/A")
        elif place == "Second":
            # If breaking your own score
            if mode == "Own":
                # Replace yourself in second place
                leader_board[activity]["Second Place"] = {
                    "User": user,
                    activity: user_stats[activity],
                }
            # If breaking someone else's score
            elif mode == "Other":
                # Move second place to third
                leader_board[activity]["Third Place"] = leader_board[activity][
                    "Second Place"
                ]
                # Move to to second place
                leader_board[activity]["Second Place"] = {
                    "User": user,
                    activity: user_stats[activity],
                }
            # If you lost your own score
            elif mode == "Lost":
                # Move third place to second place
                leader_board[activity]["Second Place"] = leader_board[activity][
                    "Third Place"
                ]
                # Get a new third place
                await self.Check_Scores("N/A", "N/A", "New Third", activity, "N/A")
        elif place == "Third":
            # If breaking your own score
            if mode == "Own":
                # Replace yourself in third place
                leader_board[activity]["Third Place"] = {
                    "User": user,
                    activity: user_stats[activity],
                }
            # If breaking someone else's score
            elif mode == "Other":
                # Move to to third place
                leader_board[activity]["Third Place"] = {
                    "User": user,
                    activity: user_stats[activity],
                }
            # If you lost your own score
            elif mode == "Lost":
                # Get a new third place
                await self.Check_Scores("N/A", "N/A", "New Third", activity, "N/A")
        elif place == "New Third":
            # Set third place to empty to start
            leader_board[activity]["Third Place"] = {
                "User": "Empty",
                activity: "0",
            }
            # Look through every user
            for z in good_days:
                # If z (current user) isn't on the score board
                if (
                    leader_board[activity]["Second Place"]["User"] != z
                    and leader_board[activity]["First Place"]["User"] != z
                ):
                    # Getting their score
                    good_day_stats = {
                        "Good Days": int(good_days[z]["Stats"]["Good Days"]),
                        "Top Streak": int(good_days[z]["Streaks"]["Top Streak"]),
                        "Current Streak": int(
                            good_days[z]["Streaks"]["Current Streak"]
                        ),
                    }
                    # If it is larger than the current third palce
                    if good_day_stats[activity] > int(
                        leader_board[activity]["Third Place"][activity]
                    ):
                        leader_board[activity]["Third Place"] = {
                            "User": z,
                            activity: good_day_stats[activity],
                        }

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
            # initialize the leaderboard if there are users in the list if not then leave as is
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
            # Getting the user scores
            user_stats = {
                "Good Days": int(good_days[user]["Stats"]["Good Days"]),
                "Top Streak": int(good_days[user]["Streaks"]["Top Streak"]),
                "Current Streak": int(good_days[user]["Streaks"]["Current Streak"]),
            }
            # Checking leaderboards in each category
            for y in ["Good Days", "Top Streak", "Current Streak"]:
                # region Check for score loss
                # If the user was in first place, but lost their score
                if leader_board[y]["First Place"]["User"] == user:
                    # If there current score is less than the score on the board, remove them
                    if user_stats[y] < int(leader_board[y]["First Place"][y]):
                        await self.Check_Scores("N/A", "N/A", "First", y, "Lost")
                # If the user was in second place, but lost their score
                if leader_board[y]["Second Place"]["User"] == user:
                    # If there current score is less than the score on the board, remove them
                    if user_stats[y] < int(leader_board[y]["Second Place"][y]):
                        await self.Check_Scores("N/A", "N/A", "Second", y, "Lost")
                # If the user was in third place, but lost their score
                if leader_board[y]["Third Place"]["User"] == user:
                    # If there current score is less than the score on the board, remove them
                    if user_stats[y] < int(leader_board[y]["Third Place"][y]):
                        await self.Check_Scores("N/A", "N/A", "Third", y, "Lost")
                # endregion Check for score loss
                # region Update scores
                # If the user stats are more than or equal to the first place
                if user_stats[y] >= int(leader_board[y]["First Place"][y]):
                    # If the current user is already in first place
                    if leader_board[y]["First Place"]["User"] == user:
                        await self.Check_Scores(user, user_stats, "First", y, "Own")
                    # If if isn't the user is the score larger than first place
                    elif user_stats[y] > int(leader_board[y]["First Place"][y]):
                        await self.Check_Scores(user, user_stats, "First", y, "Other")
                # If the user stats are more than the second place, but not first place
                elif user_stats[y] >= int(leader_board[y]["Second Place"][y]):
                    # If the current user is already in second place
                    if leader_board[y]["Second Place"]["User"] == user:
                        await self.Check_Scores(user, user_stats, "Second", y, "Own")
                    # If if isn't the user is the score larger than second place
                    elif user_stats[y] > int(leader_board[y]["Second Place"][y]):
                        await self.Check_Scores(user, user_stats, "Second", y, "Other")
                # If the user stats are more than the third place, but not second place
                elif user_stats[y] >= int(leader_board[y]["Third Place"][y]):
                    # If the current user is already in third place
                    if leader_board[y]["Third Place"]["User"] == user:
                        await self.Check_Scores(user, user_stats, "Third", y, "Own")
                    # If if isn't the user is the score larger than third place
                    elif user_stats[y] > int(leader_board[y]["Third Place"][y]):
                        await self.Check_Scores(user, user_stats, "Third", y, "Other")
                # endregion Update scores
        # Save to json
        with open(leaderboard_file_path, "w") as outputfile:
            json.dump(leader_board, outputfile, sort_keys=False, indent=4)

    ### Getting Today
    async def Get_Today(self, output_string):
        # Getting Today's Time
        today = datetime.datetime.today().astimezone(time_zone)
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
        yesterday = day - datetime.timedelta(days=1)
        yesterday = datetime.datetime.combine(
            yesterday, datetime.datetime.min.time(), tzinfo=time_zone
        )
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
        tomorrow = day + datetime.timedelta(days=1)
        tomorrow = datetime.datetime.combine(
            tomorrow.date(), datetime.datetime.min.time(), tzinfo=time_zone
        )
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
# Starting and connecting the bot
client = Good_Day_Bot(
    command_prefix="!",
    intents=intents,
    activity=discord.Game(name=f"\U0001F62D Nobody Is Having A Good Day \U0001F62D"),
)

client.run(discord_token)
