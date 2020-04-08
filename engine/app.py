from flask import Flask, request, jsonify
import base64
from classes.DB import DB
from classes.SIS import SIS

app = Flask(__name__)

db = DB()
sis = SIS()


@app.route('/api/register', methods=['GET'])
def register():
    """
    Recieve SIS credentials and register them to the SQLite database
    """
    if request.method == 'GET':

        # Get data from URL sent from phone
        device_id = request.args['device_id']
        username = request.args['username']
        coded_password = request.args['password']

        password = base64.b64decode(coded_password).decode("utf-8")  # Decode the password for SIS

        isValid = sis.validate_credentials(username, password)  # Check if the credentials are valid
        if isValid:
            db.create_user(device_id, username, coded_password)  # If valid add the user to the SQLite database
            return "true"
        else:
            return "false"

        
if __name__ == '__main__':
    app.run()