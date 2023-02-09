import imp
import os
import sys
from datetime import date as d
import requests
from authorizenet import apicontractsv1
from authorizenet.apicontrollers import createTransactionController
from decimal import Decimal
import models

#customer_id, price_id, item_id
CONSTANTS = ["36GYcjD9HX", "769rYK9Hzm37dgLT"]


def charge_credit_card(email, amount, items, name, card_number, carddate, cvv, address, city, postal, description, invoice):
	try:
		time = d.today()
		merchant_auth = apicontractsv1.merchantAuthenticationType()
		merchant_auth.name = CONSTANTS[0]
		merchant_auth.transactionKey = CONSTANTS[1]

		credit_card = apicontractsv1.creditCardType()
		credit_card.cardNumber = card_number
		credit_card.expirationDate = carddate
		credit_card.cardCode = cvv
		customerAddress = apicontractsv1.customerAddressType()
		customerAddress.firstName = name[0]
		customerAddress.lastName = name[1]
		#customerAddress.company = "Souveniropolis"
		customerAddress.city = city
		customerAddress.state = city
		customerAddress.zip = postal
		customerAddress.country = address

		# Set the customer's identifying information
		customerData = apicontractsv1.customerDataType()
		customerData.type = "individual"
		customerData.id = email
		customerData.email = email
		order = apicontractsv1.orderType()
		order.invoiceNumber = invoice
		order.description = description
		payment = apicontractsv1.paymentType()
		payment.creditCard = credit_card

		

		transaction_request = apicontractsv1.transactionRequestType()
		transaction_request.transactionType ="authCaptureTransaction"
		transaction_request.amount = Decimal(amount)
		transaction_request.order = order
		transaction_request.transId = str(email)+"_"+str(time)
		transaction_request.payment = payment

		request = apicontractsv1.createTransactionRequest()
		request.merchantAuthentication = merchant_auth
		request.refId = str(email)+"_"+str(time)
		request.transactionRequest = transaction_request
		

		transaction_controller = createTransactionController(request)
		transaction_controller.execute()

		api_response = transaction_controller.getresponse()
		response = response_mapper(api_response)
		
	except Exception as e:
		print(str(e))
		pass
	return response
	

def response_mapper(api_response):
    response = models.TransactionResponse()

    if api_response is None:
        response.messages.append("No response from api")
        return response
    
    if api_response.messages.resultCode=="Ok":
        response.is_success = hasattr(api_response.transactionResponse, 'messages')
        if response.is_success:
            response.messages.append(f"Successfully created transaction with Transaction ID: {api_response.transactionResponse.transId}")
            response.messages.append(f"Transaction Response Code: {api_response.transactionResponse.responseCode}")
            response.messages.append(f"Message Code: {api_response.transactionResponse.messages.message[0].code}")
            response.messages.append(f"Description: {api_response.transactionResponse.messages.message[0].description}")
        else:
            if hasattr(api_response.transactionResponse, 'errors') is True:
                response.messages.append(f"Error Code:  {api_response.transactionResponse.errors.error[0].errorCode}")
                response.messages.append(f"Error message: {api_response.transactionResponse.errors.error[0].errorText}")
        return response

    response.is_success = False
    response.messages.append(f"response code: {api_response.messages.resultCode}")
    return response

