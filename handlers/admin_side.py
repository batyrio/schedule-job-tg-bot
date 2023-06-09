from aiogram import types
from create_bot import bot, dp
from handlers.states import NewsStates
from aiogram.dispatcher import FSMContext
from data_base import sqlite_db
from keyboards import inline_kb, delete_kb
from aiogram.dispatcher.filters import Text



async def add_proxy_data(state, data):
    async with state.proxy() as proxy:
        for k,v in data.items():
            proxy[k] = v


@dp.message_handler(commands=['create_news'])
async def create_news(message: types.Message):
    await NewsStates.title.set()
    await message.reply('Отправьте заголовок новости', reply=False)


@dp.message_handler(state=NewsStates.title)
async def state_title_news(message: types.Message, state: FSMContext):
    await add_proxy_data(state, {'title': message.text})
    await message.reply('Теперь введите содержание новости', reply=False)
    await NewsStates.next()


@dp.message_handler(state=NewsStates.content)
async def state_content_news(message: types.Message, state: FSMContext):
    await add_proxy_data(state, {'content': message.text})
    await message.reply('Отправьте фото к новости', reply=False)
    await NewsStates.next()


@dp.message_handler(state=NewsStates.image, content_types=['photo'])
async def state_image_news(message: types.Message, state: FSMContext):
    await add_proxy_data(state, {'image': message.photo[0].file_id})
    await sqlite_db.add_news(state)
    await message.reply('Новость успешно создана!', reply=False)
    await state.finish()


@dp.message_handler(commands=['delete_news'])
async def delete_news(message: types.Message):
    news = await sqlite_db.get_news()
    for i in news:
        await bot.send_photo(message.chat.id, i[3], f'*НОВОСТЬ*\n\n {i[1]}\n{i[2]}',
                             parse_mode='Markdown', reply_markup=inline_kb.create_delete_news_keyboard(i[0]))


@dp.callback_query_handler(Text(startswith='news '))
async def callback_delete_news(callback: types.CallbackQuery):
    cb_data = callback.data.replace('news ', '')
    await sqlite_db.delete_news(cb_data)
    await delete_kb.delete_inline_keyboard(callback.message)
    await callback.answer('Новость удалена!')
    await bot.send_message(callback.message.chat.id, 'Новость успешно удалена!')












