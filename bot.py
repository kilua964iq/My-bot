import telebot
from telebot import types
import os
import time
import requests
import threading
import re
from pp_gate import Aizen as pp_check

# Bot Configuration
BOT_TOKEN = "8740209519:AAFPfns0Byh0vlkWwNxuNWAD8xBcXxsGjOI"
OWNER_ID = 1013384909
OWNER_USERNAME = "o83800"
OWNER_NAME = "Mustafa"

bot = telebot.TeleBot(BOT_TOKEN)

# Stop user dictionary for file checking
stopuser = {}

# Dictionary to track users currently checking files
users_checking_files = {}

# Anti-Spam: Track last check time for each user
user_last_check_time = {}
ANTI_SPAM_DELAY = 5  # seconds

# ============================================
# BIN Info Function
# ============================================

def get_bin_info(cc):
    """الحصول على معلومات BIN"""
    try:
        data_bin = requests.get('https://bins.antipublic.cc/bins/'+cc[:6], timeout=5).json()
        bank = data_bin.get('bank', 'Unknown')
        country = data_bin.get('country_name', 'Unknown')
        country_flag = data_bin.get('country_flag', '🌍')
        brand = data_bin.get('brand', 'Unknown')
        card_type = data_bin.get('type', 'Unknown')
        return bank, country, country_flag, brand, card_type
    except:
        return 'Unknown', 'Unknown', '🌍', 'Unknown', 'Unknown'

# ============================================
# Start Command
# ============================================

@bot.message_handler(commands=['start'])
def start_handler(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "User"
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📋 Commands", callback_data="commands"),
        types.InlineKeyboardButton("ℹ️ Info", callback_data="info")
    )
    
    text = f"""<b>
[<a href="https://t.me/o8380">ϟ</a>] Welcome to PayPal Donation Checker 🔥
- - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/o8380">ϟ</a>] Hello, {first_name}!
[<a href="https://t.me/o8380">ϟ</a>] Gateway: PayPal Donation ($1.00)
[<a href="https://t.me/o8380">ϟ</a>] Status: FREE ✨
- - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/o8380">ϟ</a>] Use /pp to check a card
[<a href="https://t.me/o8380">ϟ</a>] Upload .txt file for combo check
- - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/o8380">⌤</a>] Dev by: Mustafa - @o8380 🗣
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
[<a href="https://t.me/o8380">ϟ</a>] 📋 Commands List
- - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/o8380">ϟ</a>] /start - Start the bot
[<a href="https://t.me/o8380">ϟ</a>] /pp - Check single card
[<a href="https://t.me/o8380">ϟ</a>] Upload .txt - Combo check
- - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/o8380">ϟ</a>] Format: cc|mm|yy|cvv
- - - - - - - - - - - - - - - - - - - - - -
</b>"""
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, text, parse_mode="HTML")
        
    elif call.data == "info":
        text = f"""<b>
[<a href="https://t.me/o8380">ϟ</a>] ℹ️ Bot Info
- - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/o8380">ϟ</a>] 🌐 Gateway: PayPal Donation
[<a href="https://t.me/o8380">ϟ</a>] 💰 Amount: $1.00
[<a href="https://t.me/o8380">ϟ</a>] 💎 Status: FREE
- - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/o8380">ϟ</a>] 👨‍💻 Developer: Mustafa
[<a href="https://t.me/o8380">ϟ</a>] 📱 Username: @o8380
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
            bot.send_document(chat_id, f, caption=f"<b>🔥 Charged: {len(hits)}</b>", parse_mode="HTML")
        
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
            bot.send_document(chat_id, f, caption=f"<b>✅ Approved: {len(ccn)}</b>", parse_mode="HTML")
        
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
            bot.send_document(chat_id, f, caption=f"<b>❌ Declined: {len(dead)}</b>", parse_mode="HTML")
        
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
        
        # Anti-Spam check
        if user_id != OWNER_ID:
            current_time = time.time()
            if user_id in user_last_check_time:
                time_diff = current_time - user_last_check_time[user_id]
                if time_diff < ANTI_SPAM_DELAY:
                    remaining = int(ANTI_SPAM_DELAY - time_diff)
                    spam_msg = f"""<b>
