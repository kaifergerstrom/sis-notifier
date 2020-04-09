from pyfcm import FCMNotification
import os

class Notify:

	def __init__(self):
		self.push_service = FCMNotification(api_key=self.__get_api_key())  # Create instance of FCM
	
	def __get_api_key(self):
		"""Get the API key from ../key.txt, if it does not exist create it

		:param none:

		:returns: string of api key
		"""
		# Get one folder back from file location
		dirname, filename = os.path.split(os.path.abspath(__file__))
		key_path = f"{os.path.dirname(dirname)}\key.txt"

		error = "No API key in key.txt, it can be found at https://console.firebase.google.com/project/sis-notifier/settings/cloudmessaging"

		try:  # If the file exists, check if the key is in the file
			f = open(key_path, 'r')
			api_key = f.readline()

			if len(api_key) == 0:  # If there is no key in key.txt, error out
				raise Exception(error)

		except IOError:  # If the file does not exist, create it
			f = open(key_path, 'w')
			raise Exception(error)
		
		return api_key
		

	def send_notification(self, registration_ids, title, body):
		"""Get list of device ids associated to certain SIS account

		:param registration_ids: List of device ids to send to
		:param title: notification title
		:param body: notification body text

		:returns: list of device ids
		"""
		self.push_service.notify_multiple_devices(registration_ids=registration_ids, message_title=title, message_body=body)


if __name__ == "__main__":
	registration_id = "fiRnqL7SI-Q:APA91bHosto4FalcAxd5Xw-AsfOHrS9X0k80quy7rkxpnRuteCi00R0I6_WBpP33bNg17HVaj0GrVfV1IOiaeH0OksE40EUYFAme_R7kUAknKEnorBFTdOlaUvhcmStE4gI7fupAbDzs"
	notify = Notify()
	notify.send_notification([registration_id], "Hello World!", "Wassup my bro")
	