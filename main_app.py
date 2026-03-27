import customtkinter as ctk
import pyperclip
import time
import random
import string
from threading import Thread
from generator import generate_secure_password 
from tkinter import messagebox

# Librerie per il Background e System Tray
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw

class SandPassApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SandPass - Ultimate Vault")
        self.geometry("450x570") 
        ctk.set_appearance_mode("dark")
        
        # --- PROTOCOLLO CHIUSURA (Background) ---
        self.protocol('WM_DELETE_WINDOW', self.withdraw_to_tray)
        
        # --- STATO ---
        self.is_active = False

        # --- UI ELEMENTS ---
        self.label = ctk.CTkLabel(self, text="SANDPASS", font=ctk.CTkFont(size=26, weight="bold"))
        self.label.pack(pady=(20, 10))

        # Display Password
        self.pass_entry = ctk.CTkEntry(self, width=350, height=45, justify="center", font=ctk.CTkFont(size=20, weight="bold"))
        self.pass_entry.insert(0, "********")
        self.pass_entry.configure(state="readonly")
        self.pass_entry.pack(pady=10)

        # --- SETTINGS FRAME ---
        self.settings_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.settings_frame.pack(pady=10, padx=20, fill="x")

        # 1. Slider Lunghezza Password
        self.len_label = ctk.CTkLabel(self.settings_frame, text="Lunghezza: 16 caratteri")
        self.len_label.pack()
        self.len_slider = ctk.CTkSlider(self.settings_frame, from_=8, to=32, number_of_steps=24, command=self.update_len_label)
        self.len_slider.set(16)
        self.len_slider.pack(pady=(0, 15))

        # 2. Checkbox Opzioni
        self.check_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        self.check_frame.pack()
        
        self.symbol_var = ctk.BooleanVar(value=True)
        self.num_var = ctk.BooleanVar(value=True)
        
        self.cb_symbols = ctk.CTkCheckBox(self.check_frame, text="Simboli", variable=self.symbol_var)
        self.cb_symbols.grid(row=0, column=0, padx=10)
        
        self.cb_nums = ctk.CTkCheckBox(self.check_frame, text="Numeri", variable=self.num_var)
        self.cb_nums.grid(row=0, column=1, padx=10)

        # --- TIMER AREA ---
        self.timer_info_label = ctk.CTkLabel(self, text="Durata Vault: 30 secondi", font=ctk.CTkFont(size=12))
        self.timer_info_label.pack(pady=(20, 0))
        
        self.time_slider = ctk.CTkSlider(self, from_=5, to=120, number_of_steps=23, command=self.update_timer_label)
        self.time_slider.set(30)
        self.time_slider.pack(pady=10)

        self.countdown_bar = ctk.CTkProgressBar(self, width=350, height=12, progress_color="#e74c3c")
        self.countdown_bar.set(0)
        self.countdown_bar.pack(pady=10)

        self.countdown_text = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=14, weight="bold"))
        self.countdown_text.pack()

        # Bottoni
        self.gen_btn = ctk.CTkButton(self, text="GENERA & COPIA", command=self.start_vault_session, 
                                     fg_color="#3498db", hover_color="#2980b9", width=200, height=45, font=ctk.CTkFont(size=15, weight="bold"))
        self.gen_btn.pack(pady=20)

        self.status_label = ctk.CTkLabel(self, text="L'app continuerà a girare in background", text_color="gray")
        self.status_label.pack(side="bottom", pady=10)

        # Avvio Thread per l'icona nella Tray
        Thread(target=self.setup_tray, daemon=True).start()

    # --- LOGICA SYSTEM TRAY ---
    def setup_tray(self):
        # Crea un'icona temporanea (un quadrato blu)
        icon_image = Image.new('RGB', (64, 64), color=(52, 152, 219))
        d = ImageDraw.Draw(icon_image)
        d.rectangle([16, 16, 48, 48], fill=(255, 255, 255))

        menu = (item('Mostra SandPass', self.show_window), item('Chiudi Definitivamente', self.quit_app))
        self.tray_icon = pystray.Icon("SandPass", icon_image, "SandPass Vault", menu)
        self.tray_icon.run()

    def withdraw_to_tray(self):
        self.withdraw() # Nasconde la finestra ma non chiude il processo

    def show_window(self):
        self.deiconify() # Ripristina la finestra

    def quit_app(self):
        self.tray_icon.stop()
        self.destroy()

    # --- HELPERS ---
    def update_len_label(self, val):
        self.len_label.configure(text=f"Lunghezza: {int(val)} caratteri")

    def update_timer_label(self, val):
        self.timer_info_label.configure(text=f"Durata Vault: {int(val)} secondi")

    def start_vault_session(self):
        self.is_active = False # Ferma thread precedenti
        time.sleep(0.1)

        # Prendi impostazioni
        length = int(self.len_slider.get())
        use_sym = self.symbol_var.get()
        use_num = self.num_var.get()
        duration = int(self.time_slider.get())

        # Genera usando il file esterno generator.py
        new_pass = generate_secure_password(length=length, use_symbols=use_sym, use_numbers=use_num)
        
        # Mostra
        self.pass_entry.configure(state="normal")
        self.pass_entry.delete(0, "end")
        self.pass_entry.insert(0, new_pass)
        self.pass_entry.configure(state="readonly")
        pyperclip.copy(new_pass)
        
        # Countdown
        self.is_active = True
        Thread(target=self.run_countdown, args=(duration,), daemon=True).start()

    def run_countdown(self, duration):
        total = duration
        while duration >= 0 and self.is_active:
            self.after(0, lambda d=duration, p=(duration/total): self.update_ui(d, p))
            time.sleep(1)
            duration -= 1
        
        if self.is_active:
            self.after(0, self.clear_vault)
            self.is_active = False

    def update_ui(self, sec, prog):
        self.countdown_text.configure(text=f"Distruzione tra: {sec}s")
        self.countdown_bar.set(prog)
        self.status_label.configure(text="VAULT ATTIVO (Anche se chiudi questa finestra)", text_color="#3498db")

    def clear_vault(self):
        # 1. Pulisce tutto
        pyperclip.copy("") 
        self.pass_entry.configure(state="normal")
        self.pass_entry.delete(0, "end")
        self.pass_entry.insert(0, "********")
        self.pass_entry.configure(state="readonly")
        
        self.countdown_bar.set(0)
        self.countdown_text.configure(text="!!! SCADUTA !!!", text_color="#e74c3c")
        self.status_label.configure(text="Dati eliminati per sicurezza.", text_color="#e74c3c")

        # Se la finestra è nascosta, la riportiamo su per mostrare l'errore
        self.deiconify()

        # 2. MOSTRA L'ERRORE CRITICO A SCHERMO
        messagebox.showerror(
            title="ERRORE CRITICO - SandPass", 
            message="LA PASSWORD È SCADUTA!\n\nI dati negli appunti e nel vault sono stati distrutti correttamente."
        )

if __name__ == "__main__":
    app = SandPassApp()
    app.mainloop()