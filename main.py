from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from app import keyboards as kb
from app import database as db
from dotenv import load_dotenv
import os
# from aiogram.utils.callback_data import CallbackData

storage = MemoryStorage()
load_dotenv()
bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher(bot=bot, storage=storage)


async def on_startup(_):
    await db.db_start()
    print('Бот запущен')


class registration(StatesGroup):
    first_name = State()
    surname = State()
    city = State()
    address = State()
    phone_number = State()
    cancel = State()

class NewOrder(StatesGroup):
    type = State()
    name = State()
    desc = State()
    price = State()
    photo = State()
    cancel = State()




# Обработка кнопки 'Отмена'
@dp.message_handler(state='*', commands='Отмена')
@dp.message_handler(Text(equals='Отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('Cancelled.', reply_markup=kb.admin_panel)


# -----------------------------------------------------Команды------------------------------------------------------
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await db.cmd_start_db(message.from_user.id)
    await message.answer(f'{message.from_user.first_name}, добро пожаловать в кафе "Меланж"!',
                         reply_markup=kb.main)
    if message.from_user.id == int(os.getenv('ADMIN_ID')):
        await message.answer(f'Вы авторизовались как администратор!', reply_markup=kb.main_admin)


@dp.message_handler(commands=['id'])
async def cmd_id(message: types.Message):
    await message.answer(f'{message.from_user.id}')


@dp.message_handler(commands=['menu'])
async def menu_command(message: types.Message):
    await db.sql_read(message)
    # await message.answer(f'Вы выбрали меню!',
    #                      reply_markup=kb.catalog_list)


@dp.message_handler(commands='address')
async def contact(message: types.Message):
    await message.answer(f'Адрес: г.Протвино, ул. Ленина, д.19 \nРежим работы: вс.- чт. с 10:00 до 21:00 '
                         f'\nпт.- сб. с 10.00 до 22.00')


@dp.message_handler(commands='contacts')
async def contacts(message: types.Message):
    await message.answer(f'Телефон ресторана: +7 (4967) 74-28-34')


# ----------------------------------------------Главное меню----------------------------------------------
@dp.message_handler(text='📞 Контакты')
async def contacts(message: types.Message):
    await message.answer(f'Телефон ресторана: +7 (4967) 74-28-34')


@dp.message_handler(text='🛍 Корзина')
async def shopcart(message: types.Message):
    dishes = await db.read_dishes_in_shopcart(message.from_user.id, message)
    result = ""
    sum = 0
    for dish in dishes:
        sum += int(dish[4]) * int(dish[2])
        result += f"{dish[0]}: {dish[4]} * {dish[2]} = {int(dish[4]) * int(dish[2])}\n"
    result += "\n"

    result += f"Итого по чеку: {sum} руб."

    await bot.send_message(message.from_user.id, result, reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(f'Оформить заказ', callback_data='checkout')))




@dp.message_handler(text='📍 Адрес и режим работы')
async def contacts(message: types.Message):
    await message.answer(f'Адрес: г.Протвино, ул. Ленина, д.19 \nРежим работы: вс.- чт. с 10:00 до 21:00 '
                         f'\nпт.- сб. с 10.00 до 22.00')


@dp.message_handler(text='↗️ ВК и Instagram')
async def contacts(message: types.Message):
    await message.answer(f'Вступайте в наши группы в социальных сетях. Там вся актуальная '
                         f'информация о новинках и работе ресторана!'
                         f'\nНаш ВК: https://vk.com/pro_melange'
                         f'\nНаш Instagram: https://instagram.com/pro_melange?igshid=NTc4MTIwNjQ2YQ==')


@dp.message_handler(text='🍽 Меню')
async def menu_command(message: types.Message):
    # await db.sql_read(message)
    await message.answer('Добро пожаловать в меню!', reply_markup=kb.catalog_list_menu)
    # await message.answer(f'Вы выбрали меню!',
    #                      reply_markup=kb.catalog_list)
    #                       # f'\nпт.- сб. с 10.00 до 22.00', callback_data=dishes(action='get_all'))


# ------------------------------------------------- Часть администратора---------------------------------------
# Начало регистрации
@dp.message_handler(commands='registration')
async def add_name(message: types.Message):
    await registration.first_name.set()
    await message.reply(f'Для того, чтобы закончить оформление заказа, пожалуйста, напишите свое имя:')


# Ловим первый ответ и записываем имя пользователя
@dp.message_handler(state=registration.first_name)
async def add_name(message: types.callback_query, state: FSMContext):
    async with state.proxy() as data:
        data['first_name'] = message.text
    await message.answer(f'Напишите свою фамилию:', reply_markup=kb.cancel)
    await registration.next()


# Ловим ответ и записываем фамилию пользователя
@dp.message_handler(state=registration.surname)
async def add_surname(message: types.Message, state: FSMContext):
    if message.text == 'Отмена':
        await state.set_state(registration.cancel.state)

    async with state.proxy() as data:
        data['surname'] = message.text
    await message.answer(f'Напишите свой город', reply_markup=kb.cancel)
    await registration.next()


# Ловим ответ и записываем адрес
@dp.message_handler(state=registration.city)
async def add_city(message: types.Message, state: FSMContext):
    if message.text == 'Отмена':
        await state.set_state(registration.cancel.state)

    async with state.proxy() as data:
        data['city'] = message.text
    await message.answer(f'Напишите свой адрес', reply_markup=kb.cancel)
    await registration.next()


# Ловим ответ и записываем номер телефона
@dp.message_handler(state=registration.address)
async def add_address(message: types.Message, state: FSMContext):
    if message.text == 'Отмена':
        await state.set_state(registration.cancel.state)

    async with state.proxy() as data:
        data['address'] = message.text
    await message.answer(f'Напишите свой номер телефона')
    await registration.next()


# Ловим последний ответ
@dp.message_handler(state=registration.phone_number)
async def add_phone(message: types.Message, state: FSMContext):
    if message.text == 'Отмена':
        await state.set_state(registration.cancel.state)

    async with state.proxy() as data:
        data['phone_number'] = message.text
    await db.add_registration(state)
    await message.answer('Вы оформили заказ! Для подтверждения заказа с вами свяжется менеджер ресторана!')
    await state.finish()


@dp.message_handler(text='Админ-панель')
async def contacts(message: types.Message):
    if message.from_user.id == int(os.getenv('ADMIN_ID')):
        await message.answer(f'Вы вошли как администратор!', reply_markup=kb.admin_panel)
    else:
        await message.reply('Я тебя не понимаю.')


@dp.message_handler(text='Доставка')
async def delivery(message: types.Message):
    shopcart_id = await db.select_not_ordered_shopcart_by_account(message.from_user.id)
    await db.change_order_status('delivery', shopcart_id)
    #kkkkkk


@dp.message_handler(text='Самовывоз')
async def pickup(message: types.Message):
    shopcart_id = await db.select_not_ordered_shopcart_by_account(message.from_user.id)
    await db.change_order_status('pickup', shopcart_id)
    # TODO: ПЕРЕВОД НА РЕГИСТРАЦИЮ


@dp.message_handler(text='Отменить оформление')
async def contacts(message: types.Message):
    if message.from_user.id == int(os.getenv('ADMIN_ID')):
        await message.answer(f'Вы вернулись в меню!', reply_markup=kb.main_admin)
    else:
        await message.answer(f'Вы вернулись в меню!', reply_markup=kb.main)


@dp.callback_query_handler(lambda x: x.data and x.data.startswith('del '))
async def del_callback_run(callback_query: types.CallbackQuery):
    await db.delete_dish(callback_query.data.replace('del ', ''))
    await callback_query.answer(text=f'{callback_query.data.replace("del ", "")} удалена.', show_alert=True)


@dp.message_handler(text='Удалить блюдо')
async def delete_dish(message: types.Message):
    if message.from_user.id == int(os.getenv('ADMIN_ID')):
        read = await db.sql_read2()
        for ret in read:
            await bot.send_photo(message.from_user.id, ret[4], f'{ret[1]}\nОписание: {ret[2]}\nЦена: {ret[3]}')
            await bot.send_message(message.from_user.id, text ='⬆️⬆️⬆️', reply_markup=InlineKeyboardMarkup().\
                                   add(InlineKeyboardButton(f'Удалить {ret[1]}', callback_data=f'del {ret[1]}')))





# Начало загрузки нового блюда
@dp.message_handler(text='Добавить блюдо')
async def add_dish(message: types.Message):
    if message.from_user.id == int(os.getenv('ADMIN_ID')):
        await NewOrder.type.set()
        await message.answer(f'Выберите категорию:', reply_markup=kb.catalog_list)
    else:
        await message.reply('Я тебя не понимаю.')


# Ловим первый ответ и записываем категорию
@dp.callback_query_handler(state=NewOrder.type)
async def add_dish_type(call: types.callback_query, state: FSMContext):
    async with state.proxy() as data:
        data['type'] = call.data
    await call.message.answer(f'Напишите название блюда', reply_markup=kb.cancel)
    await NewOrder.next()


# Ловим ответ и записываем название блюда
@dp.message_handler(state=NewOrder.name)
async def add_dish_name(message: types.Message, state: FSMContext):
    if message.text == 'Отмена':
        await state.set_state(NewOrder.cancel.state)

    async with state.proxy() as data:
        data['name'] = message.text
    await message.answer(f'Напишите описание блюда', reply_markup=kb.cancel)
    await NewOrder.next()


# Ловим ответ и записываем описание блюда
@dp.message_handler(state=NewOrder.desc)
async def add_dish_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['desc'] = message.text
    await message.answer(f'Напишите цену блюда', reply_markup=kb.cancel)
    await NewOrder.next()


# Ловим ответ и записываем цену
@dp.message_handler(state=NewOrder.price)
async def add_dish_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['price'] = message.text
    await message.answer(f'Отправьте фотографию блюда')
    await NewOrder.next()


@dp.message_handler(lambda message: not message.photo, state=NewOrder.photo)
async def add_dish_photo(message: types.Message):
    await message.answer('Это не фотография!')


# Ловим последний ответ и записываем фото
@dp.message_handler(content_types=['photo'], state=NewOrder.photo)
async def add_dish_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['photo'] = message.photo[0].file_id
    await db.add_dish(state)
    await message.answer('Блюдо успешно добавлено', reply_markup=kb.admin_panel)
    await state.finish()

@dp.message_handler(text='Вернуться к главному меню')
async def cancel(message: types.Message):
    await message.reply('Назад', reply_markup=kb.main_admin)


@dp.message_handler(state=NewOrder.cancel)
async def add_dish_price(message: types.Message, state: FSMContext):
    await state.finish()
    if message.from_user.id == int(os.getenv('ADMIN_ID')):
        await message.answer(f'Вы вернулись в меню!', reply_markup=kb.main_admin)
    else:
        await message.answer(f'Вы вернулись в меню!', reply_markup=kb.main)

# @dp.message_handler(text='Отмена')
# async def cancel_admin(message: types.Message):
#     if message.from_user.id == int(os.getenv('ADMIN_ID')):
#         await message.answer(f'Вы вернулись в меню!', reply_markup=kb.main_admin)
#     else:
#         await message.answer(f'Вы вернулись в меню!', reply_markup=kb.main)

@dp.message_handler()
async def answer(message: types.Message):
    await message.reply('Извините, я вас не понимаю.')


# --------------------------------------------------- Меню--------------------------------------------
@dp.callback_query_handler(lambda c: c.data.startswith('menu_'))
async def callback_menu_catalog(callback_query: types.CallbackQuery):
    kind = callback_query.data.removeprefix('menu_')
    await db.read_dishes_by_kind(kind, callback_query.message)

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="back_from_catalog"))
    await bot.send_message(callback_query.message.chat.id, 'Вы посмотрели все блюда', reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data == 'back_from_catalog')
