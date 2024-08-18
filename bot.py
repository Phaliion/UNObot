from ast import main
from re import L
from typing import Optional
import discord
from discord_components import DiscordComponents, Button, ButtonStyle
from discord.ext import commands, tasks
#from discord_slash import SlashCommand
from discord_slash_components_bridge import SlashCommand
from discord_slash.utils.manage_commands import create_choice, create_option
from discord.utils import get
from discord import *
import os, sys, random, time, math
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json, traceback
from PIL import Image

# pid = str(os.getpid())
# f = open(r"C:\Users\raymo\OneDrive\Desktop\coding\Python_Programs\Application\pid.txt", "w")
# f.write(pid)
# f.close()

scopes = [
'https://www.googleapis.com/auth/spreadsheets',
'https://www.googleapis.com/auth/drive'
]
credentials = ServiceAccountCredentials.from_json_keyfile_name(r"D:\coding\bots\UNO\all-discord-bot-data-sheets-ab8b7f753dc2.json", scopes) #access the json key you downloaded earlier 
file = gspread.authorize(credentials) # authenticate the JSON key with gspread
sheet = file.open_by_url("https://docs.google.com/spreadsheets/d/1cj9rm497HNG1EjGvHCFywfJrFryQgFTHiUD0-Bpve2g/edit#gid=0")  #open sheet

client = commands.Bot(command_prefix=".")
client.remove_command('help')
slash = SlashCommand(client, sync_commands=True)
DiscordComponents(client)



def convert_to_str(lis):
    new_f = ""

    for x in range(0,4):
        for i in range(0,len(lis[x])):
            new_f += f"{lis[x][i]},"
        if len(lis[x]) != 0 or x == 3: new_f = new_f[:-1]
        new_f += ";"
    if lis[3] != []: new_f = new_f[:-1]
    return new_f

def convert_to_list(stri):
    new_a = [[],[],[],[]]

    for x in range(0,4):
        d = stri.split(";")[x].split(",")
        
        try:
            new_a[x] = [eval(i) for i in d]
        except:
            new_a[x] = []
    return new_a


def game_update(value, cell):
    sheet.values_update(f'UNO_GAME_DATA!{cell}',
        params={
            'valueInputOption': 'USER_ENTERED'
        },
        body={
            'values': [
                value,
                ]
        }
        )
def game_get(cell):
    try:
        return list(sheet.values_get(range=f"UNO_GAME_DATA!{cell}").values())[2]
    except: 
        return None

def user_update(value, cell):
    sheet.values_update(f'UNO_USER_DATA!{cell}',
        params={
            'valueInputOption': 'USER_ENTERED'
        },
        body={
            'values': [
                value,
                ]
        }
        )
def user_get(cell):
    try:
        return list(sheet.values_get(range=f"UNO_USER_DATA!{cell}").values())[2]
    except: 
        return None

def rows(spread_sheet): 
    try: return len(  list(sheet.values_get(range=f'{spread_sheet}!A3:F10000').values())[2]  ) + 3
    except: return 3




#  19 Red cards – 0 to 9
#  19 Blue cards – 0 to 9
#  19 Green cards – 0 to 9
#  19 Yellow cards – 0 to 9
#  8 Skip cards – two cards of each color                  ID : 10
#  8 Reverse cards – two cards of each color               ID : 11
#  8 Draw cards – two cards of each color                  ID : 12    
#  8 Black cards – 4 wild cards and 4 Wild Draw 4 cards    ID : 13    ID : 14

# [[red],[blue],[green],[yellow]]
all_cards =[[0,1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,10,10,11,11,12,12,13,14],[0,1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,10,10,11,11,12,12,13,14],[0,1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,10,10,11,11,12,12,13,14],[0,1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,10,10,11,11,12,12,13,14]]

@client.event
async def on_ready():
    print("Bot is ready")
    await client.change_presence(status=discord.Status.idle,activity=Game(name=f'UNO | /help'))
    #client.loop.create_task(loop())


