from io import BytesIO

from aiogram import F, Router, types, flags
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile
from aiogram.types import InputFile

from src.tg_core.tg_front import keyboard_button as kb
from src.tg_core.tg_front.text import TextTypes
from src.vision_utils.image_handler import ImageHandler
from src.exec_model import model_exec
from .states import PState


router = Router()

@router.message(Command("start"))
async def start_handler(msg: Message):
    await msg.answer(TextTypes.GREET.format(name=msg.from_user.full_name), reply_markup=kb.start_buttons)

@router.message(F.text == kb.ButtonTypes.LOAD_IMAGE)
async def load_image(msg: Message, state: FSMContext):
    await msg.answer(TextTypes.INPUT_IMG)
    await state.set_state(PState.load_image)

@router.message(PState.load_image)
@flags.chat_action(TextTypes.EXEC_IMAGE)
async def loading_image(msg: Message, state: FSMContext):
    if msg.photo:
        
        photo = msg.photo

        await msg.answer(TextTypes.SUCCESSFUL_IMAGE_LOAD)

        file_id = photo[-1].file_id
        file = await msg.bot.get_file(file_id)
        file_bytes = await msg.bot.download(file.file_id, destination=BytesIO())
        image_file = handle_image(file_bytes)

        await msg.answer_photo(photo=image_file)
        await state.clear()

    else:
        await msg.answer(TextTypes.UNSUCCESSFUL_IMAGE_LOAD)

def handle_image(file_bytes: bytes):
    image = ImageHandler.bytesio_decode(file_bytes)
    image = model_exec(image)
    image = ImageHandler.image_to_bytesIO(image)

    image_file = BufferedInputFile(image.getvalue(), filename="file.jpg")
    return image_file