async def callback_back_to_menu_catalog(callback_query: types.CallbackQuery):
    # await callback_query.answer('Категории:', )
    await bot.send_message(callback_query.message.chat.id, 'Категории:', reply_markup=kb.catalog_list_menu)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('add_to_shopcart_'))
async def callback_query_add_to_shopcart(callback_query: types.CallbackQuery):
    account_id = callback_query.from_user.id
    dish_id = callback_query.data.removeprefix('add_to_shopcart_')
    shopcart_id = await db.select_not_ordered_shopcart_by_account(account_id)
    if shopcart_id is None:
        shopcart_id = await db.create_shopcart(account_id)

    await db.add_dish_to_shopcart(dish_id, shopcart_id)

    await bot.send_message(callback_query.message.chat.id, 'Вы добавили блюдо!')
    await callback_query.answer()


@dp.callback_query_handler(lambda c: c.data and c.data == 'checkout')
async def callback_query_checkout(callback_query: types.CallbackQuery):
    await callback_query.message.reply('Выберите способ доставки:', reply_markup=kb.delivery_type_buttons)





@dp.callback_query_handler(lambda c: c.data and c.data.startswith('delete_from_shopcart_'))
async def callback_query_delete_from_shopcart(callback_query: types.CallbackQuery):
    account_id = callback_query.from_user.id
    dish_id = callback_query.data.removeprefix('delete_from_shopcart_')
    shopcart_id = await db.select_not_ordered_shopcart_by_account(account_id)
    if shopcart_id is None:
        await db.create_shopcart(account_id)
        await bot.send_message(callback_query.message.chat.id, 'Блюда нет в корзине!')
        await callback_query.answer()
        return

    check_is_delete = await db.delete_from_shopcart(dish_id, shopcart_id)
    if not check_is_delete:
        await bot.send_message(callback_query.message.chat.id, 'Блюда нет в корзине!')
    else:
        await bot.send_message(callback_query.message.chat.id, 'Вы удалили блюдо!')

    await callback_query.answer()


@dp.callback_query_handler()
async def callback_query_keyboard(callback_query: types.CallbackQuery):
    if callback_query.data == 'breakfast':
        await bot.send_message(chat_id=callback_query.from_user.id, text='Вы выбрали завтрак!')
    if callback_query.data == 'main_menu':
        await bot.send_message(chat_id=callback_query.from_user.id, text='Вы выбрали основное меню!')
    elif callback_query.data == 'pastries/desserts':
        await bot.send_message(chat_id=callback_query.from_user.id, text='Вы выбрали выпечку и десерты!')
    elif callback_query.data == 'drinkables':
        await bot.send_message(chat_id=callback_query.from_user.id, text='Вы выбрали напитки!')

# -------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)


# добавить в корзину
# вывод корзины
# удалить из корзины
