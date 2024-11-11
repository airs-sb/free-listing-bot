# skyblockparser v2.0
## This requires a [Hypixel API Key](https://developer.hypixel.net)

## Installation
Python 3.7 or higher is required.

Run `pip install skyblockparser`.

## An Example bot can be found here:
[Example Bot](https://github.com/noemtdev/skyblockparser-example)

## Usage for Parsing Profiles
In the following example, we use the Profile class to get the stats of each member in a SkyBlock profile.

```py
from skyblockparser.profile import SkyblockParser
import requests

api_key = ""
uuid = "28667672039044989b0019b14a2c34d6" # Refractions UUID

url = f"https://api.hypixel.net/v2/skyblock/profiles?key={api_key}&uuid={uuid}"

response = requests.get(url).json()

player = SkyblockParser(response, uuid, api_key)
print(player.get_profiles()) # ['Apple', 'Tomato', 'Pineapple', 'Zucchini', 'Coconut', 'Pomegranate']
profile = player.select_profile("selected") # Selected Profile of Refraction
await profile.init()
profile.get_items()
# This supports Profile Names too!

print(profile.skill_data)
print(profile.dungeon_data)
print(profile.slayer_data)
# Printing some example data.

profile.inv[0].render().show()
# Item Render
```
## Usage for parsing the Auction House
### As it is:
```py
from skyblockparser.auctionhouse import AuctionHouseParser
import aiohttp
import asyncio	

async def main():
    async with aiohttp.ClientSession as session:
        parser = AuctionHouseParser(session)
        await parser.update_caches()
        await session.close()
        print(await parser.lowest_price("Hyperion"))
        render = await parser.render_lowest_price("Hyperion")
        render.show()

asyncio.run(main())
```

### Usage in an API:
```py
from skyblockparser.auctionhouse import AuctionHouseParser
import aiohttp
import io

from quart import Quart, jsonify, send_file
from discord.ext import tasks
"""
discord is used for loops, can be py-cord or discord.py
or you can use your own method of implementing loops!
"""

class App(Quart):
    def __init__(self):
        super().__init__(__name__)

    @tasks.loop(count=1)
    async def init(self):
        self.session = aiohttp.ClientSession()
        self.parser = AuctionHouseParser(self.session)

    @tasks.loop(minutes=1)
    async def update_caches(self):
        await self.parser.update_caches()


app = App()

@app.before_serving
async def start_tasks():
    app.init.start()
    app.update_caches.start()

@app.route("/whole_cache")
async def whole_cache():
    return jsonify(app.parser.auction_cache)

@app.route("/lowest_price/<item>")
async def lowest_price(item):
    return jsonify(await app.parser.lowest_price(item))

@app.route("/render/lowestprice/<itemName>")
async def render_lowest_price(itemName):

    lowest_price_render = await app.parser.render_lowest_price(itemName)
    image_binary = io.BytesIO()
    lowest_price_render.save(image_binary, format="PNG")
    image_binary.seek(0)
    return await send_file(image_binary, mimetype="image/png")

app.run("0.0.0.0", 3000)

```

## Valid Storage Types:
### Regular:
```
inv 
ender_chest
inv_armor
wardrobe
equipment
personal_vault
backpack_[index starting at 0] (Storage) the index sets the backpack
pets
museum_data
```

### Bags:
```
potion_bag
talisman_bag
fishing_bag
quiver
sacks
```

## Valid Stat Types:
```
skill_data
dungeon_data
slayer_data
mining_data
```

## Profile Data:
```
profile_type
profile_id
general_stats (includes most things that arent listed under the other 3)
bestiary
quests
nether
```

## Networth:
```
networth_data
```

# Note:
- Pets do not support rendering *yet* *unless they are not from the Pet Menu #HypixelAddPetLoreToApi
- If you want to use your own hosted api, or if mine ever goes offline, the code is in the `api` directory
- If the user is not in a profile with the given profile name, it will return the selected one.
### This is in very early stages of development so do expect a few changes!
