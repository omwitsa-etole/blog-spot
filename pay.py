import paypalrestsdk
import logging

paypalrestsdk.configure({
  "mode": "sandbox", # sandbox or live
  "client_id": "AVc84hHRtSGyiJTXhhGW7tOgenYX5mYl2vbIMZROpc-U2FVMFdm7Y7EBgyyFdgLr-yPKDK8_Y9D1lkOm",
  "client_secret": "EH58LQLP8BgK79tdCyCmb3ideMiofx1mGw_pKaLEdyyzOAEMTRQyJaN7NjGj_er2LlNXkj2bBIUj6hT9" })

def Pay(name, amount, description, url):
	payment = paypalrestsdk.Payment({
	    "intent": "sale",
	    "payer": {
		"payment_method": "paypal"},
	    "redirect_urls": {
		"return_url": url+"?success",
		"cancel_url": url+"?fail"},
	    "transactions": [{
		"item_list": {
		    "items": [{
		        "name": "template purchase",
		        "sku": "template purchase",
		        "price": float(amount),
		        "currency": "USD",
		        "quantity": 1}]},
		"amount": {
		    "total": float(amount),
		    "currency": "USD"},
		"description": description}]})

	if payment.create():
		return "success"
	else:
		return payment.error