async def end_game(ctx):
    row = game_get(cell="A3:A100000")
    try:
        row = row.index([str(ctx.guild.id)]) + 3
    except: pass

    _player_data = game_get(cell=f"G{row}:Z{row}")[0]
    podium = []
    for x in range(0,int(len(_player_data) / 2)):
        _cards = convert_to_list(_player_data[(x * 2) + 1])
        _card_count = 0
        for l in range(0,4):
            for i in _cards[l]:
                _card_count += 1

        podium.append({"id":str(_player_data[x * 2]), "cards":_card_count})

    podium = sorted(podium, key=lambda i: i['cards'])

    first = await client.fetch_user(int(list(podium[0].items())[0][-1]))
    first_cards = int(list(podium[0].items())[1][-1])
    second = await client.fetch_user(int(list(podium[1].items())[0][-1]))
    second_cards = int(list(podium[1].items())[1][-1])
    try:
        third = await client.fetch_user(int(list(podium[2].items())[0][-1]))
        third_cards = int(list(podium[2].items())[1][-1])
    except: pass

    embed = discord.Embed(title=" ⠀⠀⠀⠀⠀------ Podium ------ ")
    embed.add_field(name="⠀", value="⠀", inline=True)
    embed.add_field(name=f"{first.name} :first_place:", value=f"**{int(first_cards) - 1}** cards left.", inline=True)
    embed.add_field(name="⠀", value="⠀", inline=True)
    embed.add_field(name=f"{second.name} :second_place:", value=f"**{second_cards}** cards left.", inline=True)
    embed.add_field(name="⠀", value="⠀", inline=True)
    try:
        embed.add_field(name=f"{third.name} :third_place:", value=f"**{third_cards}** cards left.", inline=True)
    except: 
        embed.add_field(name="⠀", value="⠀", inline=True)
        
    await ctx.send(embed=embed)

    sheet.values_clear(f"UNO_GAME_DATA!A{row}:AB{row}")

@slash.slash(name="help", description="Help Command")
async def help(ctx):
    embed = discord.Embed(title="Help", description="*BTW yellow card buttons are grey. They will same \"Yellow 6\". There is no yellow color :(*")
    embed.add_field(name="/create_game <@member> <@member> <@mem...", value="Creates an UNO game. **MAX 10 PLAYERS**")
    embed.add_field(name="/hand", value='Show you your hand.')
    embed.add_field(name="/play", value="Play a card when it's your turn.")
    embed.add_field(name="/uno",value="Use this command when your opponent is at 1 card.")
    embed.add_field(name="/end", value="End the game early.")

    await ctx.send(embed=embed, hidden=True)

@slash.slash(name="end", description="End the game early.")
async def end(ctx):
    row = game_get(cell="A3:A100000")

    try:
        row = row.index([str(ctx.guild.id)]) + 3
    except:
        embed = discord.Embed(title="There is no game in progress.", description="*There is not game in progress in thie server*")
        await ctx.send(embed=embed, hidden=True)
        return

    sheet.values_clear(f"UNO_GAME_DATA!A{row}:AB{row}")

    embed = discord.Embed(title="Game ended.", description="Hope you had fun!")
    await ctx.send(embed=embed)

