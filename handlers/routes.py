from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import (Message,
                           InlineKeyboardMarkup,
                           InlineKeyboardButton,
                           ReplyKeyboardMarkup,
                           ReplyKeyboardRemove,
                           KeyboardButton,
                           CallbackQuery
                           )
from aiogram.fsm.context import FSMContext
from forms.user import Form
from datetime import datetime
import aiosqlite
import asyncio



router = Router()


DB_NAME = 'bazadanyh.sql'

ADMINS_ID = [7636147669]

SERVICES = ["Стрижка", "Бразильське фарбування", "Завивка"]



async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS applications(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        telegram_id INTEGER,
                        status TEXT DEFAULT 'new',
                        full_name TEXT,
                        phone    TEXT,
                        service  TEXT,
                        date     TEXT,
                        time TEXT,
                        reminded INTEGER DEFAULT 0
            )
                         
                         """)
        await db.commit()
        
        

        
async def get_upcoming_applications():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT * FROM applications WHERE status = 'confirmed' and reminded = 0")
        result = await cursor.fetchall()
        return result
    
    
async def mark_as_reminded(application_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
                            UPDATE applications
                            SET reminded = 1
                            WHERE id = ?
                            """,(application_id,))
        await db.commit()

async def check_reminders(bot: Bot):
    while True:
        applications = await get_upcoming_applications()
        for user in applications:
            try:
                date = user[6]
                time = user[7]
                combined = f"{date} {time}"
                input_date_and_time = datetime.strptime(combined, "%d.%m.%Y %H:%M")
                
                time_left = input_date_and_time - datetime.now()
                seconds_left = time_left.total_seconds()
                if 3000 <= seconds_left <= 3600:
                    await bot.send_message(chat_id=user[1], text="НАГАДУВАННЯ!\nЧерез годину у вас візит у барбершоп")
                    await mark_as_reminded(user[0])
            except Exception:
                pass
        await asyncio.sleep(30)
        


        
async def add_applications(telegram_id, full_name, phone, service, date, time):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT INTO applications(telegram_id, full_name, phone, service, date, time) VALUES(?, ?, ?, ?, ?, ?)", (telegram_id, full_name, phone, service, date, time))
        await db.commit()
        

async def get_application(status = None):
    async with aiosqlite.connect(DB_NAME) as db:
        if status:
            cursor = await db.execute("SELECT * FROM applications WHERE status = ?", (status,))
        else:
            cursor = await db.execute("SELECT * FROM applications")
        result = await cursor.fetchall()
        return result

    
def get_main_inline_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💰 Послуги", callback_data="prices")],
            [InlineKeyboardButton(text="📓 Записатися", callback_data="application")],
            [InlineKeyboardButton(text="📞 Наші контакти", callback_data="contacts")]
        ]
    )
    return keyboard


def get_inline_keyboard_zayava():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Підтвердити", callback_data="confirm_application")],
            [InlineKeyboardButton(text="✏️ Змінити", callback_data="edit_application")],
            [InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel_application")]
            
        ]
    )
    return keyboard

def get_posluga():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=("Стрижка"))],
            [KeyboardButton(text=("Бразильське фарбування"))],
            [KeyboardButton(text=("Завивка"))],
        ],
        resize_keyboard=True
    )
    return keyboard

def admin_control_panel(application):

    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"✅ Підтвердити №{application[0]}", callback_data=f"admin_confirm_{application[0]}")],
            [InlineKeyboardButton(text=f"❌ Відхилити №{application[0]}", callback_data=f"admin_reject_{application[0]}")]
            
        ]
    )
    return keyboard

def admin_button():

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"Нові заявки", callback_data=f"admin_new_zayava")],
            [InlineKeyboardButton(text=f"Усі заявки", callback_data=f"admin_everything_zayava")]
            
        ]
    )
    return keyboard


