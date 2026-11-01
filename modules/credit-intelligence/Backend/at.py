import os
import threading
import africastalking
from flask import Flask, request, make_response
import urllib3
import requests
app = Flask(__name__)

# --- Africa's Talking Initialization ---
# The username MUST be 'sandbox' for testing
AT_USERNAME = "sandbox"
AT_API_KEY = os.getenv("AFRICASTALKING_API_KEY", "")

africastalking.initialize(AT_USERNAME, AT_API_KEY)
sms = africastalking.SMS

# --- Mock Background Task ---


# Disable the annoying SSL warning in the terminal
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def mock_underwriting_process(phone_number, national_id):
    """
    Direct REST API call to bypass Windows SSL issues
    """
    message = f"Congratulations! Your AfracaNet voucher for National ID {national_id} has been approved by the SACCO. Proceed to Githunguri Farm Supplies."
    
    url = "https://api.sandbox.africastalking.com/version1/messaging"
    headers = {
        "ApiKey": AT_API_KEY,
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    payload = {
        "username": AT_USERNAME,
        "to": phone_number,
        "message": message
    }
    
    try:
        # verify=False is the hackathon cheat code to bypass local SSL hell
        response = requests.post(url, headers=headers, data=payload, verify=False)
        print(f"SMS API Response: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Encountered an error while sending SMS: {e}")

# --- USSD Webhook Endpoint ---
@app.route('/api/ussd', methods=['POST'])
def ussd_callback():
    # Africa's Talking sends these parameters via POST
    session_id = request.form.get("sessionId")
    service_code = request.form.get("serviceCode")
    phone_number = request.form.get("phoneNumber")
    text = request.form.get("text", "")

    # The 'text' variable contains the user's input, separated by '*'
    
    if text == "":
        # First screen: The user just dialed the code
        response = "CON Welcome to AfracaNet.\n"
        response += "1. Apply for Input Loan\n"
        response += "2. Check Trust Score"
        
    elif text == "1":
        # User selected 1
        response = "CON Enter your National ID:"
        
    elif text.startswith("1*"):
        # User entered ID (e.g., "1*28471936")
        # Split the text by '*' to get the actual ID
        input_array = text.split("*")
        national_id = input_array[1]
        
        # End the USSD session cleanly on the phone
        response = f"END Thank you. Your loan application for ID {national_id} has been received.\nWe are analyzing your Chama history. You will receive an SMS shortly."
        
        # Trigger the Neo4j/LLM/SMS pipeline in a background thread 
        # so it doesn't block the USSD response to the phone
        threading.Thread(target=mock_underwriting_process, args=(phone_number, national_id)).start()
        
    else:
        response = "END Invalid Input. Please try again."

    # Africa's Talking expects a plain text response
    # Africa's Talking expects a plain text response
    flask_response = make_response(response)
    flask_response.headers['Content-Type'] = 'text/plain'
    return flask_response

if __name__ == '__main__':
    # Run the Flask app on port 5000
    app.run(port=5000, debug=True)