@slash.slash(name="uno", description="Use this command when yor opponent is on 1 card to make them draw 2 cards.")
async def uno(ctx):
    row = game_get(cell="A3:A100000")

    try:
        row = row.index([str(ctx.guild.id)]) + 3
    except:
        embed = discord.Embed(title="There is no game in progress.", description="*There is not game in progress in thie server*")
        await ctx.send(embed=embed, hidden=True)
        return

    AB = game_get(cell=f"AB{row}")[0][0]
    if AB == "FALSE":
        embed = discord.Embed(title="There are no players at 1 card that have not been \"UNO\"d yet.", description="*Be patient, it might be your time soon*")
        await ctx.send(embed=embed, hidden=True)
        return

    user = await client.fetch_user(int(AB))
    if str(ctx.author.id) == AB:
        embed = discord.Embed(title=f"{user.name} saved themself!", description="*\"/uno\" no longer works*")
        await ctx.send(embed=embed)
    else:
        letter = ["H","J","L","N","P","R","T","V","X","Z"]

        played_card = game_get(cell=f"D{row}")[0][0]
        played_card = [int(played_card.split(",")[0]) , int(played_card.split(",")[1])]

        p = game_get(cell=f"B{row}:C{row}")[0]
        o = convert_to_list(p[1])
        p = convert_to_list(p[0])

        p_clean = []
        o_clean = []
        dont_add = False
        try:
            o[played_card[0]].remove(played_card[1])
        except: dont_add = True
        for x in range(0,4):
            if len(p[x]) != 0:
                p_clean.append(p[x])
            if len(o[x]) != 0:
                if len(o[x]) != 0:
                    o_clean.append(o[x])
        if dont_add == False:
            o[played_card[0]].append(played_card[1])


        p_count = 0
        for x in range(0,len(p_clean)):
            for i in p_clean[x]:
                p_count += 1

        s = 0
        if p_count >= 2:
            s = 2
        elif p_count <= 1:
            s = p_count

        column = game_get(cell=f"A{row}:Z{row}")[0].index(AB) - 6
        column = int(column/2)

        het = game_get(cell=f"{letter[column]}{row}")[0][0]
        set = convert_to_list(het)
        column = letter[column]

        for x in range(0,s):
            random_color = random.randint(0,len(p_clean) - 1)
            random_color = p.index(p_clean[random_color])
            random_card = random.choice(p[random_color])

            del p[random_color][p[random_color].index(random_card)]
            set[random_color].append(random_card)
        game_update(value=[convert_to_str(set)], cell=f"{column}{row}")
        game_update(value=[convert_to_str(p), convert_to_str(o)], cell=f"B{row}")
        game_update(value=["FALSE"], cell=f"AB{row}")

        embed = discord.Embed(title=f"{user.name} did not say \"/uno\" fast enough.", description=f"*2 cards added to {user.name}'s hand*")
        await ctx.send(embed=embed)


@slash.slash(
    name="create_game",
    description="Create a UNO game.",
    options=[
        create_option(
            name="player_1",
            description="Player 1",
            required=True,
            option_type=6,
        ),
        create_option(
            name="player_2",
            description="Player 2",
            required=True,
            option_type=6,
        ),
        create_option(
            name="player_3",
            description="Player 3",
            required=False,
            option_type=6,
        ),
        create_option(
            name="player_4",
            description="Player 4",
            required=False,
            option_type=6,
        ),
        create_option(
            name="player_5",
            description="Player 5",
            required=False,
            option_type=6,
        ),
        create_option(
            name="player_6",
            description="Player 6",
            required=False,
            option_type=6,
        ),
        create_option(
            name="player_7",
            description="Player 7",
            required=False,
            option_type=6,
        ),
        create_option(
            name="player_8",
            description="Player 8",
            required=False,
            option_type=6,
        ),
        create_option(
            name="player_9",
            description="Player 9",
            required=False,
            option_type=6,
        ),
        create_option(
            name="player_10",
            description="Player 10",
            required=False,
            option_type=6,
        ),
    ]
    )
