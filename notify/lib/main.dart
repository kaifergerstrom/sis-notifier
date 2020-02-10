import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'user.dart';
import 'package:encrypt/encrypt.dart';

// When the app starts, set it to the designated page
void main() => runApp(new MaterialApp(home: new HomePage()));

// Constructor for HomePage object
class HomePage extends StatefulWidget {
  @override
  _HomePageState createState() => _HomePageState();
}

// HomePageState (actual code that runs when on HomePage)
class _HomePageState extends State<HomePage> {
  // Define notifications plugins for flutter
  FlutterLocalNotificationsPlugin flutterLocalNotificationsPlugin;

  Timer timer;

  // Define parsedJson object to store data
  var parsedJson = json.decode('{"new":[], "update":[]}');


  @override
  void initState() {
    // Define notifications plugin for IOS and Android
    super.initState();
    flutterLocalNotificationsPlugin = new FlutterLocalNotificationsPlugin();
    var android = new AndroidInitializationSettings('@mipmap/ic_launcher');
    var iOS = new IOSInitializationSettings();
    var initSetttings = new InitializationSettings(android, iOS);
    flutterLocalNotificationsPlugin.initialize(initSetttings);

    timer = Timer.periodic(Duration(seconds: 30), (Timer t) => displayNotifications());

  }
  
  Future navigateToLogin(context) async {
    Navigator.push(context, MaterialPageRoute(builder: (context) => LoginPage()));
  }

  Future onSelectNotification(String payload) {
    // Build the notification payload
    debugPrint("payload : $payload");
    showDialog(
      context: context,
      builder: (_) => new AlertDialog(
        title: new Text('Notification'),
        content: new Text('$payload'),
      ),
    );
  }


  @override
  Widget build(BuildContext context) {
    return new Scaffold(
        appBar: new AppBar(
          title: new Text("SIS Notifier"),
        ),
        body: new Center(
          child: new Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: <Widget>[
              new Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: <Widget>[
                  new RaisedButton(
                    padding: const EdgeInsets.all(8.0),
                    textColor: Colors.white,
                    color: Colors.blue,
                    onPressed: () => displayNotifications(),
                    child: new Text("Run Notifications"),
                  ),
                  new RaisedButton(
                    onPressed: () => navigateToLogin(context),
                    textColor: Colors.white,
                    color: Colors.red,
                    padding: const EdgeInsets.all(8.0),
                    child: new Text(
                      "Change StudentVUE Information",
                    ),
                  ),
                ],
              )
            ],
          ),
        ));
  }

  sayHi() async {
    print("Hello");
  }

  // Call the api and get the data, then display the notifications
  displayNotifications() async {
    
    // Get user info from user.json file (local)
    String user_info = await getUserData();
    var user_data = json.decode(user_info);

    // Parse json object into username and password data
    String username = user_data['username'];
    String password = user_data['password'];
    
    var bytes = utf8.encode(password);
    var base64Str = base64.encode(bytes);

    String ip = "10.0.2.2:5000";

    // URL format for api call to flask server
    String url = "http://$ip/api/update?username=$username&password=$base64Str";
    print(url);
    
    // Get http response from flask script
    http.Response response = await http.get(url);
    if (response.statusCode == 200) {
      setState(() {
        // Assign the parsed json 
        parsedJson = json.decode(response.body);
      });
      print("Successfully fetched json from flask server!");
    } else {
      // Reset the parsed json if, errors
      parsedJson = json.decode('{"new":[], "update":[]}');
      print("Request failed with status: ${response.statusCode}.");
    }
  
    // Define new and update columns for json return
    List<dynamic> new_notifications = parsedJson["new"];
    List<dynamic> update_notifications = parsedJson["update"];

    // Int to increment channel_id which sends seperate notifications
    int channel_id = 0;

    // Construct the data for new notification type
    for (var update in parsedJson['new']) {
      // Data from flask json
      String assignment = update['title'];
      String course = update['course'];
      String score = update['score'];

      // Notification header and body
      String subject = "$course: $assignment has been graded";
      String body = "You recieved a $score";

      // Show the notification
      showNotification(subject, body, channel_id);

      channel_id++;  // Increment channel id for next channel
    }

    // Construct the data for update notification type
    for (var update in parsedJson['update']) {
      // Data from flask json
      String assignment = update['title'];
      String course = update['course'];
      String old_score = update['old_score'];
      String new_score = update['new_score'];

      // Notification header and body
      String subject = "$course: $assignment has been updated";
      String body = "Your score was updated from $old_score to $new_score";

      // Show the notification
      showNotification(subject, body, channel_id);
      
      channel_id++;  // Increment channel id for next channel
    }

    print(parsedJson);

  }

  showNotification(String subject, String body, int channel_id) async {
    // Send the notifications to IOS or Android
    var android = new AndroidNotificationDetails(
        'channel id', 'channel NAME', 'CHANNEL DESCRIPTION',
        priority: Priority.High,importance: Importance.Max
    );
    var iOS = new IOSNotificationDetails();
    var platform = new NotificationDetails(android, iOS);
    await flutterLocalNotificationsPlugin.show(
        channel_id, subject, body, platform,
        payload: '');
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
        updateUserData(jsonData);  // Update and save json to user.json
      } else {
        _showDialog("Invalid Credentials", "Please enter a valid ID and password for your StudentVue account.", true);
        print("Invalid login information");
      }

    }
  }

}



