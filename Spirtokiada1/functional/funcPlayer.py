from aiogram import Router, F
from aiogram.filters import Command
from aiogram import types

from aiogram.types import FSInputFile
import __main__

import keyboards.playerKeyboards
from keyboards import playerKeyboards

routerPlayer = Router()


@routerPlayer.message(F.text == "Начать!🎮")
async def start_play(message: types.Message):
    await message.answer(text="""ДОБРО ПОЖАЛОВАТЬ НА СПИРТОКИАДУ!""",
                         reply_markup=keyboards.playerKeyboards.get_main_keyboard_for_player().as_markup(
                             resize_keyboard=True,
                             input_field_placeholder="Жмякни кнопочку :)"))


@routerPlayer.message(Command("start"))
async def command_start(message: types.Message):
    await message.answer(
        f"Привет, {message.from_user.full_name}! \nПрошу пройти регистрацию с помощью команды <b>/reg</b>. После этого мы тебе все объясним😊")

# РАСПИСАТЬ!!
@routerPlayer.message(Command("help"))
async def help_command_heandler(message: types.Message):
    await message.answer(""""""
                         )


@routerPlayer.message(F.text == "Билеты🎫")
async def get_tickets(message: types.Message):
    tickets = await __main__.db.show_ticket(message.from_user.id)
    if tickets == []:
        await message.answer(f"У тебя нет билетов, бегом на кассу!")
    else:
        for ticket in tickets:
            await message.answer(f"----- БИЛЕТ №{ticket[0]} -----\nИГРА: {ticket[1]}")


@routerPlayer.message(F.text == "Рейтинг🥇")
async def get_raiting(message: types.Message):
    rating = await __main__.db.show_rating(message.from_user.id)
    await message.answer(text=rating)


@routerPlayer.message(F.text == "Правила🧐")
async def get_rule(message: types.Message):
    await message.answer("Выбери игру, и я расскажу тебе правила :)",
                         reply_markup=playerKeyboards.get_rules_keyboard_for_player().as_markup())


@routerPlayer.callback_query(F.data.contains("rule_game"))
async def get_rules(callback: types.CallbackQuery):
    game = callback.data.split("_")[2]
    await callback.message.delete()
    if game == "1":
        await callback.message.answer("Правила игры 1")
    if game == "2":
        await callback.message.answer("Правила игры 2")
    if game == "3":
        await callback.message.answer("Правила игры 3")
    if game == "4":
        await callback.message.answer("Правила игры 4")
    if game == "5":
        await callback.message.answer("Правила игры 5")
    if game == "6":
        await callback.message.answer("Правила игры 6")
