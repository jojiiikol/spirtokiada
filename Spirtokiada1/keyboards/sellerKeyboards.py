from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
import __main__

def get_selling_ticket():
    keyboard = ReplyKeyboardBuilder()
    keyboard.row(
        types.KeyboardButton(text="Продать билет💵")
    )
    return keyboard

# Добавить кнопку возрата назад!
def get_game_type():
    keyboard = InlineKeyboardBuilder()
    game_list = __main__.db.show_game_list()
    for game in game_list:
        keyboard.add(
            types.InlineKeyboardButton(text=f"{game[1]}", callback_data=f"sell_game_{game[0]}")
        )
    keyboard.adjust(2)
    return keyboard

def set_confirm_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        types.InlineKeyboardButton(text="Подтвердить ✅", callback_data="sell_status_ok"),
        types.InlineKeyboardButton(text="Отменить ❌", callback_data="sell_status_cancel")
    )
    return keyboard