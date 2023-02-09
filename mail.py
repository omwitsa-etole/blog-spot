import smtplib, ssl

def mail(email_to, code):
	port = 465  # For SSL
	smtp_server = "smtp.gmail.com"
	password = "tuhkspzasphcvflr"
	sender = "omwitsabradone@gmail.com"
	receivers = [email_to]

	message = """
	Subject: BlogSpot Room Verification Code

	Your email has been used to request access to BlogSpot's Rooms. The verification code is 
	"""+str(code)

	context = ssl.create_default_context()
	with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
		try:
			server.login(sender, password)
			server.sendmail(sender, receivers, message)
			return "success"
		except Exception as e:
			return str(e)
			pass

def notify(email_to, from_user, msg, host):
	print("here")
	print(email_to)
	print(from_user)
	print(msg)
	port = 465  # For SSL
	smtp_server = "smtp.gmail.com"
	password = "tuhkspzasphcvflr"
	sender = "omwitsabradone@gmail.com"
	receivers = [email_to]

	message = """
	Subject: You Have a new Message in your BlogSpot Room

	Your have a new message from """+ str(from_user) +""" in your BlogSpot Room\n
	\t Message: """+str(msg)+""" \n\nLogin to Rooms to View this message, click here """+str(host)+"""/api/nx/rooms 
	"""

	context = ssl.create_default_context()
	with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
		try:
			server.login(sender, password)
			server.sendmail(sender, receivers, message)
			return "success"
		except Exception as e:
			return str(e)
			pass
