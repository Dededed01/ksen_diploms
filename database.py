import sqlite3 as sq

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from main import dp, bot

# from aiogram.utils.callback_data import CallbackData
# dishes_cb = CallbackData('')

db = sq.connect('tg.db')
cur = db.cursor()


async def db_start():
    cur.execute("CREATE TABLE IF NOT EXISTS accounts("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "tg_id INTEGER,  "
                "name TEXT, "
                "city TEXT, "
                "address TEXT, "
                "phone_number TEXT)")

    cur.execute("CREATE TABLE IF NOT EXISTS dishes("
                "i_id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "name TEXT, "
                "desc TEXT,"
                "price INTEGER, "
                "photo TEXT,"
                "kind TEXT)")

    cur.execute("CREATE TABLE IF NOT EXISTS shopcart("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "account_id INTEGER, "
                "delivery_type TEXT, "
                "ordered INTEGER DEFAULT 0, "
                "FOREIGN KEY(account_id) REFERENCES accounts(id))")

    cur.execute("CREATE TABLE IF NOT EXISTS dishes_to_shopcart("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "dish_id INTEGER,"
                "shopcart_id INTEGER,"
                "count INTEGER,"
                "FOREIGN KEY(dish_id) REFERENCES dishes(i_id),"
                "FOREIGN KEY(shopcart_id) REFERENCES shopcart(id))")

    db.commit()


async def cmd_start_db(user_id):
    user = cur.execute("SELECT * FROM accounts WHERE tg_id == {key}".format(key=user_id)).fetchone()
    if not user:
        cur.execute("INSERT INTO accounts (tg_id) VALUES ({key})".format(key=user_id))
        db.commit()


# async def add_user(message):
#     cur.execute("SELECT id FROM accounts WHERE id=?",(message.chat.id,))
#     user = cur.fetchone()
#     if not user:
#         cur.execute("INSERT INTO accounts (name, city, address, phone_number) VALUES(?,?,?,?)")
#     else:
#         pass
#
#
# async def add_user_name(message):
#     cur.execute("UPDATE accounts SET name=? WHERE id=?",(message.text,message.chat.id,))
#     db.commit()
#
#
# async def add_user_city(message):
#     cur.execute("UPDATE accounts SET city=? WHERE id=?",(message.text,message.chat.id,))
#     db.commit()
#
#
# async def add_user_address(message):
#     cur.execute("UPDATE accounts SET address=? WHERE id=?", (message.text, message.chat.id,))
#     db.commit()
#
#
# async def add_user_phone(message):
#     cur.execute("UPDATE accounts SET phone_number=? WHERE id=?", (message.text, message.chat.id,))
#     db.commit()
#

async def add_dish(state):
    async with state.proxy() as data:
        cur.execute("INSERT INTO dishes (name, desc, price, photo, kind) VALUES (?, ?, ?, ?, ?)",
                    (data['name'], data['desc'], data['price'], data['photo'], data['type']))
        db.commit()


async def add_registration(state):
    async with state.proxy() as data:
        cur.execute("INSERT INTO accounts (name, city, address, phone_number) VALUES (?, ?, ?, ?)",
                    (data['name'], data['city'], data['address'], data['phone_number']))
        db.commit()


async def sql_read(message):
    for ret in cur.execute('SELECT * FROM dishes').fetchall():
        await bot.send_photo(message.from_user.id, ret[4], f'{ret[1]}\nОписание: {ret[2]}\nЦена: {ret[3]} ')


async def read_dishes_by_kind(kind, message):
    data = cur.execute(f'SELECT * FROM dishes WHERE kind == ?', (kind,)).fetchall()
    for ret in data:
        await bot.send_photo(message.chat.id, ret[4], f'{ret[1]}\nОписание: {ret[2]}\nЦена: {ret[3]}',
                             reply_markup=InlineKeyboardMarkup()
                             .add(InlineKeyboardButton(f'Добавить в корзину', callback_data=f'add_to_shopcart_{ret[0]}'))
                             .add(InlineKeyboardButton(f'Удалить', callback_data=f'delete_from_shopcart_{ret[0]}')))

async def sql_read2():
    return cur.execute('SELECT * FROM dishes').fetchall()


