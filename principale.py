# import standard
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)


# import personalizzati
from impostazioni import TOKEN
from gestori.auto import auto, gestione_risposte_auto
from gestori.auto import callback_auto

# creo il bot
application = Application.builder().token(TOKEN).build()

# Handlers
application.add_handler(CommandHandler("auto", auto))  # chiama la funzione auto() quando arriva /auto
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, gestione_risposte_auto))  # gestisce i messaggi successivi
application.add_handler(CallbackQueryHandler(callback_auto, pattern=r'^usa_data:'))
application.add_handler(CallbackQueryHandler(callback_auto))

# Avvio il bot
application.run_polling()
if __name__ == "__main__":
    main()  # o avvia il tuo codice qui