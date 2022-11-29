import requests
from dotenv import load_dotenv
import os

load_dotenv()


class Oda:
	def __init__(self):
		pass


	def prepare_checkout(self):
		response = requests.post("https://oda.com/api/v1/slot-picker/info/", 
			headers={
				"Accept": "application/json",
				"Cookie": os.getenv("COOKIE"),
				"X-CSRFToken": os.getenv("CSRF"),
				"Referer": "https://oda.com/no/checkout/delivery/time/",
			},
			# selected from the slot selector
			json={"delivery_slot_id":639939,"is_unattended_delivery":True,"in_modal":False,"delivery_address_id":os.getenv("DELIVERY__ID")})
		print(response.text)
		return self


	def submit(self):
		body = {
			# INSIDE THE HTML OF THE REQUEST
			"csrfmiddlewaretoken": os.getenv("csrfmiddlewaretoken"),
			# INSIDE THE REQUESTS
			"22-storedPaymentMethodId": os.getenv("PAYMENT_METHOD"),
			"22-colorDepth": "24",
			"22-javaEnabled": "false",
			"22-language": "en-US",
			"22-screenHeight": "1080",
			"22-screenWidth": "1920",
			"22-timeZoneOffset": "-60",
		}
		response = requests.post("https://oda.com/no/checkout/confirm/22/", 
		headers={
			"Accept": "application/json",
			"Cookie": os.getenv("COOKIE"),
			"X-CSRFToken": os.getenv("CSRF"),
			"Referer": "https://oda.com/no/checkout/confirm/",
			"Content-Type": "application/x-www-form-urlencoded",
		},
		data=body
		# selected from the slot selector
		#json={"delivery_slot_id":639939,"is_unattended_delivery":True,"in_modal":False,"delivery_address_id":os.getenv("DELIVERY__ID")}
		)
		print(response.text)

if __name__ == "__main__":
#	Oda().prepare_checkout().submit()
	Oda().submit()
