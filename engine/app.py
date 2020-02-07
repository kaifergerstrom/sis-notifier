from flask import Flask, request, jsonify
from SIS import SIS
import base64

app = Flask(__name__)

@app.route('/api/v1/', methods=['GET'])
def API():
    if request.method == 'GET':
        username = request.args['username']
        password = request.args['password']

        password = base64.b64decode(password).decode("utf-8")

        SISpy = SIS(username,password) # username, password 
        notifications = SISpy.update_grades()
        print(notifications)
        return jsonify(notifications)

if __name__ == '__main__':
    app.run()