#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔═══════════════════════════════════════════════════════════════╗
║     🔍 ALL-IN-ONE INFO GATHERING TELEGRAM BOT                 ║
║     IP | PIN | IFSC | VEHICLE (JSON FORMAT)                   ║
║     ROHIT HACKER EDITION                                 ║
╚═══════════════════════════════════════════════════════════════╝
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import socket
import re
from urllib.parse import quote
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    ContextTypes
)
import logging
from datetime import datetime
import time

# ==============================================
# CONFIGURATION
# ==============================================
BOT_TOKEN = "8252056957:AAEfb2FZtPv4yQBy--dYaQqzuXOkDRIe3SE"

# ==============================================
# LOGGING SETUP
# ==============================================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==============================================
# CONVERSATION STATES
# ==============================================
(IP_INPUT, PIN_INPUT, IFSC_INPUT, VEHICLE_INPUT) = range(4)

# ==============================================
# HELPER FUNCTIONS
# ==============================================

def check_net():
    """Check internet connectivity"""
    for host, port in [("8.8.8.8", 53), ("1.1.1.1", 53)]:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3)
            s.connect((host, port))
            s.close()
            return True
        except:
            pass
    return False

def safe_request(url, headers=None, timeout=15, retry=2, method='GET', data=None):
    """Safe HTTP request with retry logic"""
    h = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive"
    }
    if headers:
        h.update(headers)
    
    for i in range(retry):
        try:
            if method == 'POST':
                return requests.post(url, data=data, headers=h, timeout=timeout)
            return requests.get(url, headers=h, timeout=timeout)
        except requests.exceptions.ConnectionError:
            if i < retry-1:
                time.sleep(2)
            else:
                raise
        except requests.exceptions.Timeout:
            if i < retry-1:
                time.sleep(2)
            else:
                raise

def format_json_output(data: dict) -> str:
    """Format JSON data for Telegram message"""
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    return f"```json\n{json_str}\n```"