async def delete_dish(data):
    cur.execute('DELETE FROM dishes WHERE name == ?', (data,))
    db.commit()


async def get_dish(dish_id, shopcart_id):
    data = cur.execute("SELECT d.name, d.desc, d.price, d.photo, ds.count, d.i_id FROM dishes_to_shopcart ds JOIN "
                       "dishes d ON "
                       "ds.dish_id == d.i_id WHERE shopcart_id == ?", (shopcart_id,)).fetchall()
    for dish in data:
        if dish[5] == int(dish_id):
            return f'{dish[0]}\nОписание: {dish[1]}\nЦена: {dish[2]}\nКоличество: {dish[4]}'
async def select_not_ordered_shopcart_by_account(account_id):
    shopcart = cur.execute('SELECT * FROM shopcart WHERE account_id == ? and ordered == 0', (account_id,)).fetchone()
    if not shopcart:
        return None

    return shopcart[0]


async def create_shopcart(account_id):
    shopcart = cur.execute("INSERT INTO shopcart (account_id, delivery_type, ordered) VALUES (?, ?, "
                           "?) RETURNING *", (account_id, "pickup", 0)).fetchone()

    db.commit()
    return shopcart[0]


async def add_dish_to_shopcart(dish_id, shopcart_id):
    dish_in_shopcart = cur.execute("SELECT * FROM dishes_to_shopcart WHERE dish_id = ? AND shopcart_id = ?",
                                   (dish_id, shopcart_id)).fetchone()
    if not dish_in_shopcart:
        cur.execute("INSERT INTO dishes_to_shopcart (dish_id, shopcart_id, count) VALUES (?, ?, "
                    "?)", (dish_id, shopcart_id, 1))
        db.commit()
    else:
        cur.execute("UPDATE dishes_to_shopcart SET count = count + 1 WHERE id = ?", (dish_in_shopcart[0],))
        db.commit()

async def rem_dish_from_shopcart(dish_id, shopcart_id):
    dish_in_shopcart = cur.execute("SELECT * FROM dishes_to_shopcart WHERE dish_id = ? AND shopcart_id = ?",
                                   (dish_id, shopcart_id)).fetchone()
    if dish_in_shopcart:
        cur.execute("UPDATE dishes_to_shopcart SET count = count - 1 WHERE id = ?", (dish_in_shopcart[0],))
        db.commit()
        answer = cur.execute("SELECT * from dishes_to_shopcart WHERE id = ?", (dish_in_shopcart[0],)).fetchone()
        return answer


async def delete_from_shopcart(dish_id, shopcart_id):
    dish_in_shopcart = cur.execute("SELECT * FROM dishes_to_shopcart WHERE dish_id = ? AND shopcart_id = ?",
                                   (dish_id, shopcart_id)).fetchone()
    if not dish_in_shopcart:
        return False

    cur.execute("DELETE FROM dishes_to_shopcart WHERE id = ?", (dish_in_shopcart[0],))
    db.commit()
    return True


async def read_dishes_in_shopcart(account_id, message):
    shopcart_id = await select_not_ordered_shopcart_by_account(account_id)

    data = cur.execute("SELECT d.name, d.desc, d.price, d.photo, ds.count, d.i_id FROM dishes_to_shopcart ds JOIN "
                       "dishes d ON "
                       "ds.dish_id == d.i_id WHERE shopcart_id == ?", (shopcart_id,)).fetchall()

    for ret in data:
        await bot.send_photo(message.chat.id, ret[3], f'{ret[0]}\nОписание: {ret[1]}\nЦена: {ret[2]}\nКоличество: {ret[4]}',
                             reply_markup=InlineKeyboardMarkup(row_width=3)
                             .row(InlineKeyboardButton(f'Добавить еще', callback_data=f'add_to_shopcart_{ret[5]}'),
                             InlineKeyboardButton(f'Убавить', callback_data=f'rem_from_shopcart_{ret[5]}'),
                             InlineKeyboardButton(f'Удалить', callback_data=f'delete_from_shopcart_{ret[5]}')))

    return data


async def change_order_status(status, shopcart_id):
    cur.execute('UPDATE shopcart SET delivery_type = ? WHERE id == ?', (status, shopcart_id))
    db.commit()
