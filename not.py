import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import os

TOKEN = '7443324044:AAH-_kn6FNUI4Q43MfKVnp9M-0B4i7HPLJU'
bot = telebot.TeleBot(TOKEN)

# Admin kullanıcı ID'sini buraya girin
ADMIN_ID = 6840212721  # Bunu kendi Telegram ID'nizle değiştirin
LOG_GROUP_ID = -1001948236041  # Bu kısmı kendi log grubunuzun ID'si ile değiştirin

# PDF dosyalarını saklamak için bir sözlük
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# PDF verilerini saklama yapısını güncelle
pdf_data = {
    "TYT": {
        "Türkçe": [],
        "Matematik": [],
        "Sosyal": [],
        "Fen Bilimleri": []
    },
    "AYT": {
        "Edebiyat-Sosyal": [],
        "Matematik-Fen Bilimleri": []
    },
    "KPSS": []
}

def gen_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 3
    markup.add(
        InlineKeyboardButton("TYT", callback_data="tyt_menu"),
        InlineKeyboardButton("AYT", callback_data="ayt_menu"),
        InlineKeyboardButton("KPSS", callback_data="kpss")
    )
    return markup

def gen_tyt_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("Türkçe", callback_data="tyt_turkce"),
        InlineKeyboardButton("Matematik", callback_data="tyt_matematik"),
        InlineKeyboardButton("Sosyal", callback_data="tyt_sosyal"),
        InlineKeyboardButton("Fen Bilimleri", callback_data="tyt_fen")
    )
    markup.add(InlineKeyboardButton("Ana Menü", callback_data="main_menu"))
    return markup

def gen_ayt_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("Edebiyat-Sosyal", callback_data="ayt_edebiyat_sosyal"),
        InlineKeyboardButton("Matematik-Fen Bilimleri", callback_data="ayt_matematik_fen")
    )
    markup.add(InlineKeyboardButton("Ana Menü", callback_data="main_menu"))
    return markup

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "tyt_menu":
        bot.edit_message_text("TYT alt kategorilerini seçin:", 
                              call.message.chat.id, 
                              call.message.message_id, 
                              reply_markup=gen_tyt_markup())
    elif call.data == "ayt_menu":
        bot.edit_message_text("AYT alt kategorilerini seçin:", 
                              call.message.chat.id, 
                              call.message.message_id, 
                              reply_markup=gen_ayt_markup())
    elif call.data == "main_menu":
        bot.edit_message_text("Ana menüye dönüldü. Lütfen bir sınav türü seçin:", 
                              call.message.chat.id, 
                              call.message.message_id, 
                              reply_markup=gen_markup())
    elif call.data.startswith("tyt_") or call.data.startswith("ayt_"):
        send_pdfs(call)
    elif call.data == "kpss":
        send_pdfs(call)
    elif call.data.startswith("add_"):
        add_pdf(call)

def send_pdfs(call):
    if call.data == "kpss":
        exam_type = "KPSS"
        category = "KPSS"
    else:
        exam_type, category = call.data.split("_", 1)
        exam_type = exam_type.upper()
        category = category.replace("_", " ").title()
    
    bot.answer_callback_query(call.id, f"{exam_type} {category} notları gönderiliyor...")
    if exam_type == "KPSS":
        pdfs = pdf_data[exam_type]
    else:
        pdfs = pdf_data[exam_type][category]
    
    if pdfs:
        for pdf_id in pdfs:
            bot.send_document(call.message.chat.id, pdf_id)
    else:
        bot.send_message(call.message.chat.id, f"Henüz {exam_type} {category} için PDF eklenmemiş.")

def add_pdf(call):
    exam_type, category = call.data.split("_")[1:]
    exam_type = exam_type.upper()
    category = category.replace("_", " ").title()
    msg = bot.send_message(call.message.chat.id, f"{exam_type} {category} için PDF file ID'sini gönderin.")
    bot.register_next_step_handler(msg, process_pdf_id, exam_type, category)

def process_pdf_id(message, exam_type, category):
    file_id = message.text.strip()
    if exam_type == "KPSS":
        pdf_data[exam_type].append(file_id)
    else:
        pdf_data[exam_type][category].append(file_id)
    save_data()
    bot.reply_to(message, f"{exam_type} {category} için yeni PDF ID eklendi: {file_id}")
    print(f"Yeni PDF ID eklendi: {exam_type} - {category} - {file_id}")

bot.polling()
