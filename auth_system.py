import random
import smtplib
from email.message import EmailMessage
import os

USER_FILE = 'users.txt'

from_email = 'trisciajoy07@gmail.com'
app_password = 'mdnz huss bpmf dxxl'

def send_otp(to_email):
    otp = ''.join(str(random.randint(0, 9)) for _ in range(6))
    
    msg = EmailMessage()
    msg['Subject'] = 'Your OTP Code'
    msg['From'] = from_email
    msg['To'] = to_email
    msg.set_content(f'Your OTP is: {otp}')
    
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(from_email, app_password)
            server.send_message(msg)
        print("OTP sent successfully.")
    except Exception as e:
        print("Failed to send email:", e)
        return None
    
    return otp


def save_user(email, password, name, balance=1000.0):
    with open(USER_FILE, 'a') as f:
        f.write(f"{email},{password},{name},true,{balance}\n")

def load_users():
    users = {}
    if os.path.exists(USER_FILE):
        with open(USER_FILE, 'r') as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) == 5:
                    email, password, name, verified, balance = parts
                    users[email] = {
                        'password': password,
                        'name': name,
                        'verified': verified == 'true',
                        'balance': float(balance)
                    }
    return users

def save_users(users):
    with open(USER_FILE, 'w') as f:
        for email, data in users.items():
            f.write(f"{email},{data['password']},{data['name']},{str(data['verified']).lower()},{data['balance']}\n")

def is_registered(email):
    if not os.path.exists(USER_FILE):
        return False
    with open(USER_FILE, 'r') as f:
        for line in f:
            if line.startswith(email + ","):
                return True
    return False


def verify_login(email, password):
    if not os.path.exists(USER_FILE):
        return False
    with open(USER_FILE, 'r') as f:
        for line in f:
            parts = line.strip().split(',')
            if parts[0] == email and parts[1] == password and parts[3] == 'true':
                return True
    return False

