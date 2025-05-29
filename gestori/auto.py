from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime
from telegram.ext import CallbackQueryHandler, CallbackContext
from servizi.foglio_auto import (
    salva_dati_rifornimento,
    salva_dati_spese,
    salva_dati_chilometraggio,
)

async def auto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tastiera = [["Rifornimenti", "Spese", "Chilometraggio"]]
    reply_markup = ReplyKeyboardMarkup(tastiera, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Cosa vuoi registrare?", reply_markup=reply_markup)
    context.user_data["modalità_auto"] = True
    context.user_data["stato_auto"] = None

async def gestione_risposte_auto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("modalità_auto"):
        return

    testo = update.message.text
    stato = context.user_data.get("stato_auto")

    if testo == "Rifornimenti":
        context.user_data["tipo_operazione"] = "rifornimento"
        context.user_data["stato_auto"] = "attesa_data"

        oggi = datetime.now().strftime("%d/%m/%Y")
        tastiera = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"Usa data odierna: {oggi}", callback_data=f"usa_data:{oggi}")]
        ])

        await update.message.reply_text(
            "Inserisci la data (GG/MM/AAAA):\n\nOppure premi il pulsante per usare quella odierna.",
            reply_markup=tastiera
        )
        return

    if testo == "Spese":
        context.user_data["tipo_operazione"] = "Spese"
        context.user_data["stato_auto"] = "attesa_data"

        oggi = datetime.now().strftime("%d/%m/%Y")
        tastiera = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"Usa data odierna: {oggi}", callback_data=f"usa_data:{oggi}")]
        ])

        await update.message.reply_text(
            "Inserisci la data (GG/MM/AAAA):\n\nOppure premi il pulsante per usare quella odierna.",
            reply_markup=tastiera
        )
        return

    if testo == "Chilometraggio":
        context.user_data["tipo_operazione"] = "Chilometraggio"
        context.user_data["stato_auto"] = "attesa_data"

        oggi = datetime.now().strftime("%d/%m/%Y")
        tastiera = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"Usa data odierna: {oggi}", callback_data=f"usa_data:{oggi}")]
        ])

        await update.message.reply_text(
            "Inserisci la data (GG/MM/AAAA):\n\nOppure premi il pulsante per usare quella odierna.",
            reply_markup=tastiera
        )
        return

    if stato == "attesa_data":
        try:
            datetime.strptime(testo, "%d/%m/%Y")
            context.user_data["data"] = testo
            context.user_data["stato_auto"] = "attesa_km"
            await update.message.reply_text("Inserisci i km attuali:")
        except ValueError:
            await update.message.reply_text("⚠️ Formato data non valido. Inserisci la data come GG/MM/AAAA.")
        return

    if stato == "attesa_litri":
        context.user_data["litri"] = testo
        context.user_data["stato_auto"] = "attesa_euro"
        await update.message.reply_text("Inserisci l'importo speso in €:")
        return

    if stato == "attesa_euro":
        context.user_data["euro"] = testo
        context.user_data["stato_auto"] = "attesa_note"
        await update.message.reply_text("Vuoi aggiungere delle note? (Scrivi o lascia vuoto e invia)")
        return

    if stato == "attesa_note":
        context.user_data["note"] = testo
        context.user_data["stato_auto"] = "attesa_conferma_rifornimento"

        data = context.user_data["data"]
        km = context.user_data["km"]
        litri = context.user_data["litri"]
        euro = context.user_data["euro"]
        note = context.user_data["note"]

        tastiera = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Sì", callback_data="conferma_rifornimento")],
            [InlineKeyboardButton("❌ Annulla", callback_data="annulla")]
        ])

        await update.message.reply_text(
            f"Vuoi salvare il seguente rifornimento?\n\n"
            f"📅 Data: {data}\n"
            f"🚗 Km: {km}\n"
            f"⛽ Litri: {litri}\n"
            f"💶 Euro: {euro}\n"
            f"📝 Note: {note if note.strip() else '—'}",
            reply_markup=tastiera
        )
        return

    if stato == "attesa_km":
        context.user_data["km"] = testo
        if context.user_data["tipo_operazione"] == "rifornimento":
            context.user_data["stato_auto"] = "attesa_litri"
            await update.message.reply_text("Inserisci i litri riforniti:")
        elif context.user_data["tipo_operazione"] == "Spese":
            context.user_data["stato_auto"] = "attesa_descrizione"
            await update.message.reply_text("Inserisci una descrizione della spesa:")
        elif context.user_data["tipo_operazione"] == "Chilometraggio":
            dati = {
                "data": context.user_data["data"],
                "km": context.user_data["km"]
            }
            salva_dati_chilometraggio(dati)
            await update.message.reply_text("Chilometraggio salvato con successo.")
            context.user_data.clear()
        return

    if stato == "attesa_descrizione":
        context.user_data["descrizione"] = testo
        context.user_data["stato_auto"] = "attesa_euro_spesa"
        await update.message.reply_text("Inserisci l'importo in €:")
        return

    if stato == "attesa_conferma_spese" and testo.lower() == "conferma":
        salva_dati_spese(context.user_data)
        await update.message.reply_text("Dati spesa salvati!")
        context.user_data.clear()
        return

    if testo.lower() == "annulla":
        await update.message.reply_text("Operazione annullata.")
        context.user_data.clear()
        return

# 👇 NUOVA FUNZIONE PER GESTIRE IL PULSANTE "Usa data odierna"
async def callback_auto(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    if query.data == "conferma_rifornimento":
        salva_dati_rifornimento(
            context.user_data["data"],
            context.user_data["litri"],
            context.user_data["euro"],
            context.user_data["km"],
            context.user_data.get("note", "")
        )
        salva_dati_chilometraggio(
            context.user_data["data"],
            context.user_data["km"]
        )


        await query.edit_message_text("✅ Dati rifornimento salvati!")
        context.user_data.clear()


    if query.data == "annulla":
        await query.edit_message_text("❌ Operazione annullata.")
        context.user_data.clear()
