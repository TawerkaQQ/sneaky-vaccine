from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

class ButtonTypes:
    ACTIVATE_TOKEN = "🖼 Активировать токен"
    HELP = "🖼 Помощь"
    TOKEN_INFO = "💳 Информация по токену"
    FEEDBACK = "Обратная связь"
    SYSTEM_INFO = "Информация о системе"
    LOAD_IMAGE = "📝 Загрузить изображение"
    
    

start_buttons = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=ButtonTypes.ACTIVATE_TOKEN, callback_data=ButtonTypes.ACTIVATE_TOKEN)],
        [
            KeyboardButton(text=ButtonTypes.HELP, callback_data=ButtonTypes.HELP),
            KeyboardButton(text=ButtonTypes.TOKEN_INFO, callback_data=ButtonTypes.TOKEN_INFO),
        ],
        [
            KeyboardButton(text=ButtonTypes.FEEDBACK, callback_data=ButtonTypes.FEEDBACK),
            KeyboardButton(text=ButtonTypes.SYSTEM_INFO, callback_data=ButtonTypes.SYSTEM_INFO),
        ],
        [KeyboardButton(text=ButtonTypes.LOAD_IMAGE, callback_data=ButtonTypes.LOAD_IMAGE)],
    ]
)