[<a href="https://t.me/o8380">ϟ</a>] ⏳ Anti-Spam Protection
- - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/o8380">ϟ</a>] Please wait {remaining} seconds
- - - - - - - - - - - - - - - - - - - - - -
</b>"""
                    bot.reply_to(message, spam_msg, parse_mode="HTML")
                    return
            user_last_check_time[user_id] = current_time
        
        # Extract card
        cc = None
        try:
            parts = message.text.split(None, 1)
            if len(parts) > 1:
                cc = parts[1].strip()
        except:
            pass
        
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
            bot.reply_to(message, "<b>❌ Please use format:\n/pp card|month|year|cvv</b>", parse_mode="HTML")
            return
        
        if '|' not in cc or len(cc.split('|')) != 4:
            bot.reply_to(message, "<b>❌ Invalid card format!\nUse: /pp card|month|year|cvv</b>", parse_mode="HTML")
            return
        
        wait_msg = bot.reply_to(message, "<b>⏳ Checking your card...</b>", parse_mode="HTML")
        
        bank, country, country_flag, brand, card_type = get_bin_info(cc)
        
        start_time = time.time()
        
        try:
            result = pp_check(cc)
        except Exception as e:
            result = f"Error: {str(e)}"
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        if 'Charge' in str(result):
            status_emoji = '🔥'
            status_text = 'Charged $1'
            response_text = 'Charged 🔥'
        elif 'CVV' in str(result) or 'Insufficient' in str(result):
            status_emoji = '✅'
            status_text = 'CVV Match' if 'CVV' in str(result) else 'Insufficient Funds'
            response_text = f'{result} ✅'
        else:
            status_emoji = '❌'
            status_text = 'Declined'
            response_text = f'{result} ❌'
        
        result_msg = f"""<b>#PayPal_Donation ($1.00) [/pp] 🌟</b>
- - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/o8380">ϟ</a>] <b>Card:</b> <code>{cc}</code>
[<a href="https://t.me/o8380">ϟ</a>] <b>Response: {response_text}</b>
[<a href="https://t.me/o8380">ϟ</a>] <b>Status: {status_text}</b>
[<a href="https://t.me/o8380">ϟ</a>] <b>Taken: {execution_time:.1f} S.</b>
- - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/o8380">ϟ</a>] <b>Info: {brand} - {card_type}</b>
[<a href="https://t.me/o8380">ϟ</a>] <b>Bank: {bank}</b>
[<a href="https://t.me/o8380">ϟ</a>] <b>Country: {country} {country_flag}</b>
- - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/o8380">⎇</a>] <b>Req By: {first_name}</b>
- - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/o8380">⌤</a>] <b>Dev by: Mustafa - @o8380 🗣</b>"""
        
        bot.delete_message(message.chat.id, wait_msg.message_id)
        bot.send_message(message.chat.id, result_msg, parse_mode="HTML")
        
    except Exception as e:
        bot.reply_to(message, f"<b>❌ Error: {str(e)}</b>", parse_mode="HTML")

# ============================================
# File Handler - Combo Check
# ============================================

@bot.message_handler(content_types=['document'])
def document_handler(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "User"
    username = message.from_user.username or "NoUsername"
    
    if not message.document.file_name.endswith('.txt'):
        bot.reply_to(message, "<b>❌ Please upload a .txt file</b>", parse_mode="HTML")
        return
    
    if user_id in users_checking_files and users_checking_files[user_id].get('running'):
        bot.reply_to(message, "<b>❌ You already have an active session!</b>", parse_mode="HTML")
        return
    
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        content = downloaded_file.decode('utf-8', errors='ignore')
        
        lines = [l.strip() for l in content.split('\n') if l.strip()]
        cards = []
        
        for line in lines:
            if '|' in line and len(line.split('|')) >= 4:
                cards.append(line)
        
        if not cards:
            bot.reply_to(message, "<b>❌ No valid cards found in file!</b>", parse_mode="HTML")
            return
        
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
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("▶️ START", callback_data="combo_start"))
        
        text = f"""<b>Gateway: PayPal_Donation ($1.00)
By: @{username}
📁 Cards: {len(cards)}</b>"""
        
        bot.reply_to(message, text, parse_mode="HTML", reply_markup=markup)
        
    except Exception as e:
        bot.reply_to(message, f"<b>❌ Error: {str(e)}</b>", parse_mode="HTML")

