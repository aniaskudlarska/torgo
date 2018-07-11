#==============================================
#TORGOBOT II
#author: sympolite
#This is a very cobbled-together version of the robot, which can hopefulyl serve as reference.
#==============================================

import random
import time
import os
import discord
import requests
import numpy
import re
from discord.ext.commands import Bot
from discord import Game
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
from robobrowser import RoboBrowser
from profanity import profanity


torgo = Bot(command_prefix = "$")
os.chdir("wherever/your/bot/is/located")
print("TORGOBOT II")
print("filepath is: " + os.getcwd())
filepath = os.getcwd()
help_prompt = """
COMMANDS:
Commands follow the format `$command <parameters>` (without angle brackets).

`$commands` - displays a list of commands

`$darktube <search terms>` - links the newest youtube video matching the criteria

`$deviantart <search terms>` - links every result from deviantart's Most Popular section

`$askdrpig` - gives you a diagnosis

`$oldenglish <text>` - returns what you say in a Blackletter/Fraktur font [DESKTOP ONLY]

`$fullwidth <text>` - returns what you say in a fullwidth font

`$russianroulette` - One in six chance of being banned. [REQUIRES PERMISSIONS]
"""

myself = 'THIS IS THE CLIENT ID'
channel = None
server = None
caller = None
init = False
word_list = ['anus', 'cunt', 'protestant']

@torgo.event
async def on_ready():
    profanity.load_words(wordlist=word_list)
    print('ready')    
        
@torgo.event
async def on_message(message):
    print('message received from ' + message.author.display_name + " in " + message.channel.name)  
    
    global channel
    channel = message.channel
    global server
    server = channel.server
    global caller
    global init
    caller = message.author
    if (init == False and caller.id != myself):
        await torgo.send_message(channel, "I AM TORGO. Type `$commands` to see a list of commands.")
        init = True
    #checks if the name "TORGO" has been said
    if  re.search('torgo', message.content, re.IGNORECASE):  
        await torgo.add_reaction(message, u'\U0001f440') #eyes emoji
    #checks for profanity and sends a cool message
    if profanity.contains_profanity(message.content):
        await torgo.send_typing(channel)
        #create the text from the message
        to_draw = message.content
        print(to_draw)
        #create an image based on the number of chars in the message
        txt = Image.new('RGBA', (35*(len(to_draw)),100), (255,255,255,0))
        fnt = ImageFont.truetype('resources/ModerneFraktur.ttf', 64)
        rend = ImageDraw.Draw(txt)
        rend.text((1,20), to_draw, fill=(200,0,0,255), font=fnt)
        #save, send, and delete
        txt.save('temp/texto.png')
        await torgo.send_file(channel, 'temp/texto.png')
        os.remove(filepath + '/temp/texto.png')
        
    await torgo.process_commands(message)

#NORMAL COMMANDS ========================================================================================================== 

@torgo.command()
async def hello(*args):
    print('hello')
    await torgo.say("Die.")

@torgo.command()
async def commands():
    print('commands')
    await torgo.send_message(caller, help_prompt)

@torgo.command()
async def darktube(arg1, *args):
    print('darktube')
    await torgo.send_typing(channel)
    url = "https://www.youtube.com/results/"
    #get arguments
    arg_string = arg1
    for arg in args:
        arg_string += ("+" + arg)
    payload = {'q': arg_string,'sp':'CAJQFA%253D'}
    #get html
    r = requests.get(url, params = payload)
    data = r.text
    soup = BeautifulSoup(data, "html.parser")
    pretty_data = soup.prettify()
    print(pretty_data + "\n\n\n\n")
    #sift through html
    test = soup.find('a',rel="spf-prefetch")
    if test is None:
        await torgo.say("I found no results.")
    else:
        full_link = "https://youtube.com/" + test.get('href')
        await torgo.say("For your viewing pleasure..." + "\n" + full_link)

@torgo.command()
async def deviantart(arg1, *args):
    resultFound = False
    print('deviantart')
    await torgo.send_typing(channel)
    url = "https://www.deviantart.com/popular-1-month/"
    #get arguments
    arg_string = arg1
    for arg in args:
        arg_string += ("+" + arg)
    payload = {'q': arg_string}
    #get html
    r = requests.get(url, params = payload)
    data = r.text
    soup = BeautifulSoup(data, "html.parser")
    pretty_data = soup.prettify()
    print(pretty_data + "\n\n\n\n")
    #sift through html
    for link in soup.find_all('span',class_="thumb wide"):
        if link is None:
            pass
        else:
            await torgo.say("For your viewing pleasure...\n" + link.get('data-super-full-img'))
            print(link.get('data-super-full-img'))
            resultFound = True
            break
    if (resultFound == False):
        await torgo.say("I found no results.")

@torgo.command()
async def askdrpig():
    print('askdrpig')
    await torgo.send_typing(channel)
    diseases = open("resources/disease_list.txt","r")
    diseaselist =  diseases.readlines()
    disease = diseaselist[random.randint(1,247)]
    #247 is the number of lines - this should be changed so that the number of lines
    #is given when reading the file

    base = Image.open('resources/dr_pig.jpg').convert('RGBA')
    copy_base = base.copy() #preventing an overwrite of the base
    
    txt = Image.new('RGBA', (720,720), (255,255,255,0))
    fnt = ImageFont.truetype('resources/arial.ttf', 44)
    rend = ImageDraw.Draw(txt)
    rend.text((20,530), "I diagnose you with " + disease, fill=(255,255,255,255), font=fnt)
    
    out = Image.alpha_composite(copy_base, txt)
    out.save('temp/drpigsays.png')
    await torgo.send_file(channel, 'temp/drpigsays.png')
    time.sleep(1)
    os.remove(filepath + '/temp/drpigsays.png')

@torgo.command()
#prints out the given text in blackletter/fraktur unicode chars
async def oldenglish(arg1, *args):
    print('oldenglish')
    await torgo.send_typing(channel)
    query = arg1
    for arg in args:
        query += ("+" + arg)
    print(query)
    browser = RoboBrowser()
    browser.open('http://qaz.wtf/u/convert.cgi?text=' + query)
    cells = browser.find_all('td')
    content = cells[9].text.strip()
    print(content)
    await torgo.say(str(content))

@torgo.command()
#prints out the given text in fullwidth unicode chars
#(i.e. The roman characters used often in Japanese text.) 
async def fullwidth(arg1, *args):
    print('fullwidth')
    await torgo.send_typing(channel)
    query = arg1
    for arg in args:
        query += ("+" + arg)
    print(query)
    browser = RoboBrowser()
    browser.open('http://qaz.wtf/u/convert.cgi?text=' + query)
    cells = browser.find_all('td')
    content = cells[5].text.strip()
    print(content)
    await torgo.say(str(content))

@torgo.command()
async def russianroulette():
    chance = random.randint(1,6)
    if (chance == 6):
        try:
            await torgo.ban(caller,delete_message_days=0)
            await torgo.say("BANG. You have been banned.")
        except:
            await torgo.say("Had it not been for the permissions restricting me, I would have banned you.")
    else:
        await torgo.say("Click.")

torgo.run("TOKEN HERE")

