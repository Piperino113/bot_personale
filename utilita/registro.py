import logging

def log(messaggio):
    print(f"[LOG] {messaggio}")

def avvia_logging():
    logging.basicConfig(
        filename="registro_bot.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logging.info("Logging avviato")
