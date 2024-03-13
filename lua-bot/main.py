import os
import json
import math
import random  
import discord
import jobs
import requests
from keep_alive import keep_alive
from discord.ext import commands, tasks

intents = discord.Intents.default()  # Create an instance of intents
intents.message_content = True

bot = commands.Bot(  
  command_prefix="!",  # Change to desired prefix
  case_insensitive=True,  # Commands aren't case-sensitive
  intents=intents  # Pass the intents object
)

# log_file = open("log.txt", "a")

bot.author_id = 614569655813799948  # Change to your discord id!!!

launches_file = open("launches.txt", "r")
launches_count = int(launches_file.read())  
launches_file.close()
launches_file = open("launches.txt", "w")
launches_file.write(str(launches_count + 1))
launches_file.close()

coins_data = {}
items_data = {}
jobs_data = {}
levels_data = {}
guilds_data = {}
with open("coins_save.json", 'r') as json_file:  
  coins_data = json.load(json_file)
with open("items_save.json", 'r') as json_file:  
  items_data = json.load(json_file)
with open("jobs_save.json", 'r') as json_file:  
  jobs_data = json.load(json_file)
with open("levels_save.json", 'r') as json_file:  
  levels_data = json.load(json_file)
with open("guilds_save.json", 'r') as json_file:  
  guilds_data = json.load(json_file)
  # 0: prefix
  # 1: list of blocked channels

mins_passed = 0

shop_items = {
  "gold_bar": 100,
  "case": 50
}

collectable_items = {
  "gold_bar",
  "knife",
  "prestige_medal"
}

crafting_ingredients = {
  "special_coin",
  "candy",
  "invar",
  "ethanol",
  "paperclip",
  "crude_mechanism",
  "complex_mechanism"
}

items_info = {
  "gold_bar": "A stable and long term investment.\nTurns into 100 coins when used",
  "case": "Gives random items when used",
  "knife": "Definitely not for stealing",
  "special_coin": "Very special coin made of nickel.\nTurns into 10 coins when used",
  "candy": "Ordinary candy",
  "paperclip": "For people who like collecting paperclips",
  "invar": "a nickel-iron alloy with notable thermal properties",
  "ethanol": "a steady source of fuel",
  "crude_mechanism": "a building block for simple machinery",
  "complex_mechanism": "a robust framework for complex machinery",
  "prestige_medal": "a medal that is only obtainable through prestiging"
}

crafts_list = {
  "invar": [["paperclip", 4], ["special_coin", 1]],
  "ethanol": [["candy", 5]],
  "crude_mechanism": [["invar", 3], ["ethanol", 1]]
}

jobs_list = {
  "developer": "evaluate boolean expressions",
  "statistician": "find the smallest number in a list",
  "burglar": "steal things from people"
}

prestige_emojis = {
  0: "<:prestige0:1124741922288844890>",
  1: "<:prestige1:1124808530147430401>",
  2: "<:prestige2:1124738362633367562>"
}
    
moon_phase_counter = 0
moon_phases = "🌕🌖🌗🌘🌑🌒🌓🌔"

def give_item(user_id, item, count):
  global items_data
  if item in items_data[user_id]:
    items_data[user_id][item] += count
  else:
    items_data[user_id][item] = count

def get_item(user_id, item):
  global items_data
  if not user_id in items_data:
    return 0
  if item in items_data[user_id]:
    return items_data[user_id][item]
  return 0

def calculate_levels(y, pres):
  # if y > 5:
  #   return ((0.8 ** (pres)) * math.pow((y**2 / 225) - (2*y / 45) + (1 / 9), 1/3)) * 1.656
  # else:
  #   return 0
  
  if y > 5:
    return math.sqrt(y-5) * (0.9 ** pres)
  else:
    return y/5

def calculate_messages(x, pres):
  return x*x/(0.9**(2*pres)) + 5

def progress(a, b): # returns a progress bar
  if a >= b:
    return "`[##########]`"
  buf = "`["
  x = b/10
  rem = 0
  while a > 0:
      a -= x
      buf += "#"
      rem += 1
  buf += (10 - rem) * "-" + "]`"
  return buf

def get_prestige_emoji(pres):
  if pres in prestige_emojis:
    return prestige_emojis[pres]
  return f"[{pres}]"

