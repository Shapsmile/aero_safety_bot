import sqlite3
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, Bot, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

from config import token
from data_base_func import escape_markdown_v2, get_all_sections, get_next_point, get_point_by_id, get_points_by_section, get_previous_point, double_newlines

# Токен доступа
TOKEN = token

# Адрес базы данных
data_base = "db/aerological_safety.db"

# Функция для отправки текста пункта и создания кнопок
def send_point_text(update, context, point_id):
    point_text = get_point_by_id(point_id, data_base)
    
    if point_text:
        # Экранируем текст для MarkdownV2
        point_text = escape_markdown_v2(point_text)
        point_text = double_newlines(point_text)
        
        # Получаем номера предыдущего и следующего пунктов
        prev_point_id = get_previous_point(point_id, data_base)
        next_point_id = get_next_point(point_id, data_base)
        
        # Создаем кнопки для предыдущего и следующего пунктов
        keyboard = []
        if prev_point_id:
            keyboard.append([InlineKeyboardButton(f'Предыдущий пункт: {prev_point_id}', callback_data=str(prev_point_id))])
        if next_point_id:
            keyboard.append([InlineKeyboardButton(f'Следующий пункт: {next_point_id}', callback_data=str(next_point_id))])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Отправляем сообщение с поддержкой Markdown и кнопками
        update.message.reply_text(f'{point_text}', reply_markup=reply_markup, parse_mode='MarkdownV2')
    else:
        update.message.reply_text(f'Пункт с номером {point_id} не найден в базе данных.')

# Функция для обработки номеров пунктов
def handle_point_request(update: Update, context: CallbackContext) -> None:
    message_text = update.message.text.strip()
    try:
        # Пытаемся преобразовать сообщение в целое число
        point_id = int(message_text)
        send_point_text(update, context, point_id)
    except ValueError:
        update.message.reply_text('Пожалуйста, отправьте правильный номер пункта или раздела (например, "R1" для раздела 1).')
    except Exception as e:
        update.message.reply_text(f'Произошла ошибка: {e}')

# Функция для обработки нажатий на кнопки
def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    
    # Получаем идентификатор пункта из callback_data
    point_id = int(query.data)
    
    # Обновляем сообщение с новым пунктом
    query.edit_message_text(text=f'Получаю текст пункта {point_id}...')
    send_point_text(query, context, point_id)


def handle_sections(update: Update, context: CallbackContext) -> None:
    sections = get_all_sections(data_base)
    
    if sections:
        response = "Список всех разделов:\n\n"
        for section_id, section_text in sections:
            response += f'{section_id}. {section_text}\n'
        update.message.reply_text(response)
    else:
        update.message.reply_text('В базе данных нет разделов.')

# Новая функция для обработки команды /help
def handle_help(update: Update, context: CallbackContext) -> None:
    help_text = (
        "Доступные команды:\n\n"
        "/help - показать список команд.\n"
        "/sections - показать список всех разделов.\n"
        "Номер пункта - получить текст пункта по его номеру.\n"
        "Р и число от 1 до 11 без пробела - просмотр названия раздела\n"
        "и диапазон пунктов раздела."
    )
    update.message.reply_text(help_text)

# Функция для запуска бота
def main():
    # Создаем Updater и передаем ему токен доступа
    updater = Updater(TOKEN, use_context=True)
    
    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher
    
    # Обработчик для команды /help
    dp.add_handler(CommandHandler("help", handle_help))

    # Обработчик для команды /sections
    dp.add_handler(CommandHandler("sections", handle_sections))

    # Обработчик для сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_point_request))
    
    # Обработчик для нажатий на кнопки
    dp.add_handler(CallbackQueryHandler(button))

    # Запуск бота
    updater.start_polling()
    
    # Работаем до тех пор, пока не остановят
    updater.idle()

if __name__ == '__main__':
    main()
