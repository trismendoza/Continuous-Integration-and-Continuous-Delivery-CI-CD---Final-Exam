import random
import smtplib
from email.message import EmailMessage
import requests

#Function to send payment using OTP
def send_payment_gui(amount, to_email):
    #To generate 6-digit OTP
    otp = ''.join(str(random.randint(0, 9)) for _ in range(6))

    #Email that will send an email
    from_email = 'trisciajoy07@gmail.com'
    app_password = 'wmvy ahvb vwul yymo' #Use app password

    #Send OTP email
    try:
        #Email setup
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, app_password)

        #OTP message
        message = EmailMessage()
        message['Subject'] = "OTP Verification"
        message['From'] = from_email
        message['To'] = to_email
        message.set_content(f'Your OTP is {otp}')
        server.send_message(message)
        server.quit()
    except Exception as e:
        return False, f"Failed to send OTP: {e}", None

    return True, "OTP sent successfully.", otp