@tasks.loop(seconds=60)  # Update the presence every 10 seconds
async def update_presence():
  global moon_phase_counter
  moon_phase_counter += 1
  presence = discord.Game(name=f'{moon_phases[moon_phase_counter%8]}', type=discord.ActivityType.playing)
  await bot.change_presence(activity=presence)

@tasks.loop(seconds=60)  # Dumps the saves
async def dump_saves():
  with open("coins_save.json", 'w') as json_file:
    json.dump(coins_data, json_file)
  with open("items_save.json", 'w') as json_file:
    json.dump(items_data, json_file)
  with open("jobs_save.json", 'w') as json_file:
    json.dump(jobs_data, json_file)
  with open("levels_save.json", 'w') as json_file:
    json.dump(levels_data, json_file)
  with open("guilds_save.json", 'w') as json_file:
    json.dump(guilds_data, json_file)


@tasks.loop(seconds=60)
async def reset_xp_cooldown():
  global mins_passed
  mins_passed += 1

@bot.event
async def on_ready():
  # activity = discord.Game(name="Moon")
  # await bot.change_presence(activity=activity)    
  update_presence.start()
  reset_xp_cooldown.start()
  dump_saves.start()
  channel = bot.get_channel(1077737500962988055)
  await channel.send(f'Logged in as {bot.user.name}, Launch #{launches_count}')
  print(f"Launch #{launches_count}")

@bot.event
async def on_guild_join(guild):
  if guild.system_channel is not None:
    await guild.system_channel.send(f"Thanks for adding Lua to {guild}!\nConsider using `!enable`, `!disable`, and `!prefixset` to customise the bot for your server\nMore information can be found on the official website (lua-bot.summer8n2.repl.co)")

