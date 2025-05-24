import os, asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
import json

API_TOKEN = os.getenv('BOT_TOKEN') or ""

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
bot_answers = json.load(open("bot_answers.json", 'r', encoding='utf-8'))

@dp.message(Command(commands=['start', 'guide']))
async def start_message(message: types.Message):
    kb = [
        [
            types.InlineKeyboardButton(text="League of Legends", callback_data="menu:lol"), 
            types.InlineKeyboardButton(text="Ready or Not", callback_data="menu:ron"), 
            types.InlineKeyboardButton(text="Обратная связь", callback_data="menu:feedback")
        ],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    await message.answer(bot_answers["start"]["message"], reply_markup=keyboard)

@dp.callback_query(F.data.startswith("menu"))
async def menu_callback(callback: types.CallbackQuery):
    kb = []
    destination = bot_answers
    for path in callback.data.split(':')[1:]:
        destination = destination[path]

    for _ in range(destination["button_rows"]):
        kb.append([])
    
    for button in destination["buttons"]:
        kb[button["row"]].append(types.InlineKeyboardButton(text=button["name"], callback_data=button["callback_data"]))
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    await callback.message.edit_text(text=destination["message"], reply_markup=keyboard)

@dp.callback_query(F.data.startswith("guides"))
async def guide_callback(callback: types.CallbackQuery):
    guide = bot_answers 
    for path in callback.data.split(':'):
        guide = guide[path]

    await callback.message.edit_text(text=guide[0])

    text = ""
    for line in guide[1:]:
        if line.startswith("IMAGE:"):
            if text != "": 
                await callback.message.answer(text)
                text = ""
            img = line.replace("IMAGE:", "").split("CAPTION:")
            if len(img) == 1:
                img.append("")
            await callback.message.answer_photo(photo=img[0], caption=img[1])
        else:
            text += line
    if text != "": 
        await callback.message.answer(text)

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())