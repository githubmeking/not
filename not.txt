import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import os

TOKEN = '6975695586:AAFzBdECsA7Xr6cFCz8jup0x7N3F8H695lA'
bot = telebot.TeleBot(TOKEN)

# Admin kullanıcı ID'sini buraya girin
ADMIN_ID = 6840212721  # Bunu kendi Telegram ID'nizle değiştirin

# PDF dosyalarını saklamak için bir sözlük
pdf_data = {"TYT": [], "AYT": [], "KPSS": []}

# Verileri dosyaya kaydetme ve yükleme fonksiyonları
def save_data():
    try:
        with open('pdf_data.json', 'w') as f:
            json.dump(pdf_data, f)
        print("Veri başarıyla kaydedildi.")
    except Exception as e:
        print(f"Veri kaydedilirken hata oluştu: {e}")

def load_data():
    global pdf_data
    try:
        if os.path.exists('pdf_data.json'):
            with open('pdf_data.json', 'r') as f:
                pdf_data = json.load(f)
            print("Veri başarıyla yüklendi.")
        else:
            print("Veri dosyası bulunamadı. Yeni bir dosya oluşturulacak.")
            save_data()
    except Exception as e:
        print(f"Veri yüklenirken hata oluştu: {e}")

load_data()

def gen_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 3
    markup.add(
        InlineKeyboardButton("TYT", callback_data="tyt"),
        InlineKeyboardButton("AYT", callback_data="ayt"),
        InlineKeyboardButton("KPSS", callback_data="kpss")
    )
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Hoş geldiniz! Lütfen bir sınav türü seçin:", reply_markup=gen_markup())

@bot.message_handler(commands=['admin'])
def admin_command(message):
    if message.from_user.id == ADMIN_ID:
        markup = InlineKeyboardMarkup()
        markup.row_width = 3
        markup.add(
            InlineKeyboardButton("TYT Ekle", callback_data="add_tyt"),
            InlineKeyboardButton("AYT Ekle", callback_data="add_ayt"),
            InlineKeyboardButton("KPSS Ekle", callback_data="add_kpss")
        )
        bot.send_message(message.chat.id, "Admin paneline hoş geldiniz. Ne yapmak istersiniz?", reply_markup=markup)
    else:
        bot.reply_to(message, "Bu komutu kullanma yetkiniz yok.")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data in ["tyt", "ayt", "kpss"]:
        send_pdfs(call)
    elif call.data.startswith("add_"):
        add_pdf(call)

def send_pdfs(call):
    exam_type = call.data.upper()
    bot.answer_callback_query(call.id, f"{exam_type} notları gönderiliyor...")
    if pdf_data[exam_type]:
        for pdf_id in pdf_data[exam_type]:
            bot.send_document(call.message.chat.id, pdf_id)
    else:
        bot.send_message(call.message.chat.id, f"Henüz {exam_type} için PDF eklenmemiş.")

def add_pdf(call):
    exam_type = call.data.split("_")[1].upper()
    msg = bot.send_message(call.message.chat.id, f"{exam_type} için PDF file ID'sini gönderin.")
    bot.register_next_step_handler(msg, process_pdf_id, exam_type)

def process_pdf_id(message, exam_type):
    file_id = message.text.strip()
    pdf_data[exam_type].append(file_id)
    save_data()
    bot.reply_to(message, f"{exam_type} için yeni PDF ID eklendi: {file_id}")
    print(f"Yeni PDF ID eklendi: {exam_type} - {file_id}")

bot.polling()