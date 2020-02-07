from flask import Flask, request, jsonify
from SIS import SIS
import base64

app = Flask(__name__)

@app.route('/api/update', methods=['GET'])
def update():
    if request.method == 'GET':
        username = request.args['username']
        password = request.args['password']

        password = base64.b64decode(password).decode("utf-8")

        SISpy = SIS(username,password) # username, password 
        notifications = SISpy.update_grades()
        print(notifications)
        return jsonify(notifications)

@app.route('/api/status', methods=['GET'])
def status():
    if request.method == 'GET':
        username = request.args['username']
        password = request.args['password']

        password = base64.b64decode(password).decode("utf-8")

        SISpy = SIS(username,password) # username, password 
        notifications = SISpy.update_grades()
        status = SISpy.isLoggedIn()
        return status

if __name__ == '__main__':
    app.run()