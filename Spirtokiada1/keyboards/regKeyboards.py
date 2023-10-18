from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
import __main__

def get_reg_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        types.InlineKeyboardButton(text="Игрок 🎮", callback_data="role_player"),
        types.InlineKeyboardButton(text="Организатор 👷‍♂️", callback_data="role_organization")
    )
    return keyboard

def get_org_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        types.InlineKeyboardButton(text="Продавец", callback_data="org_seller"),
        types.InlineKeyboardButton(text="Игротехник", callback_data="org_technic"),
    )
    return keyboard

def get_technic_keyboard():
    keyboard = InlineKeyboardBuilder()
    game_list = __main__.db.show_game_list()
    for game in game_list:
        keyboard.add(
            types.InlineKeyboardButton(text=f"{game[1]}", callback_data=f"set_zone_{game[0]}")
        )

    return keyboard