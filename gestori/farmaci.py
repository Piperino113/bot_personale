from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
import logging

async def comando_farmaci(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info("Comando /farmaci ricevuto")

    tastiera = [
        [KeyboardButton("Terapie")],
        [KeyboardButton("Scorte")],
        [KeyboardButton("Inventario")],
        [KeyboardButton("Eventi medici")]
    ]
    markup = ReplyKeyboardMarkup(tastiera, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Seleziona un'opzione:", reply_markup=markup)