def charge_credit(email, amount, items, name, card_number, carddate, cvv, address, city, postal, description, invoice):
	try:
		msg = []
		msg.append(None)
		time = d.today()
		# Create a merchantAuthenticationType object with authentication details
		# retrieved from the constants file
		merchantAuth = apicontractsv1.merchantAuthenticationType()
		merchantAuth.name = CONSTANTS[0]
		merchantAuth.transactionKey = CONSTANTS[1]

		# Create the payment data for a credit card
		creditCard = apicontractsv1.creditCardType()
		creditCard.cardNumber = card_number
		creditCard.expirationDate = carddate
		creditCard.cardCode = cvv

		# Add the payment data to a paymentType object
		payment = apicontractsv1.paymentType()
		payment.creditCard = creditCard

		# Create order information
		order = apicontractsv1.orderType()
		order.invoiceNumber = invoice
		order.description = description

		# Set the customer's Bill To address
		customerAddress = apicontractsv1.customerAddressType()
		customerAddress.firstName = name[0]
		customerAddress.lastName = name[1]
		#customerAddress.company = "Souveniropolis"
		customerAddress.address = str(postal)+", "+str(city)+", "+str(address)
		customerAddress.city = city
		customerAddress.state = city
		customerAddress.zip = postal
		customerAddress.country = address

		# Set the customer's identifying information
		customerData = apicontractsv1.customerDataType()
		customerData.type = "individual"
		customerData.id = email
		customerData.email = email

		# Add values for transaction settings
		duplicateWindowSetting = apicontractsv1.settingType()
		duplicateWindowSetting.settingName = "duplicateWindow"
		duplicateWindowSetting.settingValue = "600"
		settings = apicontractsv1.ArrayOfSetting()
		settings.setting.append(duplicateWindowSetting)

		# setup individual line items
		for item in items:
			a = "line_item_"
			b = str(item[0])
			globals()[a+b] = apicontractsv1.lineItemType()
			globals()[a+b].itemId = item[0]
			globals()[a+b].name = item[2]
			globals()[a+b].description = item[2]
			globals()[a+b].quantity = "1"
			globals()[a+b].unitPrice = item[3]


		# build the array of line items
		line_items = apicontractsv1.ArrayOfLineItem()
		for item in items:	
			a = "line_item_"
			b = str(item[0])
			line_items.lineItem.append(globals()[a+b])	

		# Create a transactionRequestType object and add the previous objects to it.
		transactionrequest = apicontractsv1.transactionRequestType()
		transactionrequest.transactionType = "authCaptureTransaction"
		transactionrequest.amount = amount
		transactionrequest.payment = payment
		transactionrequest.order = order
		transactionrequest.billTo = customerAddress
		transactionrequest.customer = customerData
		transactionrequest.transactionSettings = settings
		transactionrequest.lineItems = line_items

		# Assemble the complete transaction request
		createtransactionrequest = apicontractsv1.createTransactionRequest()
		createtransactionrequest.merchantAuthentication = merchantAuth
		createtransactionrequest.refId = "BlogSpot_purchase_"+str(email)+"_"+str(time)
		createtransactionrequest.transactionRequest = transactionrequest
		# Create the controller
		createtransactioncontroller = createTransactionController(
		createtransactionrequest)
		createtransactioncontroller.execute()

		response = createtransactioncontroller.getresponse()

		if response is not None:
			# Check to see if the API request was successfully received and acted upon
			if response.messages.resultCode == "Ok":
				# Since the API request was successful, look for a transaction response
				# and parse it to display the results of authorizing the card
				if hasattr(response.transactionResponse, 'messages') is True:
					msg[0] = "success"
					tr_id = response.transactionResponse.transId

					tr_code = response.transactionResponse.responseCode

					tr_message = response.transactionResponse.messages.message[0].code
					tr_description = response.transactionResponse.messages.message[0].description
					msg.append(tr_id);msg.append(tr_code);msg.append(tr_message);msg.append(tr_description)
				else:
					msg[0] = "failed"
					if hasattr(response.transactionResponse, 'errors') is True:
						tr_code = response.transactionResponse.errors.error[0].errorCode
						tr_message = response.transactionResponse.errors.error[0].errorText
						msg.append(tr_code);msg.append(tr_message)    
			# Or, print errors if the API request wasn't successful
			else:
				msg[0] = "api-fail"
				if hasattr(response, 'transactionResponse') is True and hasattr(
					response.transactionResponse, 'errors') is True:
					tr_code =  response.transactionResponse.errors.error[0].errorCode

					tr_text = response.transactionResponse.errors.error[0].errorText

				else:
					tr_code = response.messages.message[0]['code'].text
					tr_text = response.messages.message[0]['text'].text
					msg.append(tr_code)
					msg.append(tr_text)
		else:
			msg[0] = "Null Response"
	    
	except Exception as e:
		print(str(e))
		pass
	return msg
