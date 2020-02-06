import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'dart:convert';
import 'API.dart';
import 'package:http/http.dart' as http;

void main() => runApp(new MaterialApp(home: new MyApp()));

class MyApp extends StatefulWidget {
  @override
  _MyAppState createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  FlutterLocalNotificationsPlugin flutterLocalNotificationsPlugin;

  var parsedJson = json.decode('{"new":[], "update":[]}');

  @override
  void initState() {
    super.initState();
    flutterLocalNotificationsPlugin = new FlutterLocalNotificationsPlugin();
    var android = new AndroidInitializationSettings('@mipmap/ic_launcher');
    var iOS = new IOSInitializationSettings();
    var initSetttings = new InitializationSettings(android, iOS);
    flutterLocalNotificationsPlugin.initialize(initSetttings);
  }

  Future onSelectNotification(String payload) {
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
    return Scaffold(
      appBar: new AppBar(
        title: new Text('Flutter Local Notification'),
      ),
      body: new Center(
        child: new RaisedButton(
          onPressed: () => createNotifications("", ""),
          child: new Text(
            'Demo',
            style: Theme.of(context).textTheme.headline,
          ),
        ),
      ),
    );
  }

  createNotifications(String username, String password) async {
    
    String url = "http://10.0.2.2:5000/api/v1/?username=$username&password=$password";
    
    http.Response response = await http.get(url);
    if (response.statusCode == 200) {
      setState(() {
        parsedJson = json.decode(response.body);
      });
      print("Success!");
    } else {
      print("Request failed with status: ${response.statusCode}.");
    }

    print(json.encode(parsedJson));
    List<dynamic> new_notifications = parsedJson["new"];
    List<dynamic> update_notifications = parsedJson["update"];

    int channel_id = 0;

    for (var update in parsedJson['new']) {
        String assignment = update['title'];
        String course = update['course'];
        String score = update['score'];
        String subject = "$course: $assignment has been graded";
        String body = "You recieved a $score";
        print(subject + " " + channel_id.toString());
        showNotification(subject, body, channel_id);
        channel_id++;
    }

    for (var update in parsedJson['update']) {
        String assignment = update['title'];
        String course = update['course'];
        String old_score = update['old_score'];
        String new_score = update['new_score'];
        String subject = "$course: $assignment has been updated";
        String body = "Your score was updated from $old_score to $new_score";
        print(subject + " " + channel_id.toString());
        showNotification(subject, body, channel_id);
        channel_id++;
    }

  }

  showNotification(String subject, String body, int channel_id) async {
    var android = new AndroidNotificationDetails(
        'channel id', 'channel NAME', 'CHANNEL DESCRIPTION',
        priority: Priority.High,importance: Importance.Max
    );
    var iOS = new IOSNotificationDetails();
    var platform = new NotificationDetails(android, iOS);
    await flutterLocalNotificationsPlugin.show(
        channel_id, subject, body, platform,
        payload: 'Nitish Kumar Singh is part time Youtuber');
  }
}