# ==============================================
# COMMAND HANDLERS
# ==============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message"""
    keyboard = [
        [InlineKeyboardButton("🌐 IP Address Info", callback_data='ip')],
        [InlineKeyboardButton("📮 PIN Code Info", callback_data='pin')],
        [InlineKeyboardButton("🏦 IFSC Code Info", callback_data='ifsc')],
        [InlineKeyboardButton("🚗 Vehicle RC Info", callback_data='vehicle')],
        [InlineKeyboardButton("ℹ️ Help", callback_data='help')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        "╔═══════════════════════════════╗\n"
        "║  🔍 *INFO GATHERING BOT* 🔍  ║\n"
        "║  *ROHIT HACKER EDITION*  ║\n"
        "╚═══════════════════════════════╝\n\n"
        "*🔥 Features (All JSON Format):*\n"
        "• 🌐 IP Address Information\n"
        "• 📮 PIN Code Full Details\n"
        "• 🏦 IFSC Bank Details\n"
        "• 🚗 Vehicle RC Full Details\n\n"
        "👇 *Select an option below:*"
    )
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show menu"""
    keyboard = [
        [InlineKeyboardButton("🌐 IP Address Info", callback_data='ip')],
        [InlineKeyboardButton("📮 PIN Code Info", callback_data='pin')],
        [InlineKeyboardButton("🏦 IFSC Code Info", callback_data='ifsc')],
        [InlineKeyboardButton("🚗 Vehicle RC Info", callback_data='vehicle')],
        [InlineKeyboardButton("ℹ️ Help", callback_data='help')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🔍 *Select Information Type:*",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message"""
    help_text = (
        "🔍 *INFO GATHERING BOT HELP*\n\n"
        "*Commands:*\n"
        "/start - Start bot\n"
        "/menu - Show menu\n"
        "/help - Help\n\n"
        "*Features (JSON Format):*\n"
        "🌐 *IP Info* - IP/domain lookup\n"
        "📮 *PIN Code* - Indian PIN details\n"
        "🏦 *IFSC Code* - Bank branch info\n"
        "🚗 *Vehicle* - RC full details\n\n"
        "Developer: @rohit_x_official_01"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

# ==============================================
# IP TO INFO FUNCTION
# ==============================================

async def get_ip_info(ip: str) -> dict:
    """Get complete IP information in JSON"""
    result = {
        "status": "success",
        "query_ip": ip,
        "timestamp": datetime.now().isoformat(),
        "powered_by": "ROHIT HACKER"
    }
    
    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,asname,reverse,mobile,proxy,hosting,query"
        r = safe_request(url, timeout=5)
        data = r.json()
        
        if data.get('status') == 'success':
            result["location"] = {
                "ip": data.get('query'),
                "country": data.get('country'),
                "country_code": data.get('countryCode'),
                "region": data.get('regionName'),
                "city": data.get('city'),
                "zip": data.get('zip'),
                "timezone": data.get('timezone')
            }
            result["coordinates"] = {
                "latitude": data.get('lat'),
                "longitude": data.get('lon'),
                "google_maps": f"https://maps.google.com/?q={data.get('lat')},{data.get('lon')}"
            }
            result["network"] = {
                "isp": data.get('isp'),
                "organization": data.get('org'),
                "as_number": data.get('as'),
                "as_name": data.get('asname'),
                "reverse_dns": data.get('reverse')
            }
            result["flags"] = {
                "is_mobile": data.get('mobile', False),
                "is_proxy": data.get('proxy', False),
                "is_hosting": data.get('hosting', False)
            }
        else:
            result["status"] = "error"
            result["message"] = data.get('message', 'Unknown error')
    except Exception as e:
        result["status"] = "error"
        result["message"] = str(e)
    
    return result

# ==============================================
# PIN TO INFO FUNCTION
# ==============================================

async def get_pin_info(pin_code: str) -> dict:
    """Get complete PIN code information in JSON"""
    result = {
        "status": "success",
        "pincode": pin_code,
        "timestamp": datetime.now().isoformat(),
        "powered_by": "ROHIT HACKER"
    }
    
    # India Post API
    try:
        r = safe_request(f"https://api.postalpincode.in/pincode/{pin_code}")
        d = r.json()
        
        if d[0]['Status'] == "Success":
            offices = d[0]['PostOffice']
            result["total_post_offices"] = len(offices)
            result["summary"] = {
                "total": len(offices),
                "delivery": sum(1 for o in offices if o.get('DeliveryStatus') == 'Delivery'),
                "non_delivery": sum(1 for o in offices if o.get('DeliveryStatus') != 'Delivery')
            }
            result["post_offices"] = []
            
            for office in offices:
                po_data = {
                    "name": office.get('Name'),
                    "district": office.get('District'),
                    "state": office.get('State'),
                    "country": office.get('Country', 'India'),
                    "pincode": office.get('Pincode'),
                    "delivery_status": office.get('DeliveryStatus'),
                    "division": office.get('Division'),
                    "region": office.get('Region'),
                    "circle": office.get('Circle'),
                    "taluk": office.get('Taluk'),
                    "block": office.get('Block'),
                    "related_sub_office": office.get('RelatedSuboffice'),
                    "related_head_office": office.get('RelatedHeadoffice')
                }
                result["post_offices"].append(po_data)
        else:
            result["status"] = "error"
            result["message"] = d[0].get('Message', 'No records found')
    except Exception as e:
        result["status"] = "error"
        result["message"] = str(e)
    
    # Zippopotam for coordinates
    try:
        r2 = safe_request(f"https://api.zippopotam.us/in/{pin_code}")
        if r2.status_code == 200:
            d2 = r2.json()
            places = d2.get('places', [])
            if places:
                place = places[0]
                result["location"] = {
                    "city": place.get('place name'),
                    "state": place.get('state'),
                    "state_abbreviation": place.get('state abbreviation'),
                    "latitude": place.get('latitude'),
                    "longitude": place.get('longitude'),
                    "google_maps": f"https://maps.google.com/?q={place.get('latitude')},{place.get('longitude')}"
                }
    except:
        pass
    
    return result

# ==============================================
# IFSC TO INFO FUNCTION
# ==============================================

async def get_ifsc_info(ifsc_code: str) -> dict:
    """Get IFSC code information in JSON"""
    result = {
        "status": "success",
        "ifsc_code": ifsc_code,
        "timestamp": datetime.now().isoformat(),
        "powered_by": "ROHIT HACKER"
    }
    
    try:
        r = safe_request(f"https://ifsc.razorpay.com/{ifsc_code}")
        if r.status_code == 404:
            result["status"] = "error"
            result["message"] = "IFSC Code not found"
            return result
        
        d = r.json()
        
        result["bank_info"] = {
            "bank_name": d.get('BANK'),
            "branch": d.get('BRANCH'),
            "ifsc_code": d.get('IFSC'),
            "micr_code": d.get('MICR'),
            "contact": d.get('CONTACT')
        }
        
        result["address"] = {
            "full_address": d.get('ADDRESS'),
            "city": d.get('CITY'),
            "district": d.get('DISTRICT'),
            "state": d.get('STATE')
        }
        
        result["services"] = {
            "rtgs": d.get('RTGS', False),
            "neft": d.get('NEFT', False),
            "imps": d.get('IMPS', False),
            "upi": d.get('UPI', False)
        }
        
        bank_code = ifsc_code[:4]
        result["bank_code"] = bank_code
        
        bank_names = {
            'SBIN': 'State Bank of India',
            'HDFC': 'HDFC Bank',
            'ICIC': 'ICICI Bank',
            'AXIS': 'Axis Bank',
            'PUNB': 'Punjab National Bank',
            'YESB': 'Yes Bank',
            'KOTK': 'Kotak Mahindra Bank',
            'IDFB': 'IDFC First Bank',
            'BARB': 'Bank of Baroda',
            'CNRB': 'Canara Bank',
            'UBIN': 'Union Bank of India',
        }
        
        if bank_code in bank_names:
            result["known_bank_name"] = bank_names[bank_code]
            
    except Exception as e:
        result["status"] = "error"
        result["message"] = str(e)
    
    return result

# ==============================================
# VEHICLE RC INFO FUNCTION
# ==============================================

async def get_vehicle_info(rc_number: str) -> dict:
    """Get vehicle RC information in JSON format"""
    result = {
        "status": "success",
        "registration_number": rc_number,
        "powered_by": "ROHIT HACKER • @rohit_x_official_01",
        "telegram_links": [
            "https://t.me/+A8OBAZAW7ao2YWE9"
        ]
    }
    
    try:
        r = safe_request(f"https://vahanx.in/rc-search/{rc_number}", timeout=20)
        soup = BeautifulSoup(r.text, "html.parser")
        
        def get_card_text(label):
            try:
                for div in soup.select(".hrcd-cardbody"):
                    span = div.find("span")
                    if span and label.lower() in span.text.lower():
                        p = div.find("p")
                        return p.get_text(strip=True) if p else None
            except:
                return None
        
        def get_val(label):
            try:
                div_elem = soup.find("span", string=label)
                if div_elem:
                    parent = div_elem.find_parent("div")
                    p = parent.find("p") if parent else None
                    return p.get_text(strip=True) if p else None
            except:
                return None
        
        owner = get_card_text("Owner Name") or get_val("Owner Name")
        father = get_val("Father's Name")
        model = get_card_text("Modal Name") or get_val("Model Name")
        maker = get_val("Maker Model")
        fuel = get_card_text("Fuel Type") or get_val("Fuel Type")
        norms = get_val("Fuel Norms")
        vclass = get_val("Vehicle Class")
        reg_date = get_val("Registration Date")
        color = get_val("Color")
        rto = get_val("Registered RTO")
        chassis = get_val("Chassis Number")
        engine = get_val("Engine Number")
        cc = get_val("Cubic Capacity")
        seat = get_val("Seating Capacity")
        fitness = get_val("Fitness Upto")
        tax = get_val("Tax Upto")
        ins_comp = get_val("Insurance Company") or get_card_text("Insurance Company")
        ins_no = get_val("Insurance No") or get_val("Policy No")
        ins_exp = get_val("Insurance Expiry") or get_val("Insurance Upto")
        puc_no = get_val("PUC No") or get_val("PUC Number")
        puc_upto = get_val("PUC Upto") or get_val("PUC Valid Upto")
        age = get_val("Vehicle Age")
        serial = get_val("Owner Serial No")
        financer = get_val("Financier Name") or get_val("Financer Name")
        blacklist = get_val("Blacklist Status")
        noc = get_val("NOC Details") or get_val("NOC Status")
        permit = get_val("Permit Type")
        address = get_card_text("Address") or get_val("Address")
        city = get_card_text("City Name") or get_val("City Name") or get_val("City")
        phone = get_card_text("Phone") or get_val("Phone") or get_val("Mobile")
        
        if owner:
            result["basic_info"] = {
                "owner_name": owner or "NA",
                "fathers_name": father or "NA",
                "model_name": model or "NA",
                "address": address or "NA",
                "city": city or "NA",
                "phone": phone or "NA"
            }
            
            result["ownership_details"] = {
                "owner_name": owner or "NA",
                "father's_name": father or "NA",
                "owner_serial_no": serial or "NA",
                "registered_rto": rto or "NA"
            }
            
            result["vehicle_details"] = {
                "model_name": model or "NA",
                "maker_model": maker or "NA",
                "fuel_type": fuel or "NA",
                "fuel_norms": norms or "NA",
                "vehicle_class": vclass or "NA",
                "color": color or "NA",
                "chassis_number": chassis or "NA",
                "engine_number": engine or "NA",
                "cubic_capacity": cc or "NA",
                "seating_capacity": seat or "NA"
            }
            
            result["validity"] = {
                "registration_date": reg_date or "NA",
                "fitness_upto": fitness or "NA",
                "tax_upto": tax or "NA",
                "insurance_upto": ins_exp or "NA",
                "vehicle_age": age or "NA"
            }
            
            result["insurance"] = {
                "company": ins_comp or "NA",
                "policy_number": ins_no or "NA",
                "expiry_date": ins_exp or "NA",
                "status": "Active" if ins_exp else "NA"
            }
            
            result["puc_details"] = {
                "puc_number": puc_no or "NA",
                "puc_valid_upto": puc_upto or "NA"
            }
            
            result["other_info"] = {
                "financer_name": financer or "NA",
                "blacklist_status": blacklist or "NA",
                "noc_details": noc or "NA",
                "permit_type": permit or "NA"
            }
        else:
            result["status"] = "error"
            result["message"] = "RC data not found"
            
    except Exception as e:
        result["status"] = "error"
        result["message"] = f"Error: {str(e)}"
    
    return result

# ==============================================
# CALLBACK HANDLERS
# ==============================================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'help':
        await help_command(update, context)
        return ConversationHandler.END
    elif query.data == 'ip':
        await query.edit_message_text(
            "🌐 *Enter IP Address or Domain:*\n\n"
            "Examples:\n"
            "• `8.8.8.8`\n"
            "• `google.com`\n\n"
            "Send /cancel to abort",
            parse_mode='Markdown'
        )
        return IP_INPUT
    elif query.data == 'pin':
        await query.edit_message_text(
            "📮 *Enter 6-Digit PIN Code:*\n\n"
            "Examples:\n"
            "• `110001`\n"
            "• `804452`\n\n"
            "Send /cancel to abort",
            parse_mode='Markdown'
        )
        return PIN_INPUT
    elif query.data == 'ifsc':
        await query.edit_message_text(
            "🏦 *Enter 11-Character IFSC Code:*\n\n"
            "Examples:\n"
            "• `SBIN0000001`\n"
            "• `HDFC0000123`\n\n"
            "Send /cancel to abort",
            parse_mode='Markdown'
        )
        return IFSC_INPUT
    elif query.data == 'vehicle':
        await query.edit_message_text(
            "🚗 *Enter Vehicle Number:*\n\n"
            "Examples:\n"
            "• `RJ18CF3690`\n"
            "• `DL10AD7619`\n\n"
            "Send /cancel to abort",
            parse_mode='Markdown'
        )
        return VEHICLE_INPUT

# ==============================================
# INPUT HANDLERS
# ==============================================

async def handle_ip_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle IP address input"""
    user_input = update.message.text.strip()
    
    if not user_input:
        await update.message.reply_text("❌ Please enter an IP or domain!\n/cancel to abort")
        return IP_INPUT
    
    ip_pattern = r'^\d+\.\d+\.\d+\.\d+$'
    domain_pattern = r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(ip_pattern, user_input) and not re.match(domain_pattern, user_input):
        await update.message.reply_text("❌ Invalid format!\n/cancel to abort")
        return IP_INPUT
    
    ip = user_input
    if not re.match(ip_pattern, user_input):
        try:
            temp_msg = await update.message.reply_text(f"🔍 Resolving {user_input}...")
            ip = socket.gethostbyname(user_input)
            await temp_msg.delete()
        except:
            await update.message.reply_text("❌ Could not resolve domain!")
            return IP_INPUT
    
    temp_msg = await update.message.reply_text("🔍 Fetching IP info...")
    result = await get_ip_info(ip)
    await temp_msg.delete()
    
    json_output = format_json_output(result)
    await update.message.reply_text(
        f"🌐 *IP INFO RESULT*\n{json_output}",
        parse_mode='Markdown'
    )
    
    await menu_command(update, context)
    return ConversationHandler.END

async def handle_pin_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle PIN code input - Shows ALL offices"""
    pin = update.message.text.strip()
    
    if not pin.isdigit() or len(pin) != 6:
        await update.message.reply_text("❌ Enter exactly 6 digits!\n/cancel to abort")
        return PIN_INPUT
    
    temp_msg = await update.message.reply_text("🔍 Fetching PIN details...")
    result = await get_pin_info(pin)
    await temp_msg.delete()
    
    if result.get("status") == "error":
        json_output = format_json_output(result)
        await update.message.reply_text(
            f"📮 *PIN RESULT*\n{json_output}",
            parse_mode='Markdown'
        )
        await menu_command(update, context)
        return ConversationHandler.END
    
    # Send SUMMARY
    summary_data = {
        "status": result["status"],
        "pincode": result["pincode"],
        "timestamp": result.get("timestamp"),
        "powered_by": result.get("powered_by"),
        "total_post_offices": result.get("total_post_offices", 0),
        "summary": result.get("summary", {}),
        "location": result.get("location", {})
    }
    
    await update.message.reply_text(
        f"📮 *PIN SUMMARY*\n{format_json_output(summary_data)}",
        parse_mode='Markdown'
    )
    
    # Send ALL offices in chunks of 5
    all_offices = result.get("post_offices", [])
    
    if all_offices:
        chunk_size = 5
        total_chunks = (len(all_offices) + chunk_size - 1) // chunk_size
        
        for i in range(0, len(all_offices), chunk_size):
            chunk = all_offices[i:i+chunk_size]
            chunk_num = (i // chunk_size) + 1
            
            chunk_data = {
                "pincode": pin,
                "chunk": f"{chunk_num}/{total_chunks}",
                "offices": chunk
            }
            
            if chunk_num == total_chunks:
                chunk_data["note"] = f"Total {len(all_offices)} post offices. All offices shown."
            
            await update.message.reply_text(
                f"📮 *POST OFFICES ({chunk_num}/{total_chunks})*\n{format_json_output(chunk_data)}",
                parse_mode='Markdown'
            )
    
    await menu_command(update, context)
    return ConversationHandler.END

async def handle_ifsc_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle IFSC code input"""
    ifsc = update.message.text.strip().upper()
    
    if len(ifsc) != 11:
        await update.message.reply_text("❌ Enter 11 characters!\n/cancel to abort")
        return IFSC_INPUT
    
    temp_msg = await update.message.reply_text("🔍 Fetching IFSC details...")
    result = await get_ifsc_info(ifsc)
    await temp_msg.delete()
    
    json_output = format_json_output(result)
    await update.message.reply_text(
        f"🏦 *IFSC RESULT*\n{json_output}",
        parse_mode='Markdown'
    )
    
    await menu_command(update, context)
    return ConversationHandler.END

async def handle_vehicle_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle vehicle input"""
    rc = update.message.text.strip().upper()
    
    if not rc or len(rc) < 8:
        await update.message.reply_text("❌ Enter valid vehicle number!\n/cancel to abort")
        return VEHICLE_INPUT
    
    temp_msg = await update.message.reply_text("🔍 Fetching vehicle RC details...")
    result = await get_vehicle_info(rc)
    await temp_msg.delete()
    
    json_output = format_json_output(result)
    await update.message.reply_text(
        f"🚗 *VEHICLE RC RESULT*\n{json_output}",
        parse_mode='Markdown'
    )
    
    await menu_command(update, context)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel conversation"""
    await update.message.reply_text("❌ Cancelled.\nUse /menu to start again.")
    await menu_command(update, context)
    return ConversationHandler.END

# ==============================================
# ERROR HANDLER
# ==============================================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors"""
    logger.error(f"Update {update} caused error {context.error}")
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text("❌ Error occurred. Please try again.")
    except:
        pass

# ==============================================
# MAIN FUNCTION
# ==============================================

def main():
    """Start the bot"""
    print("=" * 55)
    print("🔍 INFO GATHERING BOT")
    print("ROHIT HACKER EDITION")
    print("=" * 55)
    
    if not check_net():
        print("❌ No internet connection!")
        return
    
    print("✅ Internet connected")
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler)],
        states={
            IP_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ip_input)],
            PIN_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_pin_input)],
            IFSC_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ifsc_input)],
            VEHICLE_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_vehicle_input)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('menu', menu_command))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(conv_handler)
    application.add_error_handler(error_handler)
    
    print("=" * 55)
    print("✅ Bot is running...")
    print("Press Ctrl+C to stop")
    print("=" * 55)
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Bot stopped")
        print("👋 Goodbye!\n")
    except Exception as e:
        print(f"\n❌ Error: {e}")