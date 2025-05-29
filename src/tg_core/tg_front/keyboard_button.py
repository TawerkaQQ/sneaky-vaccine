from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

menu = [
    [InlineKeyboardButton(text="🖼 Активировать токен", callback_data="activate_token")],
    [InlineKeyboardButton(text="🖼 Помощь", callback_data="activate_token"),
     InlineKeyboardButton(text="💳 Информация по токену", callback_data="token_info")],
    [InlineKeyboardButton(text="Обратная связь", callback_data="feed_back"),
     InlineKeyboardButton(text="Информация о системе", callback_data="info")],
    [InlineKeyboardButton(text="📝 Загрузить изображение", callback_data="load_image")]
]

menu = InlineKeyboardMarkup(inline_keyboard=menu)
exit_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="◀️ Выйти в меню")]], resize_keyboard=True)
iexit_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Выйти в меню", callback_data="menu")]])
