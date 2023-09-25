import requests
import datetime
from aiogram import Bot, Dispatcher, types
import asyncio
from aiogram.filters.command import Command

bot = Bot(token="YOUR TOKEN")
dp = Dispatcher()

url = 'https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions'
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"}

# get a list of games
def getting_games():
    req = requests.get(url, headers=headers)
    result = req.json()
    list_games = []

    elements = result["data"]["Catalog"]["searchStore"]["elements"]
    final_free_game_list = []
    
    # game check
    for game in elements:
        if not game['promotions']:
            continue
        if not game['promotions']['promotionalOffers']:
            continue
        promotional_offers = game['promotions']['promotionalOffers'][0]['promotionalOffers'][0]
        end_date = promotional_offers['endDate']
        end_date = datetime.datetime.fromisoformat(end_date[:-1])
        if not end_date > datetime.datetime.utcnow():
            continue

        if promotional_offers['discountSetting']['discountPercentage'] != 0:
            continue

        final_free_game_list.append(game)

    # Let's break the answer down into manageable chunks
    for game in range(len(final_free_game_list)):
        name_game = final_free_game_list[game]['title']
        description_game = final_free_game_list[game]['description']
        date_start = final_free_game_list[game]['promotions']['promotionalOffers'][0]['promotionalOffers'][0]['startDate']
        date_start = datetime.datetime.strptime(date_start, "%Y-%m-%dT%H:%M:%S.%fZ") + datetime.timedelta(hours=3)
        date_end = final_free_game_list[game]['promotions']['promotionalOffers'][0]['promotionalOffers'][0]['endDate']
        date_end = datetime.datetime.strptime(date_end, "%Y-%m-%dT%H:%M:%S.%fZ") + datetime.timedelta(hours=3)
        list_games.append({'name_game': name_game, 'description_game': description_game, 'date_start': date_start, 'date_end': date_end})

    return list_games

# bot welcome message
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hi, this is an information bot that informs about the current giveaway of games on the Epic Games Store\n\nCommands:\n/free - get a list of games that are currently being given away")

@dp.message(Command("free"))
async def cmd_start(message: types.Message):
    send_message = 'The games that are being given away today:\n'
    get_game = getting_games()
    counter = 0
    for game in range(len(get_game)):
        counter += 1
        send_message += f'\n{counter}) Game name: {get_game[game]["name_game"]}\n\nDescription\n{get_game[game]["description_game"]}\n\nDate start: {get_game[game]["date_start"]}\nDate end: {get_game[game]["date_end"]}\n'

    await message.answer(send_message)
    
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
