from aiogram import Router, F
from aiogram import types

import keyboards.technicKeyboard
from keyboards import technicKeyboard
import __main__

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

routerTechnic = Router()


class Change_status(StatesGroup):
    ticket_id = State()
    confirm = State()


class Set_point(StatesGroup):
    player_id = State()
    confirm = State()
    points = State()


@routerTechnic.message(F.text == "Начислить баллы победителю")
async def set_points(message: types.Message, state: FSMContext):
    employee = await __main__.db.check_employee(tg_id=message.from_user.id)
    if employee:
        await message.answer("Введите номер игрока")
        await state.set_state(Set_point.player_id)
    else:
        await message.answer(text="Тебе запрещено тут быть >:(")




@routerTechnic.message(Set_point.player_id)
async def set_player(message: types.Message, state: FSMContext):
    if message.text.isnumeric():
        person = await __main__.db.check_person(user_id=message.text)
        if person:
            await state.update_data(player_id=message.text)
            data = await state.get_data()
            await message.answer(text=f"Вы выбрали игрока под номером: <b>{data['player_id']}</b>",
                                 reply_markup=keyboards.technicKeyboard.set_confirm_keyboard_for_victory().as_markup())
            await state.set_state(Set_point.confirm)
        else:
            await message.answer(text="Игрока с таким номером не существует\nВведите номер еще раз")
    else:
        await message.answer(text="Номер введен неверно, он должен состоять из цифр\nВведите номер еще раз")




@routerTechnic.callback_query(Set_point.confirm, F.data.contains('victory_'))
async def set_victory(callback: types.CallbackQuery, state:FSMContext):
    choice = callback.data.split('_')[1]
    await state.update_data(confirm=choice)
    if choice == 'ok':
        await callback.answer()
        await callback.message.delete()
        await callback.message.answer("Введите количество очков")
        await state.set_state(Set_point.points)
    if choice == 'cancel':
        await callback.answer()
        await callback.message.delete()
        await callback.message.answer("Отмена")
        await state.clear()

@routerTechnic.message(Set_point.points)
async def get_points_to_player(message: types.Message, state: FSMContext):
    await state.update_data(points=message.text)
    data = await state.get_data()
    points = await __main__.db.get_user_points(data['player_id'])
    await __main__.db.set_points_to_user(data['player_id'], points, data['points'])
    await state.clear()
    await message.answer(text="Начислено")


@routerTechnic.message(F.text == "Показать список билетов🎫")
async def show_tickets(message: types.Message, state: FSMContext):
    employee = await __main__.db.check_employee(tg_id=message.from_user.id)
    if employee:
        list_tickets = await __main__.db.get_active_tickets(tg_id=message.from_user.id)
        keyboard = keyboards.technicKeyboard.get_list_tickets_for_change(list_tickets)
        await message.answer(text="Выбери билет: ", reply_markup=keyboard.as_markup())
        await state.set_state(Change_status.ticket_id)
    else:
        await message.answer(text="Тебе запрещено тут быть >:(")


@routerTechnic.callback_query(Change_status.ticket_id, F.data.contains("change_status_tic"))
async def confirm_change_status(callback: types.CallbackQuery, state: FSMContext):
    ticket_id = callback.data.split("_")[3]
    user_id = callback.data.split("_")[6]
    await state.update_data(ticket_id=f"{ticket_id}")
    await state.update_data(user_id=f"{user_id}")
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer(text=f"Билет <b>№{ticket_id}</b>",
                                  reply_markup=keyboards.technicKeyboard.set_confirm_keyboard().as_markup())
    await state.set_state(Change_status.confirm)


@routerTechnic.callback_query(Change_status.confirm, F.data.contains("change_status_"))
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
