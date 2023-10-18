from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def get_admin_keyboard():
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(
        types.KeyboardButton(text="Выдать билет"),
        types.KeyboardButton(text="Показать все билеты"),
        types.KeyboardButton(text="Весь рейтинг"),
        types.KeyboardButton(text="Зачислить очки")
    )
    return keyboard


def get_list_tickets_for_change(tickets_list):
    keyboard = InlineKeyboardBuilder()
    for ticket in tickets_list:
        keyboard.add(
            types.InlineKeyboardButton(text=f"Билет №{ticket[0]} ---- Игрок: {ticket[2]} ----- Активность: {ticket[3]}",
                                       callback_data=f"change_status_tic_{ticket[0]}_for_user_{ticket[2]}")
        )

    keyboard.adjust(1)
    return keyboard
