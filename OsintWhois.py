import os
import tkinter as tk
import threading
import socket
import whois
import dns.resolver
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageTk, ImageDraw, ImageFont

def get_ip(domain):
    try:
        ip = socket.gethostbyname(domain)
        return ip
    except Exception as e:
        return f"Error mendapatkan IP: {e}"

def get_whois(domain):
    try:
        w = whois.whois(domain)
        return w
    except Exception as e:
        return f"Error pada WHOIS: {e}"

def get_dns_records(domain, record_type):
    try:
        answers = dns.resolver.resolve(domain, record_type)
        records = [str(rdata) for rdata in answers]
        return records
    except Exception as e:
        return f"Error pada DNS {record_type}: {e}"

def get_http_headers(domain):
    try:
        url = f"http://{domain}"
        response = requests.get(url, timeout=10)
        return response.headers
    except Exception as e:
        return f"Error mendapatkan HTTP Headers: {e}"

def get_website_title(domain):
    try:
        url = f"http://{domain}"
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        if soup.title:
            return soup.title.string.strip()
        else:
            return "Judul tidak ditemukan."
    except Exception as e:
        return f"Error mengambil title: {e}"

# Fungsi untuk membuat background rounded
def create_rounded_background_image(width, height, radius, color):
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((0, 0, width, height), radius=radius, fill=color)
    return ImageTk.PhotoImage(image)

# Fungsi untuk membuat gambar tombol rounded dengan teks
def create_rounded_button_image(width, height, radius, color, text, text_color="#ffffff", font_path=None, font_size=32):
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((0, 0, width, height), radius=radius, fill=color)
    
    try:
        if font_path:
            font = ImageFont.truetype(font_path, font_size)
        else:
            try:
                font = ImageFont.truetype("arialbd.ttf", font_size)
            except Exception:
                font = ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()
    
    # Menggunakan textbbox untuk mendapatkan ukuran teks
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_x = (width - text_width) // 2
    text_y = (height - text_height) // 2
    draw.text((text_x, text_y), text, font=font, fill=text_color)
    
    return ImageTk.PhotoImage(image)

# Kelas RoundedEntry untuk tampilan input dengan sudut melengkung
class RoundedEntry(tk.Canvas):
    def __init__(self, parent, width=300, height=40, radius=20, bg_color="#1e1e1e", **kwargs):
        super().__init__(parent, width=width, height=height, bg="#121212", bd=0, highlightthickness=0, relief="flat")
        self.bg_image = create_rounded_background_image(width, height, radius, bg_color)
        self.create_image(0, 0, image=self.bg_image, anchor="nw")
        self.entry = tk.Entry(self, bd=0, bg=bg_color, fg="#e0e0e0",
                              insertbackground="#e0e0e0", font=("Helvetica", 12),
                              highlightthickness=0, relief="flat", **kwargs)
        self.create_window(5, 5, anchor="nw", window=self.entry, width=width-10, height=height-10)
        
    def get(self):
        return self.entry.get()
    
    def insert(self, index, value):
        self.entry.insert(index, value)
    
    def bind_entry(self, event, handler):
        self.entry.bind(event, handler)

# Kelas RoundedText untuk tampilan output dengan sudut melengkung
class RoundedText(tk.Canvas):
    def __init__(self, parent, width=500, height=300, radius=20, bg_color="#1e1e1e", **kwargs):
        super().__init__(parent, width=width, height=height, bg="#121212", bd=0, highlightthickness=0, relief="flat")
        self.bg_image = create_rounded_background_image(width, height, radius, bg_color)
        self.create_image(0, 0, image=self.bg_image, anchor="nw")
        self.text = tk.Text(self, bd=0, bg=bg_color, fg="#e0e0e0",
                            insertbackground="#e0e0e0", font=("Helvetica", 10),
                            highlightthickness=0, relief="flat", **kwargs)
        self.create_window(5, 5, anchor="nw", window=self.text, width=width-10, height=height-10)
        
    def get(self, index1, index2):
        return self.text.get(index1, index2)
    
    def insert(self, index, text):
        self.text.insert(index, text)
    
    def delete(self, index1, index2=None):
        self.text.delete(index1, index2)
    
    def config(self, **kwargs):
        self.text.config(**kwargs)

