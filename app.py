import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackContext, CallbackQueryHandler
import movies_api

user_movie_data = {}
liked_movies = {}

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    create_game_button = InlineKeyboardButton("New game", callback_data="create_game")
    my_games_button = InlineKeyboardButton("My games", callback_data="my_games")
    keyboard = InlineKeyboardMarkup([[create_game_button], [my_games_button]])
    user_first_name = update.message.from_user.first_name
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Hello, {user_first_name}!\nI'm a bot that will help you find a movie that will fit everyone",
        reply_markup=keyboard
    )


async def button_click(update: Update, context: CallbackContext):
    query = update.callback_query
    user_choice = query.data
    if user_choice == "create_game":
        movies_data = movies_api.get_movie_data()  # Получаем список фильмов
        if movies_data:
            user_movie_data[query.from_user.id] = {
                'movies': movies_data,
                'current_index': 0  # Индекс текущего фильма
            }
            await display_movie(query)  # Отображаем первый фильм

    else:
        response_text = "Unknown choice."
        await query.answer()
        await query.message.edit_text(response_text)


async def display_movie(query):
    user_id = query.from_user.id
    if user_id in user_movie_data:
        user_data = user_movie_data[user_id]
        current_index = user_data['current_index']
        movies = user_data['movies']
        if current_index < len(movies):
            current_movie = movies[current_index]
            response_text = format_movie_info(current_movie)
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("Следующий фильм", callback_data="next_movie")],
                [InlineKeyboardButton("Нравица", callback_data="like this")]
            ])
            await query.answer()
            await query.message.edit_text(response_text, reply_markup=keyboard)
        else:
            response_text = "Больше фильмов нет."
            await query.answer()
            await query.message.edit_text(response_text)
    else:
        await query.answer("Начните новую игру сначала.")


async def next_movie_click(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == "like_movie":
        user_id = query.from_user.id
        if user_id in user_movie_data:
            user_data = user_movie_data[user_id]
            current_index = user_data['current_index']
            movies = user_data['movies']
            if current_index < len(movies):
                # Отметьте фильм как понравившийся (в вашем коде нужно добавить механизм для хранения "лайков" пользователя)
                user_data.setdefault('likes', []).append(movies[current_index])
                await query.answer("Вы поставили лайк этому фильму.")
        else:
            await query.answer("Начните новую игру сначала.")
        return
    await display_next_movie(query)

async def like_movie(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    if user_id in liked_movies:
        user_liked_movies = liked_movies[user_id]
        user_data = user_movie_data[user_id]
        current_index = user_data['current_index']
        movies = user_data['movies']
        if current_index < len(movies):
            liked_movie = movies[current_index]
            user_liked_movies.append(liked_movie)
            await query.answer("Вы отметили этот фильм как понравившийся.")
        else:
            await query.answer("Начните новую игру сначала.")
    else:
        await query.answer("Начните новую игру сначала.")

async def display_next_movie(query):
    user_id = query.from_user.id
    if user_id in user_movie_data:
        user_data = user_movie_data[user_id]
        current_index = user_data['current_index']
        movies = user_data['movies']
        current_index += 1
        if current_index < len(movies):
            user_data['current_index'] = current_index
            next_movie = movies[current_index]
            response_text = format_movie_info(next_movie)
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("Следующий фильм", callback_data="next_movie"),
                 InlineKeyboardButton("Лайк", callback_data="like_movie")]
            ])
            await query.answer()
            await query.message.edit_text(response_text, reply_markup=keyboard)
        else:
            response_text = "Больше фильмов нет."
            await query.answer()
            await query.message.edit_text(response_text)
    else:
        await query.answer("Начните новую игру сначала.")


def format_movie_info(movie):
    response_text = "Вот информация о фильме:\n"
    response_text += f"Название: {movie.get('title')}\n"
    response_text += f"Описание: {movie.get('overview')}\n"
    response_text += f"Рейтинг: {movie.get('popularity')}\n"

    return response_text


if __name__ == '__main__':
    application = ApplicationBuilder().token('6476526521:AAFiMoP4qnadP_iNUS5l0pOvlnAYM5vJ1O8').build()

    # Добавление обработчика команды /start
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    # Добавление обработчика нажатия на кнопку "New game"
    application.add_handler(CallbackQueryHandler(button_click, pattern="create_game"))

    # Добавление обработчика нажатия на кнопку "Следующий фильм"
    application.add_handler(CallbackQueryHandler(next_movie_click, pattern="next_movie"))

    # Добавление обработчика нажатия на кнопку "Нравится"
    application.add_handler(CallbackQueryHandler(like_movie, pattern="like_movie"))

    # Запуск бота
    application.run_polling()