async def create_game(ctx, player_1, player_2, player_3="", player_4="", player_5="", player_6="", player_7="", player_8="", player_9="", player_10=""):
    embed = discord.Embed(title="This might take a bit to set up...", description="This might take up to 30 seconds because GSheets API is slow for no reason...")
    msg = await ctx.send(embed=embed)

    global all_cards
    row = rows("UNO_GAME_DATA")

    players = [player_1, player_2, player_3, player_4, player_5, player_6, player_7, player_8, player_9, player_10]

    res = []

    for x in range(0,10):
        try:
            res.append(players[x].id)
        except: pass

    temp_cards = all_cards
    player_cards = []

    for x in range(0,10):
        cards = [[],[],[],[]]
        try:
            for i in range(0,7):
                rand_color = random.randint(0,3)
                rand_num = random.choice(all_cards[rand_color])
                cards[rand_color].append(rand_num)

            for l in range(0,4):
                for i in cards[l]:
                    try:
                        del temp_cards[l][temp_cards[l].index(i)]
                    except: pass

            player_cards.append(str(res[x]))
            player_cards.append(str(convert_to_str(cards)))

        except: break
    
    ll = 0
    for ii in [str(ctx.guild.id), str(convert_to_str(lis=temp_cards)), ";;;", ";;;", "1", str(len(res))]:
        ll += 1
        player_cards.insert(ll - 1,ii)

    # play first card
    game_update(value=player_cards, cell=f"A{row}")
    game_update(value=["1", "False"], cell=f"AA{row}:AB{row}")

    while True:
        rand_color = random.randint(0,3)
        if len(temp_cards[rand_color]) != 0: break
        if len(temp_cards[0]) == 0 and len(temp_cards[1]) == 0 and len(temp_cards[2]) == 0 and len(temp_cards[3]) == 0: 
            embed = discord.Embed(title="There might be to many players...", description="There are no cards left in the draw pile.")
            await msg.edit(embed=embed)
            return
    
    nums = temp_cards
    rand_num = random.choice([0,1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9])
    del nums[rand_color][nums[rand_color].index(rand_num)]

    current_card = f"{rand_color},{rand_num}"

    game_update(value=[convert_to_str(nums), ";;;", current_card], cell=f"B{row}")


    # finally display the game
    usr = await client.fetch_user(int(res[0]))
    embed = discord.Embed(title="Current card played:", description=f"{usr.name}'s turn.")
    file = discord.File(fr"D:\coding\bots\UNO\{rand_color}\{rand_num}.png", filename="image.png")
    embed.set_thumbnail(url="attachment://image.png")

    await msg.edit(file=file, embed=embed)


@slash.slash(name="hand", description="Show the cards you have.")
async def hand(ctx):
    letter = ["H","J","L","N","P","R","T","V","X","Z"]
    row = game_get(cell="A3:A100000")

    try:
        row = row.index([str(ctx.guild.id)]) + 3
    except:
        embed = discord.Embed(title="There is no game in progress.", description="*There is not game in progress in this server*")
        await ctx.send(embed=embed, hidden=True)
        return

    column = game_get(cell=f"A{row}:Z{row}")[0].index(str(ctx.author.id)) - 6
    
    set = convert_to_list(game_get(cell=f"{letter[int(column / 2)]}{row}")[0][0])

    len_set = len(set[0]) + len(set[1]) + len(set[2]) + len(set[3])
    len_down = 0

    for x in range(1,11):
        if len_set - (10 * x) < 0: 
            len_down = (((x-1) * 10) / 10) + 1
            break
    len_down = int(len_down)

    #resize, first image
    #image1 = image1.resize((426, 240))
    new_image = Image.new('RGB',(860 , 128 * len_down), (0,0,0))

    l = 0
    ll = 0
    for x in range(0,4):
        z = set[x]
        z.sort()
        for i in z:
            if l == 10: 
                l = 0
                ll +=1
            image = Image.open(fr'D:\coding\bots\UNO\{x}\{i}.png')

            new_image.paste(image,(86 * l,128 * ll))

            l += 1

    new_image.save(fr"D:\coding\bots\UNO\finished\{str(ctx.author.id)}.png","PNG")
    #new_image.show()
    embed = discord.Embed(title="Hand")

    player_data = game_get(cell=f"G{row}:Z{row}")[0]

    for x in range(0,int(len(player_data) / 2)):
        ii = int(x * 2)
        user = await client.fetch_user(int(player_data[ii]))
        g = convert_to_list(player_data[ii + 1])
        count = 0
        for iii in range(0,4):
            for iv in g[iii]:
                count += 1
        embed.add_field(name=f"{user.name}", value=f"{count} cards left.", inline=False)

    file = discord.File(fr"D:\coding\bots\UNO\finished\{str(ctx.author.id)}.png", filename="image.png")
    embed.set_thumbnail(url="attachment://image.png")
    await ctx.send(file=file, embed=embed, hidden=True)

