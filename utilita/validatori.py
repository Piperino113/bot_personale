from datetime import datetime

def valida_data(data_stringa):
    try:
        datetime.strptime(data_stringa, "%d/%m/%Y")
        return True
    except ValueError:
        return False
