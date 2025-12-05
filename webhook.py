from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

#Storage for the latest notification
latest_notification = {}

#Route to view the latest notification in the browser
@app.route('/')
def home():
    if latest_notification:
        html = f"""
        <h2>Latest Notification</h2>
        <p><strong>Amount:</strong> {latest_notification.get('amount')}</p>
        <p><strong>Email:</strong> {latest_notification.get('receiver')}</p>
        """
    else:
        html = "<h2>No notifications received yet.</h2>"
    return render_template_string(html)

#Webhook route to receive notifications
@app.route('/notify', methods=['POST'])
def notify():
    global latest_notification
    data = request.get_json()
    latest_notification = data  #Save the received notification
    print("Webhook received:", data)
    return jsonify({"status": "Notification received"}), 200

#Run the flask server
if __name__ == '__main__':
    app.run(port=5000)
