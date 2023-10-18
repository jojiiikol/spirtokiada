from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def get_main_keyboard_for_player():
    main_keyboard_for_player = ReplyKeyboardBuilder()
    main_keyboard_for_player.row(
        types.KeyboardButton(text="Билеты🎫"),
        types.KeyboardButton(text="Рейтинг🥇"),
        types.KeyboardButton(text="Правила🧐")
    )
    return main_keyboard_for_player


def get_rules_keyboard_for_player():
    rules_keyboard_for_player = InlineKeyboardBuilder()
    rules_keyboard_for_player.add(
        types.InlineKeyboardButton(text="Игра 1", callback_data="rule_game_1"),
        types.InlineKeyboardButton(text="Игра 2", callback_data="rule_game_2"),
        types.InlineKeyboardButton(text="Игра 3", callback_data="rule_game_3"),
        types.InlineKeyboardButton(text="Игра 4", callback_data="rule_game_4"),
        types.InlineKeyboardButton(text="Игра 5", callback_data="rule_game_5"),
        types.InlineKeyboardButton(text="Игра 6", callback_data="rule_game_6"),
    )
    rules_keyboard_for_player.adjust(2)

    return rules_keyboard_for_player

def get_start_keyboard():
    start_keyboard = ReplyKeyboardBuilder()
    start_keyboard.row(
        types.KeyboardButton(text="Начать!🎮")
    )
    return start_keyboard
