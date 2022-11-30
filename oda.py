import requests
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup

load_dotenv()

class Oda:
	def __init__(self):
		self.csrftoken = None
		self.requests = requests.session()

	def login(self, username, password):
		response = self.requests.get('https://oda.com/no/user/login/')
		csrf_middleware_token = self._get_csrf_middleware_token(response.text)
		body = {
			"csrfmiddlewaretoken": csrf_middleware_token,
			"username": username,
			"password": password,
		}
		response = self.requests.post('https://oda.com/no/user/login/', 
			headers={
				"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
				"Referer": "https://oda.com/no/user/login/",
				"Content-Type": "application/x-www-form-urlencoded",
			},
			data=body
		)
		self.csrftoken = response.cookies.get_dict()["csrftoken"] 

		return self

	def prepare_checkout(self, delivery_slot_id):
		payload = {
			"delivery_slot_id":delivery_slot_id,
			"is_unattended_delivery":True,
			"in_modal":False,
			"delivery_address_id":os.getenv("DELIVERY__ID")
		}
		self.requests.post("https://oda.com/api/v1/slot-picker/info/", 
			headers={
				"Accept": "application/json",
				"Cookie": self.cookie,
				"X-CSRFToken": self.csrftoken, 
				"Referer": "https://oda.com/no/checkout/delivery/time/",
			},
			json=payload)
		return self

	def add_gifflar_to_cart(self):
		self.requests.post("https://oda.com/no/cart/products/", 
			headers={
				"Accept": "*/*",
				"Content-Type": "application/json; charset=UTF-8",
				"X-CSRFToken": self.csrftoken,
				"Referer": "https://oda.com/no/search/?q=gifflar",
			},
			json=[{"product_id":"11470","quantity":1,"delete":False,"tracking_location":"Cart"}],
		)

		return self

	def get_next_delivery_slot(self):
		response = self.requests.get("https://oda.com/api/v1/slot-picker/slots/?from-index=3&num-days=3", 
			headers={
				"Accept": "*/*",
			},
		)
		results = response.json()
		for i in results['delivery_slots']:
			if not i['is_unavailable']:
				return i
		return None

	def submit(self):
		html = self.requests.get("https://oda.com/no/checkout/confirm/").text
		csrf_middleware_token = self._get_csrf_middleware_token(html)

		body = {
			"csrfmiddlewaretoken": csrf_middleware_token,
			"22-storedPaymentMethodId": os.getenv("PAYMENT_METHOD"),
			"22-colorDepth": "24",
			"22-javaEnabled": "false",
			"22-language": "en-US",
			"22-screenHeight": "1080",
			"22-screenWidth": "1920",
			"22-timeZoneOffset": "-60",
		}
		response = self.requests.post("https://oda.com/no/checkout/confirm/22/", 
			headers={
				"Accept": "application/json",
				"X-CSRFToken": self.csrftoken,
				"Referer": "https://oda.com/no/checkout/confirm/",
				"Content-Type": "application/x-www-form-urlencoded",
			},
			data=body
		)

	def _get_csrf_middleware_token(self, html):
		soup = BeautifulSoup(html, 'html.parser')
		csrf_middleware_token = soup.find("input", {
			"name":"csrfmiddlewaretoken"
		}).attrs["value"]

		return csrf_middleware_token

if __name__ == "__main__":
	oda = Oda().login(
		os.getenv("EMAIL"),
		os.getenv("PASSWORD")
	)
	delivery_slot = oda.get_next_delivery_slot()
	if delivery_slot is None:
		raise Exception("Did not find a delivery slot")
	oda.prepare_checkout(delivery_slot['id'])
	oda.submit()

