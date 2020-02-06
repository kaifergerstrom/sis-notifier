import 'package:path_provider/path_provider.dart';
import 'dart:io';

// Get directory path without file
Future<String> get _localPath async {
  final directory = await getApplicationDocumentsDirectory();
  // For your reference print the AppDoc directory 
  print(directory.path);
  return directory.path;
}

// Define the absolute path to the user.json file
Future<File> get _localFile async {
  final path = await _localPath;
  return File('$path/user.json');
}

// Open and parse the file as string
Future<String> getUserData() async {
  try {
    // Get the file path and file
    final file = await _localFile;
    
    // Extract the contents of the file
    var contents;
    contents = await file.readAsString();
    return contents;
  } catch (e) {
    // If encountering an error, return 0.
    print("Unable to open user.json");
    return "";
  }

}

Future<File> updateUserData(String data) async {
  final file = await _localFile;
  // Write the file.
  return file.writeAsString('$data');
}