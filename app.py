from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from Final_Output_Gen import run_all
import os, shutil
import json
import time
import pandas as pd

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    
@app.route('/upload_files', methods=['POST'])
def upload_files():
    
    if 'files' not in request.files:
        return jsonify({"error": "No file part"}), 400
    files = request.files.getlist('files')
    if not files:
        return jsonify({"error": "No selected files"}), 400    
    for file in files:
        file.save(os.path.join(UPLOAD_FOLDER, file.filename))
    return jsonify({"message": "Files uploaded successfully"}), 200

@app.route('/upload_folder', methods=['POST'])
def upload_folder():
        
    if 'folder' not in request.files:
        return jsonify({"error": "No folder part"}), 400
    files = request.files.getlist('folder')
    if not files:
        return jsonify({"error": "No selected folder"}), 400
    
    for file in files:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        file.save(file_path)
    return jsonify({"message": "Folder uploaded successfully"}), 200

@app.route('/create_use_cases', methods=['POST'])
def create_use_cases():
    return jsonify({
        "message": "Use cases created successfully",
        "functionalFlows": [
            'Fare Payment',
            'Query a Farecard',
            'Cardholder profile changes',
            'Inspection',
            'Farecard Sales',
            'Reversals',
            'Refunds',
            'Counters',
            'GPS',
            'Training Mode',
            'Operator sign-in',
            'Modify screen brightness',
            'Battery',
            'Check SA Tool device information',
            'Device states',
            'Check Shift statistics',
            'Establish Wi-Fi or cellular network connection',
            'Change operator language',
            'All'
        ]
    })

@app.route('/get_sub_categories', methods=['POST'])
def get_sub_categories():
    data = request.get_json()
    category = data.get("category")
    sub_categories = {
        "Fare Payment": ["Farecard", "Tickets", "e-Tickets", "Virtual Card", "Open Payments", "With/Without audio messages"],
        "Query a Farecard": ["Tickets", "Virtual Card", "With/Without audio messages"],
        "Cardholder profile changes": ["Change universal concession", "Change SP specific concession", "Change card language profile", "Default Trip", "Block/Unblock"],
        "Inspection": ["Farecard", "Tickets", "e-Tickets", "With/Without audio messages", "Accept inspection", "Written warning", "Verbal warning", "Pay Fare", "Provincial offense notice (PON)", "Record inspections for processing", "Cancel inspections (back/waive)"],
        "Farecard Sales": ["Farecard Sale", "E-Purse load", "Period pass load", "Paper Tickets", "Tickets", "Special Tickets", "Upgrades", "Other Products", "Vouchers", "Service Guarantee", "LUM Sales", "Fixed Ride LUM Sale", "Sliding Period Pass LUM Sale", "Reversals", "e-Purse payment reversal", "Period pass load reversal", "Refunds", "E-Purse balance refund", "Period pass refund", "Ticket/Special Ticket refund", "Other products"],
        "Reversals": ["e-Purse payment reversal", "Period pass load reversal"],
        "Refunds": ["E-Purse balance refund", "Period pass refund", "Ticket/Special Ticket refund", "Other products"],
        "Counters": ["Activate", "Increment", "Configure haptic feedback", "Check counter summary"],
        "GPS": ["Enable/Disable GPS", "Select new route and line", "Override inspection location"],
        "Training Mode": ["Power on / off / reboot SA Tool", "Power on", "Shut down", "Reboot", "Passcode", "Enter lock screen passcode", "Change passcode", "Reset passcode", "Mandatory periodic passcode reset", "Operator sign-in", "First-time user", "Existing user", "Operator sign-off", "Modify screen brightness", "Modify audio tone volume", "Battery", "Operator checks battery power level", "SA Tool battery drops below the low battery threshold", "SA Tool battery dies", "Check SA Tool device information", "Switch device mode between different SPs (DISTANCE BASED TRANSIT and Distance based Transit only)", "Device states", "Operator switches SA Tool from standby to in-service state", "Operator switches SA Tool from in-service to standby state", "SA Tool switches to standby state after a configurable time of inactivity", "Operator switches to a third-party application", "Check Shift statistics", "Print shift statistics", "View historical reports", "Establish Wi-Fi or cellular network connection", "Establish Printer Connection", "Establish Payment Terminal Connection", "Change operator language", "In-App Training and FAQ", "Download Remote Lists"],
        "Operator sign-in": ["First-time user", "Existing user", "Operator sign-off"],
        "Modify screen brightness": ["Modify audio tone volume"],
        "Battery": ["Operator checks battery power level", "SA Tool battery drops below the low battery threshold", "SA Tool battery dies"],
        "Check SA Tool device information": ["Switch device mode between different SPs (DISTANCE BASED TRANSIT and Distance based Transit only)"],
        "Device states": ["Operator switches SA Tool from standby to in-service state", "Operator switches SA Tool from in-service to standby state", "SA Tool switches to standby state after a configurable time of inactivity", "Operator switches to a third-party application"],
        "Check Shift statistics": ["Print shift statistics", "View historical reports"],
        "Establish Wi-Fi or cellular network connection": ["Establish Printer Connection", "Establish Payment Terminal Connection"],
        "Change operator language": ["In-App Training and FAQ", "Download Remote Lists"],
        "All":["All"]
    }
    return jsonify({"sub_categories": sub_categories.get(category, [])})

@app.route('/get_test_scenarios', methods=['POST'])
def get_test_scenarios():
    global generated_test_scenarios
    data = request.get_json()
    functional_flow = data.get('functionalFlow')
    sub_category = data.get('subCategory')
    import time 
    # time.sleep(20) # by VK 
    response = run_all(functional_flow,sub_category)
    print("******************************")
    print("functional flow Name")
    print(functional_flow)
    print("Sub Flow Name")
    print(sub_category)
    print("--------------------------------")
    return jsonify({"message": "Success"})


@app.route('/view_test_scenarios', methods=['GET'])
def view_test_scenarios():    
    with open('Scenario_Data_New_data_v3.json', 'r') as fp: # changed file name
        file_contents = fp.read()
        file_contents = json.loads(file_contents)
        print(type(file_contents))
        #json.load(Final_Outcome, f)
    #return file_contents
    return jsonify({"scenarios": file_contents})

@app.route('/download_excel', methods=['GET'])
def download_excel():
    # Logic to generate and serve an Excel file
    # Placeholder for demonstration, actual implementation needed
    filename = pd.read_json("Scenario_Data_New_data_v2.json").to_excel("test_scenarios.xlsx")
    #filename = 'test_scenarios.xlsx'
    return send_from_directory('.', filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
