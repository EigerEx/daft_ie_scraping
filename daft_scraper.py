import asyncio
from bs4 import BeautifulSoup
import config
import re
import requests
import pickle
import discord
import random

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)



async def scrape_latest():
    """ Scrapes latest properties at link
        Makes array of each property as an object
        Returns this array"""
    URL = "https://www.daft.ie/property-for-rent/dublin-city?sort=publishDateDesc&rentalPrice_to=1500"
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find_all(class_="SearchPage__Result-gg133s-2")
    listings = []
    for listing in results:
        listing_ele = {
            "address" : listing.find(attrs={"data-testid" : "address"}).text.strip(),
            "price" : listing.find(attrs={"data-testid" : "price"}).text.strip(),
            "property_type" : listing.find(attrs={"data-testid" : "property-type"}).text.strip(),
            "link" : "https://www.daft.ie" + listing.find('a', {'href': re.compile(r'\/for-rent\/')}).get("href")
        }
        listings.append(listing_ele)
    return listings


async def print_listing(listing):
    print(listing["address"])
    print(listing["price"])
    print(listing["property_type"])
    print(listing["link"])
    print()

async def send_discord_message(ele):
    """ Sends a message on discord pinging me that a new listing is spotted"""
    channel = client.get_channel(525118950598639616)
    message = f'''<@284822134688186376>, new listing spotted!,
**Addess** : {ele['address']},
**Price** : {ele['price']},
**Link** : {ele['link']}'''
    await channel.send(message)


async def save_pickle(data):
    """ Saves data in the pickle """
    file = open("pickle", "wb")
    pickle.dump(data, file)
    file.close()


async def load_pickle():
    """ Loads data from the pickle """
    file = open("pickle", "rb")
    data = pickle.load(file)
    file.close()
    return data


async def alert_new_listing(new_listing):
    await print_listing(new_listing)
    await send_discord_message(new_listing)

async def main():
    """ 
    Scrapes new data
    Compares with saved data
    If a new listing is found, alert user!
    Save scraped data over old data
    """
    print("running!")
    scraped_data = await scrape_latest()
    saved_data = await load_pickle()
    for ele in scraped_data:
        if ele not in saved_data:
            await alert_new_listing(ele)
    #overwrite saved pickle with latest data
    await save_pickle(scraped_data)
    #loop
    await asyncio.sleep(random.randint(60, 300))
    await main()




@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    await asyncio.wait(await main())
    #loop_main_p = functools.partial(loop_main)
    #loop = asyncio.get_event_loop()
    #loop.run_until_complete(asyncio.wait(loop_main_p))
    #loop.close()
    #await loop.run_in_executor(None, loop_main_p)
    #await main()


client.run(config.token)

