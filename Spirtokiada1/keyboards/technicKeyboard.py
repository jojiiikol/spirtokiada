from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

def get_main_keyboard():
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(
        types.KeyboardButton(text="Показать список билетов🎫"),
        types.KeyboardButton(text="Начислить баллы победителю")
    )

    return keyboard

def get_list_tickets_for_change(tickets_list):
    keyboard = InlineKeyboardBuilder()
    for ticket in tickets_list:
        keyboard.add(
            types.InlineKeyboardButton(text=f"Билет №{ticket[0]} ---- Игрок: {ticket[2]}", callback_data=f"change_status_tic_{ticket[0]}_for_user_{ticket[2]}")
        )

    keyboard.adjust(1)
    return keyboard

def set_confirm_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        types.InlineKeyboardButton(text="Подтвердить ✅", callback_data="change_status_ok"),
        types.InlineKeyboardButton(text="Отменить ❌", callback_data="change_status_cancel")
    )
    return keyboard

def set_confirm_keyboard_for_victory():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        types.InlineKeyboardButton(text="Подтвердить ✅", callback_data="victory_ok"),
        types.InlineKeyboardButton(text="Отменить ❌", callback_data="victory_cancel")
    )
    return keyboard


