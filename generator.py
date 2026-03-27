import random
import string

def generate_secure_password(length=16, use_symbols=True, use_numbers=True):
    """
    Genera una password basata esattamente sulle scelte dell'utente.
    """
    pool = ""
    
    if use_numbers:
        pool += string.digits
        
    if use_symbols:
        pool += "!@#$%^&*()-_=+"

    # Se l'utente ha tolto numeri e simboli, usa solo lettere
    # Se invece ha attivato qualcosa, usa solo quello (senza lettere extra)
    if not pool:
        pool = string.ascii_letters
    elif not (use_numbers and use_symbols):
        # Se vuoi solo numeri, non aggiungiamo lettere di default
        pass 
    
    # Se vuoi permettere il mix Lettere + Numeri quando entrambi sono attivi, 
    # aggiungi le lettere solo se l'utente non ha specificato di volere "solo" una cosa.
    # Ma per essere sicuri che faccia quello che chiedi:
    
    # Versione super-precisa:
    final_pool = ""
    if use_numbers: final_pool += string.digits
    if use_symbols: final_pool += "!@#$%^&*()-_=+"
    
    # Se non hai selezionato nulla, il default sono le lettere
    if not final_pool:
        final_pool = string.ascii_letters

    password = "".join(random.choice(final_pool) for _ in range(length))
    return password