def combo_check_thread(user_id, chat_id, msg_id, total, username):
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
        
        try:
            result = pp_check(card)
        except Exception as e:
            result = f"Error: {str(e)}"
        
        current_status = result
        
        if 'Charge' in str(result):
            session['charged'].append(card)
            parts = card.split('|')
            cc = parts[0].strip()
            bank, country, country_flag, brand, card_type = get_bin_info(cc)
            hit_msg = f"""<b>#PayPal_Donation ($1.00) 🔥 CHARGED</b>
- - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/o8380">ϟ</a>] <b>Card:</b> <code>{card}</code>
[<a href="https://t.me/o8380">ϟ</a>] <b>Response: Charged 🔥</b>
[<a href="https://t.me/o8380">ϟ</a>] <b>Status: Charged $1</b>
- - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/o8380">ϟ</a>] <b>Info: {brand} - {card_type}</b>
[<a href="https://t.me/o8380">ϟ</a>] <b>Bank: {bank}</b>
[<a href="https://t.me/o8380">ϟ</a>] <b>Country: {country} {country_flag}</b>
- - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/o8380">⎇</a>] <b>Req By: @{username}</b>
- - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/o8380">⌤</a>] <b>Dev by: Mustafa - @o8380 🗣</b>"""
            bot.send_message(chat_id, hit_msg, parse_mode="HTML")
        elif 'Insufficient' in str(result):
            session['approved'].append(card)
            parts = card.split('|')
            cc = parts[0].strip()
            bank, country, country_flag, brand, card_type = get_bin_info(cc)
            ccn_msg = f"""<b>#PayPal_Donation ($1.00) ✅ APPROVED</b>
- - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/o8380">ϟ</a>] <b>Card:</b> <code>{card}</code>
[<a href="https://t.me/o8380">ϟ</a>] <b>Response: {result} ✅</b>
[<a href="https://t.me/o8380">ϟ</a>] <b>Status: Insufficient Funds</b>
- - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/o8380">ϟ</a>] <b>Info: {brand} - {card_type}</b>
[<a href="https://t.me/o8380">ϟ</a>] <b>Bank: {bank}</b>
[<a href="https://t.me/o8380">ϟ</a>] <b>Country: {country} {country_flag}</b>
- - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/o8380">⎇</a>] <b>Req By: @{username}</b>
- - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/o8380">⌤</a>] <b>Dev by: Mustafa - @o8380 🗣</b>"""
            bot.send_message(chat_id, ccn_msg, parse_mode="HTML")
        elif 'CVV' in str(result) or 'Do not honor' in str(result):
            session['approved'].append(card)
        else:
            session['declined'].append(card)
        
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
            
            text = f"""<b>Gateway: PayPal_Donation ($1.00)
By: @{username}</b>"""
            
            bot.edit_message_text(text, chat_id, msg_id, parse_mode="HTML", reply_markup=markup)
        except:
            pass
        
        time.sleep(2)
    
    session['running'] = False
    
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
        
        text = f"""<b>✅ Check Completed!
Gateway: PayPal_Donation ($1.00)
By: @{username}</b>

- - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/o8380">⌤</a>] <b>Dev by: Mustafa - @o8380 🗣</b>"""
        
        bot.edit_message_text(text, chat_id, msg_id, parse_mode="HTML", reply_markup=markup)
    except:
        pass

# ============================================
# Main
# ============================================

if __name__ == "__main__":
    print("🤖 PayPal Donation Bot Starting...")
    print("Gateway: cjrimpact.org")
    print("Amount: $1.00")
    print("Status: FREE")
    print("👨‍💻 Developer: Mustafa (@o8380)")
    
    bot.remove_webhook()
    time.sleep(1)
    
    print("✅ Bot is running!")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