@router.callback_query(F.data =="admin_new_zayava")
async def process_admin_new_zayava(callback:CallbackQuery, state:FSMContext):
    
    access = await get_application('new')
    if not access:
        await callback.message.answer("Нових заявок немає.")
        await callback.answer()
        return
    
    for application in access:
            id = application[0]
            telegram_id = application[1]
            status = application[2]
            name = application[3]
            number = application[4]
            service = application[5]
            date = application[6]
            time = application[7]
                
                
            await callback.message.answer(f"📝Заявка - {id}\n\n"
                                 f"Телеграм айді - {telegram_id}\n\n"
                                 f"Статус - {status}\n\n"
                                 f"Ім'я - {name}\n\n"
                                 f"Номер телефону - {number}\n\n"
                                 f"Послуга - {service}\n\n"
                                 f"Дата - {date}\n"
                                 f"Година - {time}",
                                 reply_markup=admin_control_panel(application)
                                 )
    await callback.answer()

@router.callback_query(F.data =="admin_everything_zayava")
async def process_admin_everything_zayava(callback:CallbackQuery, state:FSMContext):
    
    access = await get_application()
    if not access:
        await callback.message.answer("Нових заявок немає.")
        await callback.answer()
        return
    
    for application in access:
            id = application[0]
            telegram_id = application[1]
            status = application[2]
            name = application[3]
            number = application[4]
            service = application[5]
            date = application[6]
            time = application[7]
                
                
            await callback.message.answer(f"📝Заявка - {id}\n\n"
                                 f"Телеграм айді - {telegram_id}\n\n"
                                 f"Статус - {status}\n\n"
                                 f"Ім'я - {name}\n\n"
                                 f"Номер телефону - {number}\n\n"
                                 f"Послуга - {service}\n\n"
                                 f"Дата - {date}\n"
                                 f"Година - {time}",
                                 reply_markup=admin_control_panel(application)
                                 )
    await callback.answer()

@router.callback_query(F.data == "confirm_application")
async def process_confirm(callback:CallbackQuery, state:FSMContext):
    data = await state.get_data()
    await add_applications(data["telegram_id"], data["name"], data["number"], data["service"], data["date"], data["time"])
    await callback.message.answer("Ви успішно записались на послугу!")
    await state.clear()
    await callback.answer()
    
@router.callback_query(F.data == "edit_application")
async def process_edit(callback:CallbackQuery, state: FSMContext):
        await state.clear()
        await state.update_data(telegram_id = callback.from_user.id)
        await callback.message.answer("Почнімо заповняти анкету заново")
        await callback.message.answer("Введіть ім'я:")
        await state.set_state(Form.name)
        await callback.answer()

