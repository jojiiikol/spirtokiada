from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from aiogram import Router, F
from aiogram.filters import Command
from aiogram import types

import keyboards.technicKeyboard, keyboards.adminKeyboards
from keyboards import regKeyboards, playerKeyboards, sellerKeyboards, adminKeyboards

import __main__

adminRouter = Router()

class Sellticket_admin(StatesGroup):
    id_game = State()
    id_player = State()
    confirm = State()

class Change_status_admin(StatesGroup):
    ticket_id = State()
    confirm = State()

class set_points_admin(StatesGroup):
    user_id = State()
    points = State()

@adminRouter.message(F.text == "AdM1n")
async def get_admin_panel(message: types.Message):
    if message.from_user.username == "jojiiikol":
        await message.answer(text="Добро пожаловать, господин", reply_markup=keyboards.adminKeyboards.get_admin_keyboard().as_markup(resize_keyboard=True))
    else:
        pass
@adminRouter.message(F.text == "Зачислить очки")
async def set_points(message: types.Message, state: FSMContext):
    if message.from_user.username == "jojiiikol":
        await message.answer(text="Введите номер участника")
        await state.set_state(set_points_admin.user_id)
    else:
        await message.answer(text="403")

@adminRouter.message(set_points_admin.user_id)
async def update_points(message: types.Message, state:FSMContext):
    await state.update_data(user_id=message.text)
    await message.answer(text="Введите количество очков")
    await state.set_state(set_points_admin.points)

@adminRouter.message(set_points_admin.points)
async def add_points(message: types.Message, state:FSMContext):
    await state.update_data(points=message.text)
    data = await state.get_data()
    points = await __main__.db.get_user_points(data['user_id'])
    await __main__.db.set_points_to_user(data['user_id'], points, data['points'])
    await state.clear()



@adminRouter.message(F.text == "Весь рейтинг")
async def get_raiting(message: types.Message):
    if message.from_user.username == "jojiiikol":
        raiting = await __main__.db.get_raiting()
        raiting_text = ""
        for i, people in enumerate(raiting, 1):
            raiting_text += f"Место: {i}, Номер участника: {people[0]}, Имя Фамилия: {people[1], people[2]}, Очки: {people[3]}\n"
        await message.answer(text=raiting_text)
    else:
        await message.answer(text="403")

@adminRouter.message(F.text == "Показать все билеты")
async def show_tickets(message: types.Message, state: FSMContext):
    if message.from_user.username == "jojiiikol":
        list_tickets = await __main__.db.get_all_tickets()
        keyboard = keyboards.adminKeyboards.get_list_tickets_for_change(list_tickets)
        await message.answer(text="Выбери билет: ", reply_markup=keyboard.as_markup())
        await state.set_state(Change_status_admin.ticket_id)
    else:
        await message.answer(text="Тебе запрещено тут быть >:(")

@adminRouter.callback_query(Change_status_admin.ticket_id, F.data.contains("change_status_tic"))
async def confirm_change_status(callback: types.CallbackQuery, state: FSMContext):
    ticket_id = callback.data.split("_")[3]
    user_id = callback.data.split("_")[6]
    await state.update_data(ticket_id=f"{ticket_id}")
    await state.update_data(user_id=f"{user_id}")
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer(text=f"Билет <b>№{ticket_id}</b>", reply_markup=keyboards.technicKeyboard.set_confirm_keyboard().as_markup())
    await state.set_state(Change_status_admin.confirm)

@adminRouter.callback_query(Change_status_admin.confirm, F.data.contains("change_status_"))
async def change_status_ticket(callback: types.CallbackQuery, state: FSMContext):
    status = callback.data.split("_")[2]
    data = await state.get_data()
    if status == "ok":
        await callback.answer()
        await callback.message.edit_text(text=f"Билет <b>№{data['ticket_id']}</b>\n---------\nИСПОЛЬЗОВАН")
        await __main__.db.set_false_ticket(ticket_id=data['ticket_id'])
        await state.clear()
    if status == "cancel":
        await callback.answer()
        await callback.message.edit_text(text=f"Билет <b>№{data['ticket_id']}</b>\n---------\nОТМЕНА ИСПОЛЬЗОВАНИЯ")
        await state.clear()

@adminRouter.message(F.text=="Выдать билет")
async def get_ticket(message: types.Message, state: FSMContext):
    if message.from_user.username == "jojiiikol":
        await message.answer(text="Выбери игру, которую необходимо продать",
                             reply_markup=sellerKeyboards.get_game_type().as_markup())
        await state.set_state(Sellticket_admin.id_game)
    else:
        await message.answer(text="Тебе тут не место")



# Сохранение значения игры в памяти
# Перевод на установки игрока
@adminRouter.callback_query(Sellticket_admin.id_game, F.data.contains("sell_game"))
async def choise_game(callback: types.CallbackQuery, state: FSMContext):
    choice = callback.data.split("_")
    await callback.answer()
    await callback.message.delete()
    await state.update_data(game_id=choice[2])
    await callback.message.answer(f"Вы выбрали игру: {choice[2]}, введите номер игрока")
    await state.set_state(Sellticket_admin.id_player)


# Установка юзера билету
# Проверка на существующего юзера
@adminRouter.message(Sellticket_admin.id_player)
async def set_player(message: types.Message, state: FSMContext):
    if message.text.isnumeric():
        person = await __main__.db.check_person(user_id=message.text)
        if person:
            await state.update_data(id_player=message.text)
            data = await state.get_data()
            await message.answer(
                text=f"Билет на игру: <b>{data['game_id']}</b>\nИгрок с номером: <b>{data['id_player']}</b>",
                reply_markup=sellerKeyboards.set_confirm_keyboard().as_markup())
            await state.set_state(Sellticket_admin.confirm)
        else:
            await message.answer(text="Игрока с таким номером не существует\nВведите номер еще раз")
    else:
        await message.answer(text="Номер введен неверно, он должен состоять из цифр\nВведите номер еще раз")


# Запись билета в бд
@adminRouter.callback_query(Sellticket_admin.confirm, F.data.contains("sell_status"))
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


