import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'user.dart';

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

  // Physical formatting of homepage
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: new AppBar(
        title: new Text('Flutter Local Notification'),
      ),
      body: new Center(
        child: new RaisedButton(
          onPressed: () => displayNotifications(),
          child: new Text(
            'Demo',
            style: Theme.of(context).textTheme.headline,
          ),
        ),
      ),
    );
  }

  // Call the api and get the data, then display the notifications
  displayNotifications() async {
    
    // Get user info from user.json file (local)
    String user_info = await getUserData();
    var user_data = json.decode(user_info);

    // Parse json object into username and password data
    String username = user_data['username'];
    String password = user_data['password'];
  
    // URL format for api call to flask server
    String url = "http://10.0.2.2:5000/api/v1/?username=$username&password=$password";
    
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
      title: new Text("Simple Login Example"),
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
                labelText: 'Email'
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

  // Create sign in button
  Widget _buildButtons() {
    return new Container(
      child: new Column(
        children: <Widget>[
          new RaisedButton(
            child: new Text('Login'),
            onPressed: _loginPressed,
          ),
        ],
      ),
    );
    }


  // Run this function when login button pressed
  void _loginPressed () {
    // Construct json to store in file
    _username = _username.trim();
    _password = _password.trim();
    var jsonData = '{ "username" : "$_username", "password" : "$_password"}';
    updateUserData(jsonData);  // Update and save json to user.json
  }

}



