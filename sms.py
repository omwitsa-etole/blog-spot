import africastalking


africastalking.initialize(
    username='blogspot',
    api_key='c9c708b8793c22438908693e8cae1e053707d20f3f3741b75921aedea9dbf576'
)



class send_sms:
	def __init__(self,recipient):
		self.recipients = []
		self.sms = africastalking.SMS
		for r in recipient:
			self.recipients.append(r)
		
		self.send()		
	def send(self):
		recipients = self.recipients
		message = "Hey AT Ninja!";
		sender = "254716925063";
		try:
			response = self.sms.send(message, recipients, sender)
			print(response)
		except Exception as e:
			print(str(e))
			print (f'Houston, we have a problem: {e}')

send_sms(['+254716925063'])