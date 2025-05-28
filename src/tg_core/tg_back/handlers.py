from io import BytesIO

from aiogram import F, Router, types, flags
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile
from aiogram.types import InputFile

from src.tg_core.tg_front import keyboard_button as kb
from src.tg_core.tg_front import text
from src.vision_utils.image_handler import ImageHandler
from src.exec_model import model_exec
from .states import PState


router = Router()

#TODO Пофиксить "Выйти в меню" после захода в функцию не выходит из-за состояние мб
@router.message(Command("start"))
async def start_handler(msg: Message):
    await msg.answer(text.greet.format(name=msg.from_user.full_name), reply_markup=kb.menu)


@router.callback_query(F.data == 'load_image')
async def input_image(callback: CallbackQuery, state: FSMContext):
    await state.set_state(PState.load_image)
    await callback.message.edit_text(text.input_img)
    await callback.message.answer(text.input_exit, reply_markup=kb.exit_kb)


@router.message(PState.load_image)
@flags.chat_action("Обрабатываем изображение")
async def loading_image(msg: Message | CallbackQuery, state: FSMContext):

    if msg.photo:
        photo = msg.photo

        print("photo", photo)

        await msg.answer("Изображение успешно загружено!")

        file_id = photo[-1].file_id
        file = await msg.bot.get_file(file_id)
        file_bytes = await msg.bot.download(file.file_id, destination=BytesIO())

        image = ImageHandler.bytesio_decode(file_bytes)
        image = model_exec(image)
        image = ImageHandler.image_to_bytesIO(image)

        image_file = BufferedInputFile(image.getvalue(), filename="file.jpg")
        await msg.answer_photo(photo=image_file)


    else:
        await msg.answer("Пожалуйста, отправьте одно изображение")

async def menu(msg: Message):
    await msg.answer(text.menu, reply_markup=kb.menu)