@router.callback_query(F.data == "cancel_application")
async def process_cancel(callback:CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Заповнення анкети припинене")
    await callback.answer()
    
    

@router.message(Command("admin"))
async def admin(message:Message, state:FSMContext):
    await message.answer("Провіряємо ваш ID:...")
    
    if  message.from_user.id not in ADMINS_ID:
        await message.answer("У вас немає доступу")
        return
    
    
    await message.answer("Вхід успішно виконано!\nВи в головному меню Адміністратора", reply_markup=admin_button())
    
    
@router.callback_query(F.data.startswith("admin_confirm_"))
async def admin_confirmed(callback:CallbackQuery, bot:Bot):
    application_id = int(callback.data.split("_")[-1])
    await update_status_id(application_id, "confirmed")
    await callback.message.answer(f"Заявку номер {application_id} прийнято")
    get_apl = await get_application_by_id(application_id)
    telegram_id = get_apl[1]
    await bot.send_message(chat_id=telegram_id, text="Вашу заявку прийнято")
    await callback.answer()
    

@router.callback_query(F.data.startswith("admin_reject_"))
async def admin_rejected(callback:CallbackQuery, bot:Bot):
    application_id = int(callback.data.split("_")[-1])
    await update_status_id(application_id, "rejected")
    await callback.message.answer(f"Заявку номер {application_id} відхилено")
    get_apl = await get_application_by_id(application_id)
    telegram_id = get_apl[1]
    await bot.send_message(chat_id=telegram_id, text="Вашу заявку відхилено")
    await callback.answer()

@router.message(Command("start"))
async def start(message:Message):
    await message.answer(
        "Привіт! Тут ти можеш записаться на стрижку\n\nВибери дію:\n\n",
        reply_markup=get_main_inline_keyboard()
    )
    

async def update_status_id(application_id, status):
    async with aiosqlite.connect(DB_NAME) as db:
            await db.execute("""
                             UPDATE applications 
                             SET status = ?
                             WHERE id = ?
                             """,(status, application_id))
            await db.commit()
            
            

async def get_application_by_id(application_id):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(f"SELECT * FROM applications WHERE id = ?", (application_id,))
        result = await cursor.fetchone()
        return result
    
@router.callback_query(F.data == "prices")
async def process_services(callback:CallbackQuery):
    await callback.message.answer(
        "💰 Наші ціни:\n\n"

        "• Стрижка — 1200 грн\n"

        "• Бразильське фарбування — 4000 грн\n"

        "• Завивка — 4300 грн"
    )
    await callback.answer()
    
@router.callback_query(F.data == "contacts")
async def process_contacts(callback:CallbackQuery):
    contacts_text =(
                "<b>НАШІ КОНТАКТИ:</b>\n\n"
            "Місцезнаходження — <a href='https://google.com'>Google Maps</a>\n"
            "Номер телефону — <code>+13123513541</code>\n"
            "Наш Інстаграм — <a href='https://instagram.com'>Instagram</a>"
    )
    await callback.message.answer(contacts_text, parse_mode="HTML")
    await callback.answer()
    
    
    
@router.callback_query(F.data == "application")
async def application_start(callback: CallbackQuery, state: FSMContext):
    await state.update_data(telegram_id = callback.from_user.id)
    await callback.message.answer("Введіть ваше ім'я:")
    await state.set_state(Form.name)
    await callback.answer()
    
@router.message(Form.name, F.text)
async def procces_name(message: Message, state: FSMContext):
    await state.update_data(name = message.text)
    await message.answer("Тепер введіть ваш номер:")
    await state.set_state(Form.number)
    
@router.message(Form.number)
async def process_number(message:Message, state: FSMContext):
    phone_number = message.text
    
    if not phone_number.startswith("+") or not phone_number[1:].isdigit() or len(phone_number) != 13:
        await message.answer("Номер введено не коректно\nПриклад номеру:+380999999999")
        return
    
    
    await state.update_data(number = message.text)
    await message.answer("Чудово, а тепер введіть послугу, яку ви обрали:", reply_markup=get_posluga())
    await state.set_state(Form.service)
    
@router.message(Form.service)
async def process_service(message:Message, state: FSMContext):
    
    
    if message.text not in SERVICES:
        await message.answer("Такої послуги не існує", reply_markup=get_posluga())
        return
    
    await state.update_data(service = message.text)
    await message.answer("Напишіть дату на яку ви б хотіли записатися\n\nЗа таким прикладом - дд.мм.рррр", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Form.date)
    
    
@router.message(Form.date)
async def process_date(message:Message, state:FSMContext):
    
    date_text = message.text
    
    try:
        input_date = datetime.strptime(message.text, "%d.%m.%Y").date()
        if input_date < datetime.now().date():
            await message.answer("Ця дата вже минула! Введіть майбутню дату (наприклад: 29.08.2026):")
            return
    except ValueError:
        await message.answer("Неправильний формат дати. Приклад: 29.08.2026")
        return
        
    await state.update_data(date=date_text)
    await message.answer("Останній крок!\nВкажіть годину на яку бажаєте записатись")
    await state.set_state(Form.time)
    
    
    
@router.message(Form.time)
async def process_time(message:Message, state:FSMContext):
    input_time = message.text.strip()
    try:
        hours, minutes = input_time.split(":")
        hours = int(hours)
        minutes = int(minutes)
    except ValueError:
        await message.answer("Час вказано не коректно\nПриклад: 15:00")
        return

    if minutes < 0 or minutes > 59:
        await message.answer("Хвилини вказано некоректно (від 00 до 59).\nПриклад: 15:00")
        return
    
    if hours > 21 or hours < 8:
            await message.answer("Ми працюємо з 08:00 до 22:00.\nВкажіть час з 08:00 до 21:00 включно:")
            return
    
    await state.update_data(time=input_time)  
    
    data = await state.get_data()
    name = data["name"]
    number = data["number"]
    service = data["service"]
    date = data["date"]
    time = data["time"]
    
    
    await message.answer(f"Чудово\n\nПеревірте чи всі дані коректні:\n\nІм'я - {name}\nНомер телефону - {number}\nПослуга - {service}\nДата - {date}\nГодина - {time}",
                         reply_markup= get_inline_keyboard_zayava())
