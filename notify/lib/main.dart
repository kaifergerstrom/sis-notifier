import 'package:flutter/material.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

// When the app starts, set it to the designated page
void main() => runApp(new MaterialApp(home: new MyApp()));

class MyApp extends StatefulWidget {
  @override
  State<StatefulWidget> createState() {
    return _MyAppState();
  }
}

class _MyAppState extends State<MyApp> {
  String _message = '';

  final FirebaseMessaging _firebaseMessaging = FirebaseMessaging();

  _register() {
    _firebaseMessaging.getToken().then((token) => print(token));
  }

  @override
  void initState() {
    // TODO: implement initState
    super.initState();
    getMessage();
  }
  
  void getMessage(){
    _firebaseMessaging.configure(
        onMessage: (Map<String, dynamic> message) async {
      print('on message $message');
      setState(() => _message = message["notification"]["title"]);
    }, onResume: (Map<String, dynamic> message) async {
      print('on resume $message');
      setState(() => _message = message["notification"]["title"]);
    }, onLaunch: (Map<String, dynamic> message) async {
      print('on launch $message');
      setState(() => _message = message["notification"]["title"]);
    });
  }

  @override
  Widget build(BuildContext context) {
    // TODO: implement build
    return Scaffold(
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: <Widget>[
              Text("Message: $_message"),
            OutlineButton(
              child: Text("Register My Device"),
              onPressed: () {
                _register();
              },
            ),
            // Text("Message: $message")
          ]),
        ),
      );
  }
}

/* Login Page */

class LoginPage extends StatefulWidget {
  @override
  State<StatefulWidget> createState() => new _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {

  // Username and password filter
  final TextEditingController _usernameFilter = new TextEditingController();
  final TextEditingController _passwordFilter = new TextEditingController();

  // Username and password placeholders
  String _username = "";
  String _password = "";

  bool isValid = false;

  _LoginPageState() {
    // Create listeners for username and password changes
    _usernameFilter.addListener(_usernameListen);
    _passwordFilter.addListener(_passwordListen);
  }

  // Listener to update username value
  void _usernameListen() {
    if (_usernameFilter.text.isEmpty) {
      _username = "";
    } else {
      _username = _usernameFilter.text;
    }
  }

  // Listener to update password value
  void _passwordListen() {
    if (_passwordFilter.text.isEmpty) {
      _password = "";
    } else {
      _password = _passwordFilter.text;
    }
  }

  // Structure of login page
  @override
  Widget build(BuildContext context) {
    return new Scaffold(
      appBar: _buildBar(context),
      body: new Container(
        padding: EdgeInsets.all(16.0),
        child: new Column(
          children: <Widget>[
            _buildTextFields(),
            _buildButtons(),
          ],
        ),
      ),
    );
  }

  // Header bar design for login
  Widget _buildBar(BuildContext context) {
    return new AppBar(
      title: new Text("Student VUE Login"),
      centerTitle: true,
    );
  }

  // Create text fields for login page
  Widget _buildTextFields() {
    return new Container(
      child: new Column(
        children: <Widget>[
          new Container(
            child: new TextField(
              controller: _usernameFilter,
              decoration: new InputDecoration(
                labelText: 'Student ID'
              ),
            ),
          ),
          new Container(
            child: new TextField(
              controller: _passwordFilter,
              decoration: new InputDecoration(
                labelText: 'Password'
              ),
              obscureText: true,
            ),
          )
        ],
      ),
    );
  }

  void _showDialog(String title, String body, bool error) {
    // flutter defined function
    showDialog(
      context: context,
      builder: (BuildContext context) {
        // return object of type Dialog
        return AlertDialog(
          title: new Text(title),
          content: new Text(body),
          actions: <Widget>[
            // usually buttons at the bottom of the dialog
            new FlatButton(
              child: new Text("Close"),
              onPressed: () {
                Navigator.of(context).pop();
              },
            ),
          ],
        );
      },
    );
  }

  // Create sign in button
  Widget _buildButtons() {
    return new Container(
      child: new Column(
        children: <Widget>[
          new RaisedButton(
            child: new Text('Login'),
            onPressed: () => _loginPressed(),
          ),
        ],
      ),
    );
    }


  // Run this function when login button pressed
  void _loginPressed() async {
    // Construct json to store in file
    _username = _username.trim();
    _password = _password.trim();

    // Check if any of the fields are empty, if so display error

    if (_username == "" || _password == "") {
      _showDialog("Empty Field", "Please fill out all fields!", true);
    } else {
      
      // String ip for server
      String ip = "10.0.2.2:5000";

      // Encode the inserted password for post request
      var bytes = utf8.encode(_password);
      var base64Str = base64.encode(bytes);

      // URL format for api call to flask server
      String url = "http://$ip/api/status?username=$_username&password=$base64Str";
      print(url);
      
      // Boolean if the credentials are valid
      bool isValid = false;

      // Get the response from the server and return the boolean value
      http.Response response = await http.get(url);
      if (response.statusCode == 200) {
        setState(() {
          // Assign the parsed json 
          isValid = (response.body).toLowerCase() == 'true';
        });
        print("Successfully fetched json from flask server!");
      } else {
        // Reset the parsed json if, errors
        isValid = false;
        print("Request failed with status: ${response.statusCode}.");
      }
      
      // If the informating provided is valid, save the variables in memory and create gradebook on server
      if (isValid) {
        var jsonData = '{ "username" : "$_username", "password" : "$_password"}';
        print("Login information is valid! Saving data!");
        _showDialog("Success!", "Succesfully saved StudentVue Credentials!.", false);
        //updateUserData(jsonData);  // Update and save json to user.json
      } else {
        _showDialog("Invalid Credentials", "Please enter a valid ID and password for your StudentVue account.", true);
        print("Invalid login information");
      }

    }
  }

}



