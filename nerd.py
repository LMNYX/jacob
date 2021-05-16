import requests, json
import re
from bs4 import BeautifulSoup
import discord,asyncio,os, time, urllib
from discord.ext import commands, tasks


def clearhtml(raw_html):
	cleanr = re.compile('<.*?>')
	cleantext = re.sub(cleanr, '', raw_html)
	return cleantext
def replace_all(text, dic):
	for i, j in dic.items():
		text = text.replace(i, j)
	return text

# -- def end

DISCORD_TOKEN = ""
DISCORD_CHANNEL_ID  = 843251174185762837
DISCORD_FOOTBALL_ID = 843286538363732000
NERD_TIMEOUT = 30   # seconds
CHANNEL = None      # Do not edit

# -- config end

def GeneratePages(AMOUNT_TO_GENERATE = 1):
	_r = requests.get(f"https://en.wikipedia.org/w/api.php?format=json&action=query&generator=random&grnnamespace=0&prop=revisions|images&rvprop=content&grnlimit={str(AMOUNT_TO_GENERATE)}").json()

	_pages = _r['query']['pages']

	_returnData = []

	for r in _pages:
		_pageID = _pages[str(r)]['pageid']
		_parsedData = requests.get(f"https://en.wikipedia.org/w/api.php?format=json&action=parse&pageid={_pageID}").json()['parse']
		
		soup = BeautifulSoup(_parsedData['text']['*'], 'html.parser')
		
		_trySoup = soup.find_all("div", {"class":"shortdescription"})

		if len(_trySoup) > 0:
			_shortDesc = _trySoup[0].text
		else:
			_shortDesc = soup.find_all('div', {'class': 'mw-parser-output'})[0].p.text

		_builtData = {
			"id": _pageID,
			"title": _parsedData['title'],
			"shortdesc": "No proper description provided" if _shortDesc == '\n' else replace_all(_shortDesc, {"\n": "", "[1]": ""})
		}
		_returnData.append(_builtData)

	return _returnData

# -- discord

client = commands.Bot(command_prefix='.')
_TEMP_MSG = ""

@client.event
async def on_ready():
	global CHANNEL
	global FOOTBALL_CHANNEL
	print('We have logged in as {0.user}'.format(client))
	CHANNEL = client.get_channel(id=int(DISCORD_CHANNEL_ID))
	FOOTBALL_CHANNEL = client.get_channel(id=int(DISCORD_FOOTBALL_ID))
	await WikiThredia.start()

@tasks.loop(seconds=NERD_TIMEOUT)
async def WikiThredia():
	global CHANNEL
	global FOOTBALL_CHANNEL
	if CHANNEL == None:
		return # Wait until ready

	_data = GeneratePages(1)[0]
	_url = f"""https://en.wikipedia.org/wiki/{urllib.parse.quote(f"{_data['title']}")}"""
	embed=discord.Embed(title=_data['title'], description=_data['shortdesc'], color=0x7592e8)
	embed.set_footer(text="Wikipedia Random Page")
	if("football" in _data['shortdesc']):
		await FOOTBALL_CHANNEL.send(f"<{_url}>", embed=embed)
	else:
		await CHANNEL.send(f"<{_url}>", embed=embed)

client.run(DISCORD_TOKEN)