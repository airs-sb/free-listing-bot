import gzip
import base64
import struct
import asyncio
import aiohttp
import json
import copy

from .renderer import render
from .exceptions import SkyblockParserException

def TAG_End(b):
    return None, b


def TAG_byte(b):
    return b[0], b[1:]


def TAG_Short(b):
    return struct.unpack('>h', b[:2])[0], b[2:]


def TAG_Short_unsigned(b):
    return struct.unpack('>H', b[:2])[0], b[2:]


def TAG_Int(b):
    return struct.unpack('>i', b[:4])[0], b[4:]


def TAG_Long(b):
    return struct.unpack('>q', b[:8])[0], b[8:]


def TAG_Float(b):
    return struct.unpack('>f', b[:4])[0], b[4:]


def TAG_Double(b):
    return struct.unpack('>d', b[:8])[0], b[8:]


def TAG_Byte_Array(b):
    length, b = TAG_Int(b)
    items = []
    for _ in range(length):
        item, b = TAG_byte(b)
        items.append(item)
    decomp = gzip.decompress(bytes(items))
    return TAG_Compound(decomp)[0]['']['i'], b


def TAG_String(b):
    length, b = TAG_Short_unsigned(b)
    value = b[:length]
    b = b[length:]
    return value, b


def TAG_List(b, use_binary=False):
    tag_type, b = b[0], b[1:]
    length, b = TAG_Int(b)
    values = []
    for _ in range(length):
        if tag_type in (9, 10):
            value, b = tags[tag_type](b, use_binary=use_binary)
        else:
            value, b = tags[tag_type](b)
        values.append(value.decode('utf-8')
                      if isinstance(value, bytes) else value)
    return values, b


def TAG_Compound(b, use_binary=False):
    output = {}
    value = True
    while b:
        tag_type, b = TAG_byte(b)
        if tag_type == 0:
            break
        else:
            tag_name, b = TAG_String(b)
            if tag_type in (9, 10):
                value, b = tags[tag_type](b, use_binary=use_binary)
            else:
                value, b = tags[tag_type](b)
            if not use_binary:
                tag_name = tag_name.decode('utf-8')
            output[tag_name] = value.decode(
                'utf-8') if isinstance(value, bytes) else value
    return output, b


def TAG_Int_Array(b):
    pass


def TAG_Long_Array(b):
    pass


tags = (
    TAG_End,
    TAG_byte,
    TAG_Short,
    TAG_Int,
    TAG_Long,
    TAG_Float,
    TAG_Double,
    TAG_Byte_Array,
    TAG_String,
    TAG_List,
    TAG_Compound,
    TAG_Int_Array,
    TAG_Long_Array,
)


def decode_item(nbt):
    nbt = gzip.decompress(base64.b64decode(nbt))
    data = TAG_Compound(nbt)[0]

    return data


class AuctionHouseParser:
    def __init__(self, session:aiohttp.ClientSession):

        self.session = session
        self.loop = asyncio.get_event_loop()

        self.auction_cache = []
        self.temp = []
        
        self.prices = {}
        self.item_table = {}


    async def get_page_count(self):
        r = await self.session.get("https://api.hypixel.net/skyblock/auctions")
        return (await r.json())["totalPages"]
    
    async def get_page(self, page):
        r = await self.session.get(f'https://api.hypixel.net/skyblock/auctions?page={page}')
        data = await r.json()
        items = []
        
        if not data["success"]:
            return items
        
        for i in data["auctions"]:
            if i.get("bin", False) is False:
                continue 

            try:
                decoded = decode_item(i["item_bytes"])
                self.temp.append({"id": decoded[""]["i"][0]["tag"]["ExtraAttributes"]["id"],
                        "price": i["starting_bid"], 
                        "command": f"/viewauction {i['uuid']}", 
                        "itemName": str(decoded[""]["i"][0]["tag"]["display"]["Name"]).replace("§", "&").replace("Â", ""), 
                        "itemLore": i["item_lore"].replace("§", "&"), 
                        "rarity": i["tier"], 
                        "auctioneer": i["auctioneer"],
                        "cleanName": i["item_name"]})
                
            except:
                continue


    async def cache_all_auctions(self):
        gather = asyncio.gather(
            *[self.get_page(i) for i in range(await self.get_page_count())]
        )
        await gather

        self.auction_cache.clear()
        self.auction_cache = copy.deepcopy(self.temp)

        self.temp.clear()


    async def update_caches(self):
        await self.cache_all_auctions()
        gather = asyncio.gather(
            self.update_item_table(),
            self.update_prices()
        )
        await gather

    async def update_item_table(self):
        r = await self.session.get("https://api.hypixel.net/resources/skyblock/items")
        data = await r.json()
        for item in data["items"]:
            self.item_table[item["name"]] = item["id"]

    async def update_prices(self):
        r = await self.session.get("https://raw.githubusercontent.com/SkyHelperBot/Prices/main/prices.json")
        self.prices = json.loads(await r.text()) # do not ask why it didnt work otherwise

    async def lowest_price(self, itemName):
        item_id = self.item_table.get(itemName, None)
        value = self.prices.get(item_id.lower(), 0)

        if item_id is None:
            raise SkyblockParserException("Item not found")

        lowest_price = None
        data = None

        for item in self.auction_cache:

            if item["id"] != item_id:
                continue

            if lowest_price is None or item["price"] < lowest_price:
                lowest_price = item["price"]
                data = item

        data["value_clean"] = value
            
        return data
    

    async def render_lowest_price(self, itemName):

        item_id = self.item_table.get(itemName, None)

        if item_id is None:
            raise SkyblockParserException("Item not found.")

        lowest_price = None
        data = None

        for item in self.auction_cache:

            if item["id"] != item_id:
                continue


            if lowest_price is None or item["price"] < lowest_price:
                lowest_price = item["price"]
                data = item

        lore = data["itemLore"].split("\n")
        name = data["itemName"]

        lore.insert(0, name)

        return render(lore)
