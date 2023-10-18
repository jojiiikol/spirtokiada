from aiogram import Router, F
from aiogram import types

from keyboards import sellerKeyboards
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import __main__


class Sellticket(StatesGroup):
    id_game = State()
    id_player = State()
    confirm = State()


routerSeller = Router()

# Функция запускает FSM для продажи билета
# Проверка, действительно ли юзер - сотрудник?
@routerSeller.message(F.text == "Продать билет💵")
async def get_list_game(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    employee = await __main__.db.check_employee(tg_id=user_id)
    if employee:
        await message.answer(text="Выбери игру, которую необходимо продать",
                             reply_markup=sellerKeyboards.get_game_type().as_markup())
        await state.set_state(Sellticket.id_game)
    else:
        await message.answer(text="Чувачок, у тебя будут реальные проблемы👺")


# Сохранение значения игры в памяти
# Перевод на установки игрока
@routerSeller.callback_query(Sellticket.id_game, F.data.contains("sell_game"))
async def choise_game(callback: types.CallbackQuery, state: FSMContext):
    choice = callback.data.split("_")
    await callback.answer()
    await callback.message.delete()
    await state.update_data(game_id=choice[2])
    await callback.message.answer(f"Вы выбрали игру: {choice[2]}, введите номер игрока")
    await state.set_state(Sellticket.id_player)


# Установка юзера билету
# Проверка на существующего юзера
@routerSeller.message(Sellticket.id_player)
async def set_player(message: types.Message, state: FSMContext):
    if message.text.isnumeric():
        person = await __main__.db.check_person(user_id=message.text)
        if person:
            await state.update_data(id_player=message.text)
            data = await state.get_data()
            await message.answer(
                text=f"Билет на игру: <b>{data['game_id']}</b>\nИгрок с номером: <b>{data['id_player']}</b>",
                reply_markup=sellerKeyboards.set_confirm_keyboard().as_markup())
            await state.set_state(Sellticket.confirm)
        else:
            await message.answer(text="Игрока с таким номером не существует\nВведите номер еще раз")
    else:
        await message.answer(text="Номер введен неверно, он должен состоять из цифр\nВведите номер еще раз")


# Запись билета в бд
@routerSeller.callback_query(Sellticket.confirm, F.data.contains("sell_status"))
async def sell_ticket(callback: types.CallbackQuery, state: FSMContext):
    choice = callback.data.split("_")
    data = await state.get_data()
    if choice[2] == "ok":
        await callback.answer()
        await callback.message.edit_text(
            text=f"Билет на игру: <b>{data['game_id']}</b>\nИгрок с номером: <b>{data['id_player']}</b>\n-------------\n💸ПРОДАНО💸")
        game_id = data['game_id']
        user_id = data['id_player']
        await __main__.db.add_new_ticket(game_id=game_id, user_id=user_id)
        await state.clear()
    if choice[2] == "cancel":
        await callback.answer()
        await callback.message.edit_text(
            text=f"Билет на игру: <b>{data['game_id']}</b>\nИгрок с номером: <b>{data['id_player']}</b>\n-------------\n❌ОТМЕНЕНО❌")
        await state.clear()
