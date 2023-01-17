import logging
import os
import wallet_interaction
import categories
import exception
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.contrib.fsm_storage.memory import MemoryStorage


API_TOKEN = os.getenv("API_TOKEN")
logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)


def auth(func):
    """Функція для свого роду авторизації. Бот розрахований з метою користування однією людиною."""
    async def wrapper(message):
        if message['from']['id'] != 366741870:  # Id люди, що буде користуватися ботом у телеграмі.
            return await message.reply("Вибачте, але ви не маєте доступу до цієї команди", reply=False)
        return await func(message)

    return wrapper


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """Цей хендлер буде визваний, коли користувач активує команди `/start` або `/help`"""
    await message.reply("Привіт!\n"
                        "Це твій персональний допоміжник у підрахунку витрат!\n"
                        "Мене звати WalletKeeper і я допоможу тобі вести бюджет!\n\n"
                        "Щоб додати витрату введіть, наприклад, '60 кавові вироби'\n"
                        "Саме так, зверни увагу, вказувати валюту не потрібно. "
                        "Я буду вважати, що ти використовуєшь гривні у повсякденності:)\n\n"
                        "Якщо ви бажаєте встановити щоденний ліміт базових витрат, введіть /set_base\n"
                        "За замовчуванням ваш ліміт базових витрат встановлений у розмірі 500 гривень.\n"
                        "До базових витрат входять тількі ті витрати, що йдуть на оплату фіксованих щоденних потреб.\n"
                        "Тобто серед категорій це: продукти, кава/чай, сніданок/обід/вечеря або будь-яке приймання їжі "
                        "та будь-щось інше, що не відноситься до основних категорій окрім вищеперелічених.\n\n"
                        "Останні ващі витрати: /last_expenses\n"
                        "Категорії: /categories\n"
                        "Сьогоденна статистика: /today_stat\n"
                        "Cтатистика за цей місяць: /month_stat\n"
                        "Щомісячна статистика: /every_month_stat\n",
                        reply=False)


@dp.message_handler(lambda message: message.text.startswith('/delete'))
async def delete_expense(message: types.Message):
    """Цей хендлер буде визваний, коли користувач введе `/delete[id_витрати]`"""

    row = int(message.text[7:])
    wallet_interaction.delete_by_id(row)
    answer = "Витрата була видалена"
    await message.answer(answer)


@dp.message_handler(commands=['categories'])
async def show_categories(message: types.Message):
    """Цей хендлер буде визваний, коли користувач введе `/categories`"""

    showcase = categories.Categories().get_all_categories()
    answer_message = "Категорії:\n\n* " + \
                     ("\n* ".join([category.name + ' -- ' + category.nominations for category in showcase]))
    await message.answer(answer_message)


@dp.message_handler(Command("set_base"), state=None)
async def quest_basic(message: types.Message):
    """Цей хендлер буде визваний, коли користувач введе `/set_base`"""

    await message.answer("Яким буде ваш ліміт базових витрат у день?")
    await wallet_interaction.BasicExp.Q1.set()


@dp.message_handler(state=wallet_interaction.BasicExp.Q1)
async def set_basic(message: types.Message, state: FSMContext):
    """Цей хендлер буде визваний, коли користувач відповість, скільки в нього буде щоденний ліміт"""

    answer = message.text
    await state.update_data(answer=answer)
    data = await state.get_data()
    value = data.get("answer")
    basic_set = wallet_interaction.set_basic_expenses(value)
    await message.answer(f"Ваші базові витрати встановлені у розмірі {basic_set} грн.")
    await state.finish()


@dp.message_handler(commands=['today_stat'])
async def today_stat(message: types.Message):
    """Цей хендлер буде визваний, коли користувач введе `/today_stat`"""

    today_statistics = wallet_interaction.today_stat()
    await message.answer(today_statistics)


@dp.message_handler(commands=['month_stat'])
async def month_stat(message: types.Message):
    """Цей хендлер буде визваний, коли користувач введе `/month_stat`"""

    month_statistics = wallet_interaction.month_stat()
    await message.answer(month_statistics)


@dp.message_handler(commands=['every_month_stat'])
async def month_stat(message: types.Message):
    """Цей хендлер буде визваний, коли користувач введе `/every_month_stat`"""

    every_month_statistics = wallet_interaction.every_month_stat(wallet_interaction.MONTH_DICT)
    answer = "Ваші помісячні витрати наступні:\n\n"
    for key, value in every_month_statistics.items():
        answer = answer + f" > За {key} ви витратили {value} грн.\n"
    await message.answer(answer + (f"\nНещодавні витрати: /last_expenses\n"
         f"Витрати за сьогодні: /today_stat\n"
         f"Загалом у цьому місяці: /month_stat\n"))


@dp.message_handler(commands=['last_expenses'])
async def last_expenses(message: types.Message):
    """Цей хендлер буде визваний, коли користувач введе `/last_expenses`"""

    last = wallet_interaction.last_exp()
    await message.answer(last)


@dp.message_handler()
async def add_expense(message: types.Message):
    """Цей хендлер буде визваний, коли користувач почне вводити будь-яке повідомлення"""

    try:
        expense_addition = wallet_interaction.add_expense(message.text)
        await message.answer(f"Витрата додана: {expense_addition.category_name} "
                             f"-- {expense_addition.amount} грн")
    except exception.NotCorrectMessage as err:
        await message.reply(f"{err}")
    daily = wallet_interaction.check_daily()
    if daily:
        await message.answer(daily)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