@slash.slash(name="play", description="Play a card")
async def play(ctx):
    row = game_get(cell="A3:A100000")

    try:
        row = row.index([str(ctx.guild.id)]) + 3
    except:
        embed = discord.Embed(title="There is no game in progress.", description="*There is not game in progress in thie server*")
        await ctx.send(embed=embed, hidden=True)
        return

    letter = ["H","J","L","N","P","R","T","V","X","Z"]
    column = game_get(cell=f"A{row}:Z{row}")[0].index(str(ctx.author.id)) - 6

    check = game_get(cell=f"E{row}:AA{row}")[0]
    reversed = int(check[-1])
    del check[-1]
    player_turn = int(check[0])
    player_count = int(check[1])

    players = []
    for x in range(2,21): 
        if (x % 2) != 0: continue
        try:
            players.append(check[x])
        except: break

    try:
        if players.index(str(ctx.author.id)) + 1 != player_turn:
            embed = discord.Embed(title="It is not your turn.")
            await ctx.send(embed=embed, hidden=True)
            return
    except:
        embed = discord.Embed(title="You are not in the game.", description="*There is a game in progress, but you are not in it.*")
        await ctx.send(embed=embed, hidden=True)
        return

    played_card = game_get(cell=f"D{row}")[0][0]
    played_card = [int(played_card.split(",")[0]) , int(played_card.split(",")[1])]

    letter = ["H","J","L","N","P","R","T","V","X","Z"]
    column = game_get(cell=f"A{row}:Z{row}")[0].index(str(ctx.author.id)) - 6
    column = int(column/2)

    het = game_get(cell=f"{letter[column]}{row}")[0][0]
    set = convert_to_list(het)
    column = letter[column]

    comps = [[]]

    l = 0
    ll = 0
    lll = 0
    zzz = True
    for x in range(0,4):
        z = set[x]
        z.sort()
        for i in z:
            lll += 1
            if l == 5: 
                l = 0
                ll +=1
                comps.append([])
            zz = i

            if i == 10: zz="Skip"
            elif i == 11: zz="Reverse"
            elif i == 12: zz="Draw 2"
            elif i == 13: zz="Wild"
            elif i == 14: zz="Wild Draw 4"

            if x == 3 and i < 10: zz=f"Yellow {i}"
            elif x == 3 and i >= 10: zz=f"Yellow {zz}"
            
            if x == 0: styl = ButtonStyle.red
            elif x == 1: styl = ButtonStyle.blue
            elif x == 2: styl = ButtonStyle.green
            elif x == 3: styl = ButtonStyle.grey

            if i > 12: styl = ButtonStyle.grey

            if x == played_card[0] or i == played_card[1] or i > 12: zc = False
            else: zc = True
            comps[ll].append(Button(label=f"{zz}", style=styl, custom_id=f"{x}_{i}_{lll}", disabled=zc))
            if zc == False: zzz = False

            l += 1

    p = game_get(cell=f"B{row}:C{row}")[0]
    o = convert_to_list(p[1])
    p = convert_to_list(p[0])

    p_clean = []
    o_clean = []
    dont_add = False
    try:
        o[played_card[0]].remove(played_card[1])
    except: dont_add = True
    for x in range(0,4):
        if len(p[x]) != 0:
            p_clean.append(p[x])
        if len(o[x]) != 0:
            if len(o[x]) != 0:
                o_clean.append(o[x])
    if dont_add == False:
        o[played_card[0]].append(played_card[1])

    if l == 5:  
        ll += 1
        comps.append([])

    d = False
    if (len(p_clean) == 0 and len(o_clean) == 0):
        d = True

    comps[ll].append(Button(label=f"Draw a card", style=ButtonStyle.grey, custom_id=f"draw", disabled=d))

    if l == 5:  
        ll += 1
        comps.append([])

    if len(p_clean) == 0 and len(o_clean) == 0 and zzz == True:
        comps[ll].append(Button(label=f"Skip", style=ButtonStyle.grey, custom_id=f"skip", disabled=False))

    embed = discord.Embed(title="Play one of these cards.",description="Click a button ")

    try:
        comps.remove([])
    except: pass
    try:
        await ctx.send(
            content=" ",
            embed=embed,
            components = comps,
            hidden = True,
        )
    except:
        embed = discord.Embed(title="Command failed...", description="Use\"/play\" again, it was just an error.")
        await ctx.send(embed=embed, hidden=True)
        return

    interaction = await client.wait_for("button_click", check = lambda a: (
        a.custom_id != "")
    )
    clicked = interaction.component_id
    try:
        clicked_card = [int(clicked.split("_")[0]) , int(clicked.split("_")[1])]
    except: clicked_card = clicked

    if len(p_clean) == 0 and len(o_clean) == 0:
        pass

    elif len(p_clean) == 0:
        for iii in range(0,4):
            for iiii in o[iii]:
                try:
                    if iii == clicked_card[0] and iiii == clicked_card[1]:
                        continue
                except: pass
                if iii == played_card[0] and iiii == played_card[1] and clicked_card == "draw":
                    continue
                
                p[iii].append(iiii)
        o = [[],[],[],[]]
        if clicked_card == "draw":
            o[played_card[0]].append(played_card[1])
        else:
            o[clicked_card[0]].append(clicked_card[1])

    p_clean = []
    o_clean = []
    for x in range(0,4):
        if len(p[x]) != 0:
            p_clean.append(p[x])
        if len(o[x]) != 0:
            o_clean.append(o[x])

    user_before = await client.fetch_user(players[player_turn - 1])


    clicked_label = ""
    if clicked_card == "draw": 
        random_color = random.randint(0,len(p_clean) - 1)
        random_color = p.index(p_clean[random_color])
        random_card = random.choice(p[random_color])
        del p[random_color][p[random_color].index(random_card)]
        set[random_color].append(random_card)

        player_turn+=reversed
        if player_turn > player_count: player_turn = 1
        if player_turn < 1: player_turn = player_count

        game_update(value=[convert_to_str(p), convert_to_str(o)], cell=f"B{row}:C{row}")
        game_update(value=[str(player_turn)], cell=f"E{row}")
        game_update(value=[convert_to_str(set)], cell=f"{column}{row}")

        embed = discord.Embed(title="Card drew.")
        file = discord.File(fr"D:\coding\bots\UNO\{random_color}\{random_card}.png", filename="image.png")
        embed.set_thumbnail(url="attachment://image.png")
        await ctx.send(file=file, embed=embed, hidden=True)

        usr = await client.fetch_user(players[player_turn - 1])
        embed = discord.Embed(title="Card Played.", description=f"{usr.name}'s turn\n**{user_before.name} drew a card**")
        file = discord.File(fr"D:\coding\bots\UNO\{played_card[0]}\{played_card[1]}.png", filename="image.png")
        embed.set_thumbnail(url="attachment://image.png")
        await ctx.send(file=file, embed=embed, hidden=False)

        return

    elif clicked_card == "skip":
        embed = discord.Embed(title="Skipped playing.")
        await ctx.send(embed=embed, hidden=True)

        player_turn+=reversed
        if player_turn > player_count: player_turn = 1
        if player_turn < 1: player_turn = player_count

        game_update(value=[str(player_turn)], cell=f"E{row}")

        usr = await client.fetch_user(players[player_turn - 1])
        embed = discord.Embed(title="Card Played.", description=f"{usr.name}'s turn\n**{user_before.name} could not play, and there were no cards in the draw pile. {user_before.name} skipped their turn.**")
        file = discord.File(fr"D:\coding\bots\UNO\{played_card[0]}\{played_card[1]}.png", filename="image.png")
        embed.set_thumbnail(url="attachment://image.png")
        await ctx.send(file=file, embed=embed, hidden=False)

        return

    else:
        color = clicked_card[0]
        card = clicked_card[1]
        set[color].remove(card)

        if int(card) == 11:
            reversed = reversed * -1
        
        for x in range(0,2):
            player_turn+=reversed
            if player_turn > player_count: player_turn = 1
            if player_turn < 1: player_turn = player_count

            if int(card) != 10: break

        if int(card) == 12:
            p_count = 0
            for x in range(0,len(p_clean)):
                for i in p_clean[x]:
                    p_count += 1

            s = 0
            if p_count >= 2:
                s = 2
            elif p_count <= 1:
                s = p_count

            het = game_get(cell=f"{letter[player_turn - 1]}{row}")[0][0]
            set2 = convert_to_list(het)

            for x in range(0,s):
                random_color = random.randint(0,len(p_clean) - 1)
                random_color = p.index(p_clean[random_color])
                random_card = random.choice(p[random_color])
                del p[random_color][p[random_color].index(random_card)]
                set2[random_color].append(random_card)
            
            game_update(value=[convert_to_str(set2)], cell=f"{letter[player_turn - 1]}{row}")
        
        async def wild(ctx):
            global color

            embed = discord.Embed(title="Choose a color to switch to.")
            await ctx.send(
                content="",
                embed=embed,
                components = [
                    [Button(label=f"Red", style=ButtonStyle.red, custom_id=f"0", disabled=False), Button(label=f"Blue", style=ButtonStyle.blue, custom_id=f"1", disabled=False), Button(label=f"Green", style=ButtonStyle.green, custom_id=f"2", disabled=False), Button(label=f"Yellow", style=ButtonStyle.grey, custom_id=f"3", disabled=False)]
                ],
                hidden = True,
            )

            interaction = await client.wait_for("button_click", check = lambda a: (a.custom_id != ""))

            clicked_color = interaction.component_id
            clicked_label = ""
            if clicked_color == '0': clicked_label = "**Chosen Color: Red**"
            elif clicked_color == '1': clicked_label = "**Chosen Color: Blue**"
            elif clicked_color == '2': clicked_label = "**Chosen Color: Green**"
            elif clicked_color == '3': clicked_label = "**Chosen Color: Yellow**" 

            color = int(clicked_color)

            return clicked_color, clicked_label

        if int(card) == 13:
            clicked_color, clicked_label = await wild(ctx)

        if int(card) == 14:
            p_count = 0
            for x in range(0,len(p_clean)):
                for i in p_clean[x]:
                    p_count += 1

            s = 0
            if p_count >= 4:
                s = 4
            elif p_count <= 3:
                s = p_count

            het = game_get(cell=f"{letter[player_turn - 1]}{row}")[0][0]
            set2 = convert_to_list(het)

            for x in range(0,s):
                random_color = random.randint(0,len(p_clean) - 1)
                random_color = p.index(p_clean[random_color])
                random_card = random.choice(p[random_color])
                del p[random_color][p[random_color].index(random_card)]
                set2[random_color].append(random_card)
            
            game_update(value=[convert_to_str(set2)], cell=f"{letter[player_turn - 1]}{row}")

            clicked_color, clicked_label = await wild(ctx)


        if int(card) == 13 or int(card) == 14:
            o[int(clicked_color)].append(card)
            card_down = f"{clicked_color},{card}"
        else:
            o[color].append(card)
            card_down = f"{color},{card}"


        if convert_to_str(set) == ";;;":
            await end_game(ctx)
            return

        usr = await client.fetch_user(players[player_turn - 1])
        embed = discord.Embed(title="Card Played.", description=f"{usr.name}'s turn\n{clicked_label}")
        file = discord.File(fr"D:\coding\bots\UNO\{color}\{card}.png", filename="image.png")
        embed.set_thumbnail(url="attachment://image.png")
        card_count = 0
        for x in range(0,4):
            for i in set[x]:
                card_count += 1

        if card_count != 1:
            await ctx.send(file=file, embed=embed, hidden=False)
        else:
            embed = discord.Embed(title="Card Played.", description=f"{usr.name}'s turn\n{clicked_label}\n**{user_before.name} is on their last card! Use\"/uno\" to get them to draw 2!**")
            file = discord.File(fr"D:\coding\bots\UNO\{color}\{card}.png", filename="image.png")
            embed.set_thumbnail(url="attachment://image.png")
            await ctx.send(file=file, embed=embed)
            game_update(value=[str(ctx.author.id)], cell=f"AB{row}")

        game_update(value=[convert_to_str(p), convert_to_str(o), card_down, str(player_turn)], cell=f"B{row}:E{row}")
        game_update(value=[convert_to_str(set)], cell=f"{column}{row}")
        game_update(value=[str(reversed)], cell=f"AA{row}")

        return


@slash.slash(name="pid", description="no")
async def pid(ctx):
    print(os.getpid())

client.run("")