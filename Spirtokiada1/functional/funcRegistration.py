from aiogram import Router, F
from aiogram.filters import Command
from aiogram import types

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

import keyboards.technicKeyboard
from keyboards import regKeyboards, playerKeyboards, sellerKeyboards

import __main__

routerRegistartion = Router()


class Registration(StatesGroup):
    set_firstName = State()
    set_lastName = State()
    set_employee = State()
    get_password = State()


class SetTechnic(StatesGroup):
    set_zone = State()


@routerRegistartion.message(Command("reg"))
async def command_reg(message: types.Message, state: FSMContext):
    __main__.db.cursor.execute(f"""SELECT * FROM users WHERE tg_id = {message.from_user.id}""")
    user = __main__.db.cursor.fetchone()
    if user:
        await message.answer(text="Вы уже прошли этап регистрации :D")
    else:
        await message.answer(text="Напишите свое имя: ")
        await state.set_state(Registration.set_firstName)


@routerRegistartion.message(Registration.set_firstName)
async def set_firstname(message: types.Message, state: FSMContext):
    await state.update_data(firstName=message.text)
    await message.answer(text="Напишите свою фамилию: ")
    await state.set_state(Registration.set_lastName)


@routerRegistartion.message(Registration.set_lastName)
async def set_lastname(message: types.Message, state: FSMContext):
    await state.update_data(lastName=message.text)
    await state.update_data(nickname=message.from_user.username)
    await state.update_data(tg_id=message.from_user.id)
    await state.update_data(chat_id=message.chat.id)
    await message.answer(text="Кто ты, воин?", reply_markup=regKeyboards.get_reg_keyboard().as_markup())
    await state.set_state(Registration.set_employee)


@routerRegistartion.callback_query(Registration.set_employee, F.data.contains("role_"))
async def end_regisration(callback: types.CallbackQuery, state: FSMContext):
    role = callback.data.split("_")
    if role[1] == "player":
        await callback.answer()
        await callback.message.delete()
        await state.update_data(employee="FALSE")
        user_data = await state.get_data()
        await __main__.db.create_player(nickname=user_data['nickname'], first_name=user_data['firstName'],
                                        last_name=user_data['lastName'], employee=False, tg_id=user_data['tg_id'],
                                        chat_id=user_data['chat_id'])

        user_id = await __main__.db.get_user_id(callback.from_user.id)
        await callback.message.answer(
            text=f"Спасибо!\nВаше имя: {user_data['firstName']} \nВаша фамилия: {user_data['lastName']} \nВаш номер: <b>{user_id}</b>")
        await callback.message.answer(text="Прошу закрепить верхнее сообщение, чтобы не забыть ваш номер!",
                                      reply_markup=playerKeyboards.get_start_keyboard().as_markup(
                                          resize_keyboard=True,
                                          input_field_placeholder="Начинай, чего ты ждешь?"))
        await state.clear()

    if role[1] == "organization":
        await callback.answer()
        await callback.message.delete()
        await callback.message.answer(text="Введи пароль: ")
        await state.set_state(Registration.get_password)


@routerRegistartion.message(Registration.get_password)
async def get_pass(message: types.Message, state: FSMContext):
    if message.text == "12345":
        await state.update_data(employee="TRUE")
        user_data = await state.get_data()
        await __main__.db.create_player(nickname=message.from_user.username, first_name=user_data['firstName'],
                                        last_name=user_data['lastName'], employee=True, tg_id=message.from_user.id,
                                        chat_id=message.chat.id)

        user_id = await __main__.db.get_user_id(message.from_user.id)
        await message.answer(
            text=f"Добро пожаловать, коллега!\nВаше имя: {user_data['firstName']} \nВаша фамилия: {user_data['lastName']} \nВаш номер: <b>{user_id}</b>")
        await state.clear()
        await message.answer(text="Выбери свою роль", reply_markup=regKeyboards.get_org_keyboard().as_markup())
    else:
        await message.answer(
            text="Ты ошибся походу, игрок :)\nСнова используй команду <b>/reg</b> и больше не баллуйся!👺")
        await state.clear()


@routerRegistartion.callback_query(F.data.contains("org_"))
async def get_org_role(callback: types.CallbackQuery, state: FSMContext):
    role = callback.data.split("_")
    if role[1] == "seller":
        await callback.answer()
        await callback.message.delete()
        await callback.message.answer(text="""Твоя цель - продавать билеты
        Как это происходит?
        
        Ты спрашиваешь у человека на какую игру он хочет купить билет, производишь оплату и далее тыкаешь по кнопке с названием игры.
        Потом тебе необходимо будет ввести номер игрока(спроси про номер у игрока).
        Если все прошло без проблем - поздравляю, ты продал билет!
            Если ты где-то ошибся, жмякни на кнопку "Отменить продажу" и сделай все заново, только второй раз не тряси деньги у игрока :)""",
                                      reply_markup=sellerKeyboards.get_selling_ticket().as_markup(resize_keyboard=True,
                                                                                                  input_field_placeholder="Удачи в продажах!"))
    if role[1] == "technic":
        await callback.answer()
        await callback.message.delete()
        await state.set_state(SetTechnic.set_zone)
        await callback.message.answer(text="Выбери игровую зону",
                                      reply_markup=regKeyboards.get_technic_keyboard().as_markup())



@routerRegistartion.callback_query(SetTechnic.set_zone, F.data.contains("set_zone_"))
async def set_zone(callback: types.CallbackQuery, state: FSMContext):
    zone = callback.data.split("_")[2]
    await callback.answer()
    await callback.message.delete()
    await state.update_data(zone=zone)
    data = await state.get_data()
    user_id = await __main__.db.get_user_id(tg_id=callback.from_user.id)

    await __main__.db.set_zone_technic(user_id=user_id, game_id=data["zone"])
    await callback.message.answer(
        text="Твоя задача - следить за билетами и обнулять их\nКак это делать?\nК тебе приходит игрок и говорит, что купил билет на твою игру\nТы жамкаешь кнопку для вывода билетов на экран --> Ищешь его билет у себя --> Нажимаешь на билет и обнуляешь его --> Игрок играет - игрок счастлив\n\nЕсли билета игрока у тебя нет в списке - попроси показать его телефон и тыкни у него на кнопку 'Билеты': \n\t\t\t\tЕсли у него нет билета на твою игру, то он мошенник и смело отправляй его на кассу\n\t\t\t\tЕсли у него есть билет, то пиши @jojiiikol номер билета, название игры, номер игрока",
        reply_markup=keyboards.technicKeyboard.get_main_keyboard().as_markup(resize_keyboard=True,
                                                                             input_field_placeholder="Жамкай чаще! :)"))
    await state.clear()