# Kelas utama GUI
class OSINTGUI:
    def __init__(self, master):
        self.master = master
        master.title("OSINT Tool - By Keltrox")
        master.geometry("600x750")
        master.resizable(False, False)
        master.configure(bg="#121212")
        
        # Menampilkan logo di bagian atas GUI
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            logo_path = os.path.join(base_dir, "images", "logo.png")
            if not os.path.exists(logo_path):
                raise FileNotFoundError(f"File logo tidak ditemukan di {logo_path}")
            image = Image.open(logo_path)
            image = image.resize((300, 300), Image.LANCZOS)
            self.logo_img = ImageTk.PhotoImage(image)
            self.logo_label = tk.Label(master, image=self.logo_img, bg="#121212", bd=0, highlightthickness=0)
            self.logo_label.pack(side=tk.TOP, pady=10)
        except Exception as e:
            print("Logo tidak dapat dimuat:", e)
        
        # Label input domain
        self.domain_label = tk.Label(master, text="Masukkan Domain:",
                                     bg="#121212", fg="#e0e0e0", font=("Helvetica", 12), bd=0, highlightthickness=0)
        self.domain_label.pack(pady=5)
        
        # RoundedEntry sebagai kolom input
        self.domain_entry = RoundedEntry(master, width=400, height=40, radius=10, bg_color="#1e1e1e")
        self.domain_entry.pack(pady=5)
        self.domain_entry.bind_entry("<Return>", lambda event: self.run_osint())
        
        # Tombol OSINT dengan tampilan rounded (menggunakan Label dengan gambar)
        btn_width = 180
        btn_height = 30
        btn_radius = 10
        btn_color = "#ff0000"  # Merah
        btn_text = "Jalankan OSINT"
        self.button_image = create_rounded_button_image(btn_width, btn_height, btn_radius, btn_color, btn_text, font_size=32)
        self.run_button = tk.Label(master, image=self.button_image, bg="#121212", cursor="hand2", bd=0, highlightthickness=0)
        self.run_button.pack(pady=5)
        self.run_button.bind("<Button-1>", lambda event: self.run_osint())
        
        # RoundedText sebagai kolom output
        self.output_text = RoundedText(master, width=400, height=250, radius=10, bg_color="#1e1e1e")
        self.output_text.pack(pady=10)
        
    def append_text(self, text):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, text)
        self.output_text.config(state=tk.DISABLED)
        self.output_text.text.see(tk.END)
        
    def run_osint(self):
        thread = threading.Thread(target=self.run_osint_task)
        thread.daemon = True
        thread.start()
        
    def run_osint_task(self):
        domain = self.domain_entry.get().strip()
        if not domain:
            self.append_text("Mohon masukkan domain.\n")
            return
        
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.config(state=tk.DISABLED)
        
        self.append_text(f"Analisis untuk domain: {domain}\n\n")
        self.append_text("IP Address:\n")
        ip = get_ip(domain)
        self.append_text(f"{ip}\n\n")
        self.append_text("WHOIS Information:\n")
        whois_info = get_whois(domain)
        self.append_text(f"{whois_info}\n\n")
        self.append_text("DNS Records:\n")
        for record_type in ["A", "MX", "NS", "TXT"]:
            self.append_text(f"{record_type} Records:\n")
            records = get_dns_records(domain, record_type)
            if isinstance(records, list):
                for record in records:
                    self.append_text(f"  {record}\n")
            else:
                self.append_text(f"  {records}\n")
            self.append_text("\n")
        self.append_text("HTTP Headers:\n")
        headers = get_http_headers(domain)
        if isinstance(headers, dict):
            for key, value in headers.items():
                self.append_text(f"  {key}: {value}\n")
        else:
            self.append_text(f"  {headers}\n")
        self.append_text("\n")
        self.append_text("Website Title:\n")
        title = get_website_title(domain)
        self.append_text(f"{title}\n")

def main():
    root = tk.Tk()
    app = OSINTGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
