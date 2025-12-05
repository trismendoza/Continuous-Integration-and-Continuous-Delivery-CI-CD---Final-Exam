import tkinter as tk
from tkinter import messagebox, simpledialog
from auth_system import verify_login, is_registered, save_user, send_otp, load_users, save_users
from payment_otp import send_payment_gui
import requests
import os

#Users and balance storage
USER_FILE = 'users.txt'

#Class for the Login and Register
class AuthGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Mini Payment System")
        self.root.geometry("300x300")
        self.build_login_screen()

    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    #Login screen
    def build_login_screen(self):
        self.clear_frame()
        tk.Label(self.root, text="Login", font=("Arial", 14)).pack(pady=10)

        tk.Label(self.root, text="Email:").pack()
        self.email_entry = tk.Entry(self.root, width=25)
        self.email_entry.pack(pady=5)

        tk.Label(self.root, text="Password:").pack()
        self.password_entry = tk.Entry(self.root, show="*", width=25)
        self.password_entry.pack(pady=5)

        tk.Button(self.root, text="Login", command=self.login).pack(pady=10)
        tk.Button(self.root, text="Register", command=self.build_register_screen).pack()

    #Register screen
    def build_register_screen(self):
        self.clear_frame()
        tk.Label(self.root, text="Register", font=("Arial", 14)).pack(pady=10)

        tk.Label(self.root, text="Name:").pack()
        self.name_entry = tk.Entry(self.root, width=25)
        self.name_entry.pack(pady=5)

        tk.Label(self.root, text="Email:").pack()
        self.reg_email_entry = tk.Entry(self.root, width=25)
        self.reg_email_entry.pack(pady=5)

        tk.Label(self.root, text="Password:").pack()
        self.reg_pass_entry = tk.Entry(self.root, show="*", width=25)
        self.reg_pass_entry.pack(pady=5)

        tk.Button(self.root, text="Send OTP & Register", command=self.register).pack(pady=10)
        tk.Button(self.root, text="Back to Login", command=self.build_login_screen).pack()

    #Function for login, the user must be registered
    def login(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        if verify_login(email, password):
            username = self.get_username(email)
            self.root.destroy()
            open_dashboard(email, username)
        else:
            messagebox.showerror("Login Failed", "Invalid credentials or account not verified.")

    #Register Fuction, it will send an OTP to the email of the user
    def register(self):
        name = self.name_entry.get().strip()
        email = self.reg_email_entry.get().strip()
        password = self.reg_pass_entry.get().strip()

        if is_registered(email):
            messagebox.showerror("Registration Failed", "Email already registered.")
            return

        otp = send_otp(email)
        if not otp:
            messagebox.showerror("Error", "Failed to send OTP.")
            return

        entered_otp = simpledialog.askstring("OTP Verification", "Enter the OTP sent to your email:")
        if entered_otp == otp:
            save_user(email, password, name)

            messagebox.showinfo("Success", "Registration complete! Please login.")
            self.build_login_screen()
        else:
            messagebox.showerror("Invalid OTP", "Incorrect OTP entered.")

    def get_username(self, email):
        if not os.path.exists(USER_FILE):
            return "User"
        with open(USER_FILE, 'r') as f:
            for line in f:
                parts = line.strip().split(',')
                if parts[0] == email:
                    return parts[2]
        return "User"
    
#Class for the Payment System
class PaymentSystem:
    def __init__(self, root, email, username):
        self.root = root
        self.user_email = email
        self.username = username
        self.users = load_users()
        self.build_dashboard()

    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    #Main screen for the system
    def build_dashboard(self):
        self.clear_frame()
        tk.Label(self.root, text=f"Welcome, {self.username}", font=("Arial", 16)).pack(pady=10)

        tk.Label(self.root, text="Recipient Email:").pack()
        self.to_entry = tk.Entry(self.root, width=25)
        self.to_entry.pack(pady=5)

        tk.Label(self.root, text="Amount:").pack()
        self.amt_entry = tk.Entry(self.root)
        self.amt_entry.pack()

        tk.Button(self.root, text="Send Payment", command=self.send_payment).pack(pady=10)
        tk.Button(self.root, text="Check Balance", command=self.check_balance).pack(pady=5)

        self.output = tk.Label(self.root, text="", fg="green")
        self.output.pack(pady=10)

    def check_balance(self):
        balance = self.users[self.user_email]["balance"]
        messagebox.showinfo("Balance", f"Your balance is ₱{balance:.2f}")

    #Function to send payment with OTP
    def send_payment(self):
        to_email = self.to_entry.get().strip()
        amount_str = self.amt_entry.get().strip()

        if not to_email or not amount_str:
            messagebox.showerror("Input Error", "Please enter both recipient and amount.")
            return

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Enter a valid amount.")
            return

        if to_email not in self.users:
            messagebox.showerror("Error", "Recipient does not exist.")
            return

        current_balance = self.users[self.user_email]["balance"]
        if amount > current_balance:
            messagebox.showerror("Insufficient Funds", "Not enough balance.")
            return

        success, msg, otp = send_payment_gui(amount, self.user_email)
        if not success:
            messagebox.showerror("Error", msg)
            return

        #Verify OTP
        entered_otp = simpledialog.askstring("OTP Verification", "Enter the OTP sent to your email:")
        if entered_otp == otp:
            self.users[self.user_email]["balance"] -= amount
            self.users[to_email]["balance"] += amount
            save_users(self.users)

            self.output.config(
                text=f"₱{amount:.2f} sent to {to_email}.\nRemaining: ₱{self.users[self.user_email]['balance']:.2f}"
            )

            #Send webhook notification
            try:
                response = requests.post("http://localhost:5000/notify", json={
                "status": "success",
                "amount": amount,
                "sender": self.user_email,
                "receiver": to_email
            })
                messagebox.showinfo("Webhook", f"Webhook response: {response.json()}")
            except Exception as e:
                messagebox.showwarning("Webhook", f"Webhook failed: {e}")
        else:
            messagebox.showerror("Invalid OTP", "Payment cancelled.")

def open_dashboard(email, name):
    dashboard = tk.Tk()
    dashboard.title("Mini Payment System")
    dashboard.geometry("400x400")
    PaymentSystem(dashboard, email, name)
    dashboard.mainloop()

if __name__ == '__main__':
    root = tk.Tk()
    app = AuthGUI(root)
    root.mainloop()