@bot.event
async def on_message(message):
  msg = message.content
  channel = message.channel
  user_id = str(message.author.id)
  
  if message.author == bot.user:
    return 
    
  if message.guild == None:
    guild_id = "0"
    # await log_file.write(f"{user_id}\'s DMs: {msg}\n")
    print(f"{message.author}\'s DMs: {msg}")
    # print(f"{message.author.id}\'s DMs : {msg}")
  else:
    guild_id = str(message.guild.id)
    # await log_file.write(f"{guild_id} {user_id}: {msg}\n")
    print(f"{message.guild} #{message.channel} @{message.author}: {msg}")
    # print(f"{message.guild.id} #{message.channel.id} @{message.author.id}: {msg}")
  
  if guild_id not in levels_data:
    levels_data[guild_id] = {}

  if guild_id not in guilds_data:
    guilds_data[guild_id] = ["!", {}]
  
  prefix = guilds_data[guild_id][0]
  if msg[:len(prefix)] == prefix:
    msg = msg[len(prefix):]

  if str(message.channel.id) in guilds_data[guild_id][1] and guilds_data[guild_id][1][str(message.channel.id)] == 1 and not message.author.guild_permissions.administrator:
    return
    
  if message.content == "lua prefix":
    await channel.send(f"The prefix for Lua in {message.guild} is `{prefix}`")

  if not user_id in levels_data[guild_id]:
    levels_data[guild_id][user_id] = [1, mins_passed, 0, 0];
  else:
    if levels_data[guild_id][user_id][1] != mins_passed:
      levels_data[guild_id][user_id][0] += 1;
      levels_data[guild_id][user_id][1] = mins_passed
    else:
      pass
      # print(f"multiple messages in the same minute #{mins_passed}")
  
  if len(msg) > 0 and msg[0] != "!":
    # responses for jobs
    if user_id in jobs_data:
      if jobs_data[user_id][1] != "":
        if jobs_data[user_id][0] == "developer":
          if msg.lower() != jobs_data[user_id][1].lower():
            coins_data[user_id] -= 8
            await channel.send(f"You failed your task and lost 8 coins!\nYou now have {coins_data[user_id]} coin(s)")
          else:
            coins_data[user_id] += 7
            await channel.send(f"You got paid 7 coins for your work\nYou now have {coins_data[user_id]} coin(s)")
        elif jobs_data[user_id][0] == "statistician":
          if msg.lower() != jobs_data[user_id][1].lower():
            coins_data[user_id] -= 5
            await channel.send(f"You failed your task and lost 5 coins!\nYou now have {coins_data[user_id]} coin(s)")
          else:
            coins_data[user_id] += 4
            await channel.send(f"You got paid 4 coins for your work\nYou now have {coins_data[user_id]} coin(s)")
        elif jobs_data[user_id][0] == "burglar":
          sum = 0
          profit = 0
          temp = msg.split()
          for i in range(len(temp)):
            # print(f"is temp[i] a digit? {temp[i].isdigit()}")
            if temp[i].isdigit():
              temp[i] = int(temp[i])
              # print(f"items to steal: {jobs_data[user_id][1][0]}")
              # print(f"associated value: {jobs_data[user_id][1][0][temp[i]]}")
              if temp[i] in jobs_data[user_id][1][0] and jobs_data[user_id][1][0][temp[i]] != -1:
                # print(f"items: {jobs_data[user_id][1][0]}")
                sum += temp[i]
                profit += jobs_data[user_id][1][0][temp[i]]
                jobs_data[user_id][1][0][temp[i]] = -1
              else:
                await channel.send("Item not present in house")
                return
            else:
              await channel.send("Invalid input format")
              return
          if sum > jobs_data[user_id][1][1]:
            k = random.randint(35, 50)
            await channel.send(f"You tried steal items you couldn't carry, and were caught and fined {k} coins")
            coins_data[user_id] -= k
          else:
            await channel.send(f"You successfully burglarised the house, earning {profit} coin(s)")
            coins_data[user_id] += profit
          await channel.send(f"You now have {coins_data[user_id]} coin(s)")
        jobs_data[user_id][1] = "" 

    # coins for messaging
    if user_id in coins_data:
      if random.choice([True, False, False, False, False, False, False, False, False, False]):
        coins_data[user_id] += 1 

    if message.content[:len(prefix)] != prefix:
      return
  
  if msg == "help":
    await channel.send("  Lua - A utility/fun bot by `8n2#1750`\n*Not actually created using Lua (the scripting language)*\nEnter `" + prefix + "commands` to view the list of supported commands")
  
  if msg == "commands":
    await channel.send("""
List of commands
`{arg}`: argument
`*{arg}`: optional argument
`ping`: gets ping
`help`: helpful information
`commands`: gets the list of commands
`whois`: gets user_id
`bin {number}`: converts a base-10 number to binary
`oct {number}`: converts a base-10 number to octal
`hex {number}`: converts a base-10 number fo hexadecimal
`reverse {message}`: reverses a message
`launches`: gets the current # of launches
`claim`: claims 50 coins
`balance *{user}`: gets the user's balance
`coinflip {wager}`: performs a coinflip with wager
`gamble {wager}`: multiplies the wager by (-1:1) and   adds to balance
`pay {user} {amount}`: pays user some amount of coins
`shop`: lists available shop items
`info {itemid}`: gets an item's description
`buy {itemid} *{amount}`: purchases an item
`inventory *{userid}`: view someone's inventory
`use {itemid}`: uses an item
`jobs`: lists all the available jobs
`work *{jobid}`: change jobs or work
`gift {itemid} {userid} *{amount}`: gifts item(s) to a user
`recipes`: lists all available recipes
`craft {itemid} *{amount}`: crafts the specified amount of items
`level *{user_id}`: gets the relevant user's level
`prestige`: gain 1 prestige rank and resets the user's level
`prefixset {new_prefix}`: sets the prefix in a server to new_prefix
`disable {channel}`: disables Lua in the specified channel
`enable {channel}`: enables Lua in the specified channel
    """)
  if msg == "ping":
    await channel.send(f"Latency: {round(bot.latency * 1000, 2)}ms")
    
  if msg == "whois":
     await channel.send(user_id)

  # `!math {expression}`: evaluates an expression
  
  # if msg[:5] == "!math":
  #   try:
  #     if "**" in msg:
  #       await channel.send("Exponents are not supported")
  #     elif len(msg) > 32:
  #       await channel.send("Expression is too long")
  #     else:
  #       await channel.send(eval(msg[5:]))
  #   except Exception as e:
  #     await channel.send(f"{type(e).__name__}: {e}")  
      
  if msg[:3] == "bin":
    try:
      await channel.send(f"`{bin(int(msg[4:]))}`")
    except Exception as e:
      await channel.send(f"{type(e).__name__}: {e}")
      
  if msg[:3] == "oct":
    try:
      await channel.send(f"`{oct(int(msg[4:]))}`")
    except Exception as e:
      await channel.send(f"{type(e).__name__}: {e}")
      
  if msg[:3] == "hex":
    try:
      await channel.send(f"`{hex(int(msg[4:]))}`")
    except Exception as e:
      await channel.send(f"{type(e).__name__}: {e}")
      
  if msg[:7] == "reverse":
    try:
      await channel.send(msg[8:][::-1].strip())
    except Exception as e:
      await channel.send(f"{type(e).__name__}: {e}")
        
  if msg == "launches":
    await channel.send(f"Launch #{launches_count}")
        
  if msg == "claim":
    if user_id in coins_data:
      # if coins_data[user_id] == 0:
      #   coins_data[user_id] += 10
      #   await channel.send(f"You claimed 10 coins. Current balance: {coins_data[user_id]} coin(s).")
      # else:
      await channel.send("You have already claimed your coins")
    else:
      coins_data[user_id] = 50
      await channel.send("You claimed 50 coins. Current balance: 50 coins.")
      
  if msg == "balance" or msg == "bal":
    if not user_id in coins_data or coins_data[user_id] == 0:
      await channel.send(f"You currently have no coins.\nYou can obtain coins from messaging, {prefix}claim, or {prefix}work")
    else:
      await channel.send(f"You have {coins_data[user_id]} coin(s)")
  elif msg[:3] == "bal":
    try: 
      temp = msg.split()
      if temp[1].strip()[:2] == "<@":
        user_id = temp[1].strip()[2:-1]
        if user_id in coins_data:
          user = await bot.fetch_user(int(user_id))
          await channel.send(f"{user.name}\'s balance: {coins_data[user_id]} coin(s)")  
        else:
          await channel.send(f"{user.name} does not have a balance")
      else:
        if temp[1].strip() in coins_data:
          query_user = await bot.fetch_user(int(temp[1].strip()))
          await channel.send(f"{query_user.name}\'s balance: {coins_data[temp[1].strip()]} coin(s)")
        else:
          await channel.send(f"{temp[1].strip()} does not have a balance")
    except Exception as e:
      await channel.send(f"Something went wrong {type(e).__name__}: {e}")
      
  if msg[:8] == "coinflip" or msg[:2] == "cf":
    if not user_id in coins_data or coins_data[user_id] == 0:
      await channel.send(f"You currently have no coins.\nYou can obtain coins from messaging, {prefix}claim, or {prefix}work")
    else:
      if msg[:8] == "coinflip":
        coinflip_amount = msg[8:].strip()
      elif msg[:2] == "cf":
        coinflip_amount = msg[2:].strip()
      if coinflip_amount.isdigit():
        coinflip_amount = int(coinflip_amount)
        if coinflip_amount > coins_data[user_id]:
          await channel.send("Invalid coinflip amount")
        else:
          if random.choice([True, False]):
            await channel.send(f"You gained {coinflip_amount} coin(s)")
            coins_data[user_id] += coinflip_amount
          else:
            await channel.send(f"You lost {coinflip_amount} coin(s)")
            coins_data[user_id] -= coinflip_amount
          await channel.send(f"Current balance: {coins_data[user_id]} coin(s)")
      else:
        await channel.send("Invalid coinflip amount")
      
  if msg[:6] == "gamble":
    if not user_id in coins_data or coins_data[user_id] == 0:
      await channel.send(f"You currently have no coins.\nYou can obtain coins from messaging, {prefix}claim, or {prefix}work")
    else:
      coinflip_amount = msg[7:].strip()
      if coinflip_amount.isdigit():
        coinflip_amount = int(coinflip_amount)
        if coinflip_amount > coins_data[user_id]:
          await channel.send("Invalid gamble amount")
        else:
          multiplier = random.randint(0, 200)
          if math.ceil(coinflip_amount * multiplier / 100 - coinflip_amount) == 0 or math.floor(coinflip_amount * multiplier / 100 - coinflip_amount) == 0:
            await channel.send("You didn't lose or gain any coins")
          elif multiplier > 100:
            await channel.send(f"You gained {math.floor(coinflip_amount * multiplier / 100 - coinflip_amount)} coin(s)")
            coins_data[user_id] += math.floor(coinflip_amount * multiplier / 100) - coinflip_amount
          elif multiplier < 100:
            await channel.send(f"You lost {abs(math.ceil(coinflip_amount * multiplier / 100) - coinflip_amount)} coin(s)")
            coins_data[user_id] += math.ceil(coinflip_amount * multiplier / 100) - coinflip_amount
          await channel.send(f"Current balance: {coins_data[user_id]} coin(s)")
      else:
        await channel.send("Invalid gamble amount")

  if msg[:3] == "pay":
    try:
      if not user_id in coins_data or coins_data[user_id] == 0:
        await channel.send(f"You currently have no coins.\nYou can obtain coins from messaging, {prefix}claim, or {prefix}work")
      else:
        temp = msg.split()
        user_id = user_id
        payment_amount = int(temp[2])
        if temp[1].strip()[:2] == "<@":
          payee_id = str(temp[1].strip()[2:-1])
        else:
          payee_id = str(temp[1].strip())
        if payment_amount <= 0:
          await channel.send("Payment amount must be non-negative")
        elif payment_amount <= coins_data[user_id]:
          if payee_id in coins_data:
            coins_data[payee_id] += payment_amount
          else:
            coins_data[payee_id] = payment_amount
          coins_data[user_id] -= payment_amount
          payee_user = await bot.fetch_user(int(payee_id))
          await channel.send(f"Payment of {payment_amount} coin(s) successful\nYour new balance: {coins_data[user_id]} coins(s)\n{payee_user.name}'s new balance: {coins_data[payee_id]} coins(s)")
        else:
          await channel.send("Insufficient funds")
    except Exception as e:
      await channel.send(f"Payment declined due to {type(e).__name__}: {e}\n")

  if msg[:3] == "say" and user_id == str(bot.author_id): # 8n2 only
    temp = msg.split()
    chnl = bot.get_channel(int(temp[1]))
    await chnl.send(" ".join(temp[2:]))
  
  if msg[:5] == "steal" and user_id == str(bot.author_id): # 8n2 only
    temp = msg.split()
    user_id = user_id
    payment_amount = int(temp[2])
    if temp[1].strip()[:2] == "<@":
      payee_id = str(temp[1].strip()[2:-1])
    else:
      payee_id = str(temp[1].strip())
    coins_data[user_id] += payment_amount
    coins_data[payee_id] -= payment_amount
    await channel.send(f"Stealing of {payment_amount} coin(s) successful")
    await channel.send(f"Your new balance: {coins_data[user_id]} coins(s)")
    await channel.send(f"{payee_id}'s new balance: {coins_data[payee_id]} coins(s)")
  elif msg[:5] == "steal":
    await channel.send("Stealing is prohibited")

  if msg == "shop":
    await channel.send("Buy fancy items with your coins!\nUse `" + prefix + "buy {item} *{amount}` to buy item\nUse `" + prefix + "info {item}` to view item description")
    for key, value in shop_items.items():
        if value == 1:
          await channel.send(f"`{key}`: {value} coin")
        else:
          await channel.send(f"`{key}`: {value} coins")
          
  if msg[:4] == "info":
    temp = msg.split()
    if len(temp) == 1:
      await channel.send("That item doesn't exist, or doesn't have a description")
    else:
      buf = ""
      if temp[1] in items_info:
        buf += f"`{temp[1]}`: "
        if temp[1] in collectable_items:
          buf += "collectable, "
        if temp[1] in crafting_ingredients:
          buf += "crafting ingredient, "
        if temp[1] in crafts_list:
          buf += "craftable, "
        buf = buf[:-2] + f"\n{items_info[temp[1]]}"
        await channel.send(buf)
      else:
        await channel.send("That item doesn't exist")

  if msg[:3] == "buy":
    user_id = user_id
    if user_id not in items_data:
      items_data[user_id] = {}
    try:
      temp = msg[4:].strip().split()
      if temp[0] in shop_items:
        if len(temp) == 2:
          if temp[1].isdigit():
            temp[1] = int(temp[1])
            total_cost = shop_items[temp[0]] * temp[1]
          else:
            await channel.send("Invalid purchase amount")
        else:
          total_cost = shop_items[temp[0]]
          temp.append(1)
        if not user_id in coins_data:
          await channel.send(f"You currently have no coins.\nYou can obtain coins from messaging, {prefix}claim, or {prefix}work")
        elif coins_data[user_id] < total_cost:
          await channel.send("Insufficient funds")
        else:
          give_item(user_id, temp[0], temp[1])
          await channel.send(f"Purchase of {temp[1]}x {temp[0]}(s) successful")
          coins_data[user_id] -= total_cost
      else:
        await channel.send("Requested item not available")
    except Exception as e:
      await channel.send(f"Purchase failed due to {type(  e).__name__}: {e}")

  if msg[:9] == "inventory" or msg[:3] == "inv":
    user_id = user_id
    temp = msg.split()
    if len(temp) == 1:
      query_id = user_id
    else:
      if temp[1].strip()[:2] == "<@":
        query_id = str(temp[1].strip()[2:-1])
      else:
        query_id = str(temp[1].strip())
    if not query_id in items_data:
      await channel.send(f"{query_id} doesn't have any items")
    else:
      query_user = await bot.fetch_user(int(query_id))
      await channel.send(f"{query_user.name}'s inventory")
      buf = ""
      for key, value in items_data[query_id].items():
        if value != 0:
          buf += f"`{key}`: {value}\n"
      await channel.send(buf)
          
  if msg[:3] == "use":
    try:
      temp = msg.split()
      item = temp[1]
      # print("get_item", get_item(user_id, item))
      if get_item(user_id, item) == 0:
        await channel.send("You don't have that item")
      else:
        if item == "gold_bar":
          give_item(user_id, "gold_bar", -1)  
          coins_data[user_id] += 100
          await channel.send(f"You used the gold bar, selling it for 100 coins\nYour new balance: {coins_data[user_id]} coins")
        elif item == "case":
          await channel.send("You opened the case and recieved: ")
          give_item(user_id, "case", -1)
          buf = ""
          for i in range(random.randint(1, 3)):
            temp = random.randint(0, 101)
            if temp > 98:
              buf += "1x `knife`\n"
              give_item(user_id, "knife", 1)
            elif temp > 70:
              buf += "1x `special_coin`\n"
              give_item(user_id, "special_coin", 1)
            elif temp > 40:
              buf += "1x `candy`\n"
              give_item(user_id, "candy", 1)
            else:
              buf += "1x `paperclip`\n"
              give_item(user_id, "paperclip", 1)
          await channel.send(buf)
        elif item == "special_coin":
          give_item(user_id, "special_coin", -1)  
          coins_data[user_id] += 10
          await channel.send(f"You used the special coin, exchanging it for 10 coins\nYour new balance: {coins_data[user_id]} coins")
        else:
          await channel.send("This item is useless")
    except Exception as e:
      await channel.send(f"Something went wrong {type(e).__name__}: {e}")

  if msg == "jobs":
    await channel.send("Available jobs\nUse `" + prefix + "work {jobid}` to claim a job")
    for key, value in jobs_list.items():
      await channel.send(f"`{key}`: {value}")
    
  if msg[:4] == "work":
    try:
      temp = msg.split()
      if len(temp) == 1:
        if user_id in jobs_data:
          if jobs_data[user_id][0] == "developer":
            tup = jobs.generate_expression(2)
            await channel.send("Evalute this boolean expression:")
            await channel.send(tup[0])
            jobs_data[user_id][1] = str(tup[1])
          elif jobs_data[user_id][0] == "statistician":
            tup = jobs.generate_list(20)
            await channel.send(f"Find the smallest number in this list:\n{tup[0]}")
            jobs_data[user_id][1] = str(tup[1])
          elif jobs_data[user_id][0] == "burglar":
            if get_item(user_id, "knife") == 0:
              await channel.send("You must own a knife to be a burglar")
              return
            tup = jobs.generate_items(random.randint(3, 6))
            jobs_data[user_id][1] = tup
            await channel.send(f"You found a house to rob. Listed below are various possessions\nThe items are listed by weight followed by cost in coins:\nYou can pick up a maximum of {tup[1]}kg(s)")
            buf = """"""
            for key, value in tup[0].items():
               buf += f"`{key}`: {value}\n"
            await channel.send(buf)
            await channel.send("Enter the weight(s) of the item(s) that you would like to steal")
          else:
            await channel.send(f"You don't currently have a job.\nUse `{prefix}jobs` to view the available list of jobs.")
      else:
        # print(temp[1])
        if temp[1] in jobs_list:
          if temp[1] == "burglar":
            if get_item(user_id, "knife") >= 1:
              await channel.send("You are now \"working\" as a `burglar`")
              jobs_data[user_id] = [temp[1], ""]
            else:
              await channel.send("You must own a knife to be a burglar")
          else:
            await channel.send(f"You are now working as a `{temp[1]}`")
            jobs_data[user_id] = [temp[1], ""]
        else:
          await channel.send("Invalid job")
    except Exception as e:
      await channel.send(f"Work failed due to {type(e).__name__}: {e}")

  if msg[:4] == "gift":
    # `!gift {itemid} {userid} *{amount}`: gifts item(s) to a user
    # 0: command
    # 1: itemid
    # 2: userid
    # 3: item
    try:
      temp = msg.split()
      item_id = temp[1]
      if len(temp) == 3:
        temp.append("1")
      # print(temp)
      if temp[2].strip()[:2] == "<@":
        giftee_id = str(temp[2].strip()[2:-1])
      else:
        giftee_id = str(temp[2].strip())
      if temp[3].isdigit():
        temp[3] = int(temp[3])
        if get_item(user_id, item_id) < temp[3]:
          # print(get_item(user_id, item_id), temp[3])
          await channel.send("Not enough items")
        else:
          give_item(giftee_id, item_id, temp[3])
          give_item(user_id, item_id, -temp[3])
          giftee = await bot.fetch_user(int(giftee_id))
          await channel.send(f"Successfully gifted {temp[3]}x {item_id}(s) to {giftee.name}\nYou now have {get_item(user_id, item_id)} {item_id}(s)\n{giftee.name} now has {get_item(giftee_id, item_id)} {item_id}(s)")
      else:
        await channel.send("Invalid gifting amount")
    except Exception as e:
      await channel.send(f"Gift failed due to {type(e).__name__}: {e}")
      await channel.send("Proper syntax: `" + prefix + "gift {itemid} {userid} *{amount}`")

  if msg[:5] == "craft":
    try:
      tmp = msg.split()
      item = tmp[1]
      if len(tmp) == 2:
        amt = 1
      else:
        amt = tmp[2]
        if amt.isdigit():
          amt = int(amt)
        else:
          await channel.send("Invalid crafting amount")
          return
      if item in crafts_list:
        ing = crafts_list[item]
        for temp in ing:
          if get_item(user_id, temp[0]) < amt * temp[1]:
            await channel.send(f"You do not have enough items {get_item(user_id, temp[0])}/{amt * temp[1]} `{temp[0]}`")
            return
        for temp in ing:
          give_item(user_id, temp[0], -(amt * temp[1]))
          await channel.send(f"-{amt * temp[1]}x`{temp[0]}`")
        give_item(user_id, item, amt)
        await channel.send(f"Successfully crafted {amt}x`{item}`")
    except Exception as e:
      await channel.send(f"Something went wrong while crafting {type(e).__name__}: {e}")

  if msg == "recipes":
    buf = "Crafting Recipes\n"
    for key, value in crafts_list.items():
      buf += f"`{key}`: {items_info[key]}\ningredients: "
      for temp in value:
        buf += f"{temp[1]}x`{temp[0]}`, "
      buf = buf[:-2] + "\n"
    await channel.send(buf)

  if msg[:5] == "level":
    try:
      temp = msg.split()
      if len(temp) == 1:
        query_id = user_id
      else:
        if temp[1].strip()[:2] == "<@":
          query_id = temp[1].strip()[2:-1]
        else:
          query_id = temp[1].strip()
      query_user = await bot.fetch_user(int(query_id))
      guild_levels_data = levels_data[guild_id]
      if query_id in guild_levels_data:
        lvl = calculate_levels(guild_levels_data[query_id][0], guild_levels_data[query_id][2])
        buff = ""
        buff += f"{query_user.name}\'s level: {math.floor(lvl)} {get_prestige_emoji(levels_data[guild_id][user_id][2])}"
        buf = "`["
        rem = lvl - int(lvl)
        tmp = rem
        num = 10
        while rem > 0:
          rem -= 0.1
          num -= 1
          buf += "#"
        buf += "-" * num + "]`"
        tmp1 = levels_data[guild_id][query_id][0]
        tmp2 = calculate_messages(50, levels_data[guild_id][query_id][2])
        await channel.send(f"{buff}\nProgress towards level {int(lvl) + 1}: {buf} {round(tmp * 100, 2)}%\nProgress towards {get_prestige_emoji(levels_data[guild_id][query_id][2]+1)} {progress(tmp1, tmp2)} {round(tmp1/tmp2*100, 2)}%")
      else:
        await channel.send(f"{query_id} is not leveled, or isn't in this server")
    except Exception as e:
      await channel.send(f"Something went wrong while getting the level {type(e).__name__}: {e}")

  if msg == "prestige":
    try:
      if user_id in levels_data[guild_id]:
        lvl = calculate_levels(levels_data[guild_id][user_id][0], levels_data[guild_id][user_id][2])
        if lvl >= 50:
          await channel.send("Are you sure you want to prestige?\nEnter `" + prefix + "prestige confirm` to confirm")
        else:
          await channel.send(f"You need {50 - math.floor(lvl)} more levels to prestige")
          tmp1 = levels_data[guild_id][user_id][0]
          tmp2 = calculate_messages(50, levels_data[guild_id][user_id][2])
          await channel.send(f"Progress {progress(tmp1, tmp2)} {round(tmp1/tmp2*100, 2)}%")
    except Exception as e:
      await channel.send(f"Something went wrong while prestiging {type(e).__name__}: {e}")
  
  if msg == "prestige confirm":
    try:
      if user_id in levels_data[guild_id]:
        lvl = calculate_levels(levels_data[guild_id][user_id][0], levels_data[guild_id][user_id][2])
        if lvl >= 50:
          levels_data[guild_id][user_id][3] += levels_data[guild_id][user_id][0]
          levels_data[guild_id][user_id][0] = 0
          levels_data[guild_id][user_id][2] += 1
          give_item(user_id, "prestige_medal", 1)
          await channel.send(f"You have reached prestige {get_prestige_emoji(levels_data[guild_id][user_id][2])}\nThe required amount of messages to level up has increased")
        else:
          await channel.send(f"You need {50 - math.floor(lvl)} more levels to prestige")
          tmp1 = levels_data[guild_id][user_id][0]
          tmp2 = calculate_messages(50, levels_data[guild_id][user_id][2])
          await channel.send(f"Progress {progress(tmp1, tmp2)} {round(tmp1/tmp2*100, 2)}%")
    except Exception as e:
      await channel.send(f"Something went wrong while prestiging {type(e).__name__}: {e}")

  if msg[:9] == "prefixset":
    try:
      if message.guild == None:
        await channel.send("The default prefix in DMs is `!` and cannot be changed")
        return
      if not message.author.guild_permissions.administrator:
        await channel.send("Admin permissions are required to edit the prefix")
        return
      temp = msg.split()
      guilds_data[guild_id][0] = temp[1]
      await channel.send(f"Prefix for {message.guild} has been set to {temp[1]}")
    except Exception as e:
      await channel.send(f"Something went wrong while setting the prefix {type(e).__name__}: {e}")

  if msg[:7] == "disable":
    try:
      if not message.author.guild_permissions.administrator:
        await channel.send("Admin permissions are required to enable Lua in a channel")
        return
      temp = msg.split()
      if temp[1][:2] == "<#":
        channel_query = bot.get_channel(int(temp[1][2:-1]))
        chnl_id = temp[1][2:-1]
      else:
        channel_query = bot.get_channel(int(temp[1]))
        chnl_id = temp[1]
      if channel_query:
        if str(channel_query.guild.id) == guild_id:
          guilds_data[guild_id][1][str(chnl_id)] = 1
          await channel.send(f"Lua is now disabled in #{channel_query.name}")
        else:
          await channel.send(f"The channel does not belong to {message.guild}.")
      else:
        await channel.send("Invalid channel ID.")
    except Exception as e:
      await channel.send(f"Something went wrong while enabling the channel {type(e).__name__}: {e}")
      
  if msg[:6] == "enable":
    try:
      if not message.author.guild_permissions.administrator:
        await channel.send("Admin permissions are required to enable Lua in a channel")
        return
      temp = msg.split()
      if temp[1][:2] == "<#":
        channel_query = bot.get_channel(int(temp[1][2:-1]))
        chnl_id = temp[1][2:-1]
      else:
        channel_query = bot.get_channel(int(temp[1]))
        chnl_id = temp[1]
      if channel_query:
        if str(channel_query.guild.id) == guild_id:
          guilds_data[guild_id][1][str(chnl_id)] = 0
          await channel.send(f"Lua is now enabled in #{channel_query.name}")
        else:
          await channel.send(f"The channel does not belong to {message.guild}.")
      else:
        await channel.send("Invalid channel ID.")
    except Exception as e:
      await channel.send(f"Something went wrong while enabling the channel {type(e).__name__}: {e}")

  # print(levels_data)

        
  # await channel.send(message.content)


extensions = [
  'cogs.cog_example'  # Same name as it would be if you were importing it
]

if __name__ == '__main__':  # Ensures this is the file being ran
  for extension in extensions:
    bot.load_extension(extension)  # Loades every extension.  

keep_alive()  # Starts a webserver to be pinged.
token = os.environ.get("BOT_TOKEN") 
bot.run(token)  # Starts the bot