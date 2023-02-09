from flask import Flask, render_template, request, redirect, url_for, session, abort, flash
import random
import mysql.connector
import datetime
import webbrowser
import socket
#from werkzeug import secure_filename
import vonage
from datetime import date
from datetime import timedelta
#from guppy import hpy
import psutil
import os
#import shutil
from twilio.rest import Client
import werkzeug.exceptions
from werkzeug.exceptions import HTTPException

from cryptography.fernet import Fernet
import sched, time
import sys
app = Flask(__name__)
app.debug = True
#app.secret_key = 'app@BlogSpot'
#app = Flask(__name__)
#app.debug = True
app.secret_key = 'app@BlogSpot'
#app.config['MYSQL_HOST'] = 'localhost'
#app.config['MYSQL_USER'] = 'root'
#app.config['MYSQL_PASSWORD'] = 'root'
code = ""
verification = ""
send_end = {}


class Payements:
	def __init__(self, pay, amt):
		self.paytype = pay
		self.amount = amt

class Vars:
	
	mssg = [None]
	paytype = None
	amount = 0

class TimedValue:

    def __init__(self):
        self._started_at = datetime.datetime.now()

    def __call__(self):
        time_passed = datetime.datetime.now() - self._started_at
        print("here")
        print(time_passed.total_seconds())
        if time_passed.total_seconds() > 60*2:
            return True
        return False

class CK:
	def __init__(self):
		self.cookies = {}
	def setCookie(self, name, val):
		self.time_set = datetime.datetime.now()
		self.set_cookie = {name: val}
		self.cookies.update(self.set_cookie)
		
	def getCookie(self, name):
		time_passed = datetime.datetime.now() - self.time_set
		if time_passed.total_seconds() > 60*3:
			self.cookies = {}
			return False
		else:
			try:
				return self.cookies[name]
			except KeyError:
				return False
				pass

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def page_err(e):
	return render_template('500.html'), 500



@app.errorhandler(405)
def method_not_allowed(e):
    if request.path.startswith('/api/'):
	#if session.get("loggedin")
        return jsonify(message="Method Not Allowed"), 405
    else:
        return render_template("405.html"), 405




def connector():
	"""
	db = mysql.connector.connect(host="localhost",    # your host, usually localhost
                     user="root",         # your username
                     passwd="root",  # your password
                     db="dbo")
	"""
	for i in range(0,8):
		try:
			db = mysql.connector.connect(host="192.185.81.65",    # your host, usually localhost
		             user="askabcry_admim",         # your username
		             passwd="tryandhackme",  # your password
		             db="askabcry_rooms")
			break
		except Exception as e:
			print(str(e))
			pass
	#"""
	if db == None:
		raise "No connection"

	return db


def pay(phone, amount):
	pass

def notification(description):
	try:
		while True:
			try:
				db = connector()
				break
			except:
				pass
		cur = db.cursor(buffered=True)
		cur.execute('INSERT INTO notifications (notification) VALUES (%s)', (description, ))
	except Exception as e:
		print(str(e))
		db.rollback()
		pass
	finally:
		db.commit()
		db.close()
def alert(description):
	notification(description)
	#client = vonage.Client(key="923c97c5", secret="2sceTYgOJBBD3esG")
	#sms = vonage.Sms(client)
	#responseData = sms.send_message(
	    #{
		#"from": "Blogspot ",
		#"to": "254717881525",
		#"text": description,
	    #}
	#)
	account_sid = "ACe49b09af512780159044b3221769b9af"#os.environ['TWILIO_ACCOUNT_SID']
	auth_token = "c28188c06904eb88cd3a7c41fb757113"#os.environ['TWILIO_AUTH_TOKEN']
	client = Client(account_sid, auth_token)

	message = client.messages.create(
	  body=description,
	  from_='+16402238067',
	  to='+254717881525'
	)
	#if responseData["messages"][0]["status"] == "0":
	if message.sid:
	    msg = "success"
	else:
	    msg = "Message failed with error: {responseData['messages'][0]['error-text']}"
	return msg

@app.route("/donate/paypal", methods=['GET','POST'])
def paypal():
	return render_template("paypal.html")
@app.route("/api/v/donate/<mode>", methods =['POST'])
def donate(mode):
	msg = None
	if request.method == 'POST' and "amount" in request.form and "phone" in request.form:
		if mode == "mpesa":
			phone = request.form["phone"]
			amount = request.form["amount"]
			while True:
				if len(phone) < 12 or len(phone) > 12:
					msg = "Invalid phone number"	
					break
				
				try:
					msg = pay(phone, amount)
					break
				except Exception as e:
					print(str(e))
					break
			try:
				while True:
					try:
						db = connector()
						break
					except:
						pass
				cur = db.cursor(buffered=True)
				cur.execute("INSERT INTO donations (user, amount, mode) VALUES(%s, %s, %s)", (user, amount, mode, ))
				msg = "donation recieved, thank you"
			except Exception as e:
				print(str(e))
				msg = "error during transaction"
				db.rollback()
				pass
			finally:
				db.commit()
				db.close()
				alert(user+" has transferred "+amount+" to your mpesa")
		if mode == "paypal":
			msg = None
			date = str(datetime.datetime.now())
			user = request.form["email"]
			amount = request.form["amount"]
			try:
				while True:
					try:
						db = connector()
						break
					except:
						pass
				cur = db.cursor(buffered=True)
				cur.execute("INSERT INTO donations (user, amount, mode) VALUES(%s, %s, %s)", (user, amount, mode, ))
				msg = "donation recieved, thank you"
			except Exception as e:
				print(str(e))
				msg = "error during transaction"
				db.rollback()
				pass
			finally:
				db.commit()
				db.close()
				alert(user+" has transferred "+amount+" to your paypal")
			return msg
		if mode == "crypto":
			pass
	print(msg)
def new_user(ip, agnt):
	try:
		while True:
			try:
				db = connector()
				break
			except:
				pass
		cur = db.cursor(buffered=True)
		cur.execute('SELECT * FROM visitors WHERE ip_addr =%s', (ip, ))
		res = cur.fetchall()
		if res:
			cur.execute('UPDATE visitors SET is_new=1 WHERE ip_addr=%s', (ip, ))
		else:
			sql = "INSERT INTO visitors (ip_addr, is_new, agent) VALUES(%s, 0, %s)"
			cur.execute(sql, (ip, agnt, ))
	except Exception as e:
		print(str(e))
		db.rollback()
		pass
	finally:
		db.commit()
		db.close()
@app.route("/", methods=['GET'])
def landing():
	return render_template('landing.html')

@app.route("/<blogger>", methods=['GET', 'POST'])
def home(blogger):
	
	is_routable = "NULL"
	if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
		is_routable = request.environ['REMOTE_ADDR']
	else:
		is_routable = request.environ['HTTP_X_FORWARDED_FOR']
	agnt = request.headers.get('User-Agent')
	time = datetime.datetime.now()
	new_user(str(is_routable), agnt)
	#is_routable = request.environ.get('HTTP_X_REAL_IP', request.remote_addr) 
	hostname = is_routable
	imgs = ['analysis.jpg', 'computercode.jpeg', 'ux.jpg']
	imgs=random.choice(imgs)
	return render_template("templates/template_2.html", **locals())


@app.route("/read/projects/<title>", methods=['POST', 'GET'])
def read(title):
	if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
		is_routable = request.environ['REMOTE_ADDR']
	else:
		is_routable = request.environ['HTTP_X_FORWARDED_FOR']
	hostname = is_routable
	if title:
		#title = request.form['title']
		return render_template("blog.html", **locals())	
	return render_template("blog.html", **locals())
@app.route("/projects/completed", methods=['GET'])
def projects():
	
	imgs = ['analysis.jpg', 'computercode.jpeg', 'ux.jpg']
	imgs=random.choice(imgs)
	
	return render_template("projects.html", **locals())
	
@app.route("/exec", methods=['POST', 'GET'])
def assign():
	global code
	hostname=socket.gethostname()
	IPAddr=socket.gethostbyname(hostname)
	code = None
	if request.method == 'POST' or request.method=='GET':
		if 'code' in request.form:
			code = request.form["code"]
	return code
		
@app.route("/exec/<lang>", methods=['GET'])
def execute(lang):
	global code
	print(code)
	if request.method == 'GET':
		code = code
	return render_template("exec.html", **locals())
@app.route("/chat/user", methods=['POST', 'GET'])
def messages():
	if request.method == 'POST':
		if 'email' in request.form:
			session["user"] = request.form["email"]
			message = request.form["message"]
			to = request.form["to"]
			msg = None
			key = Fernet.generate_key()
			fernet = Fernet(key)
			encMessage = fernet.encrypt(message.encode())
			try:
				while True:
					try:
						db = connector()
						break
					except:
						pass
				cur = db.cursor(buffered=True)
				
				cur.execute("INSERT INTO messages (user, to_user, message, dkey) VALUES(%s, %s, %s, %s)", (session["user"], to, encMessage,key, ))
				msg = "message sent"
			except Exception as e:
				print(str(e))
				msg = "error during transaction"
				db.rollback()
				pass
			finally:
				db.commit()
				db.close()
			return msg
	if request.method == 'GET':
		if session.get('user') is not None:
			messages = []
			try:
				while True:
					try:
						db = connector()
						break
					except:
						pass
				cur = db.cursor(buffered=True)
				cur.execute('SELECT * FROM messages WHERE user =%s', (session['user'], ))
				messages = cur.fetchall()
				
			except Exception as e:
				db.rollback()
				print(str(e))
				pass
			finally:
				db.close()
			return render_template("messages.html", messages=messages, n=len(messages), Fernet=Fernet)
@app.route("/<mode>")
def Api(mode):
	print(mode)
	if mode == "api" and session.get("loggedin") == None:
		return redirect(signin)
@app.route("/api/v/fn/<mode>", methods=['POST', 'GET'])
def order(mode):
	global verification
	global send_end
	if request.method == 'POST' and 'email' in request.form:
		if mode == "delete-msg":
			no = request.form["id"]
			try:
				while True:
					try:
						db = connector()
						break
					except:
						pass
				cur = db.cursor(buffered=True)
				cur.execute('INSERT INTO deleted (user, to_user, message) SELECT user, to_user, message FROM messages WHERE id=%s', (no, ))
				cur.execute('DELETE FROM messages WHERE id=%s', (no, ))
				msg = "message deleted"
			except:
				msg = "error during transaction"
				db.rollback()
				pass
			finally:
				db.commit()
				db.close()
			return msg
		if mode == "add-event":
			title = request.form["title"]
			describe = request.form["description"]
			date = request.form["date"]
			ttime = request.form["time"]
			msg = None
			try:
				while True:
					try:
						db = connector()
						break
					except:
						pass
				cur = db.cursor(buffered=True)
				cur.execute('INSERT INTO events (title, description, date, event_time) VALUES(%s, %s, %s, %s)', (title, describe, date, ttime, ))
				msg = "new event created"
			except:
				msg = "error during transaction"
				db.rollback()
				pass
			finally:
				db.commit()
				db.close()
			return msg
		if mode=="read":
			msg = None
			user = request.form["email"];
			no = request.form["id"]
			try:
				while True:
					try:
						db = connector()
						break
					except:
						pass
				cur = db.cursor(buffered=True)
				cur.execute('SELECT is_read FROM messages WHERE id=%s', (no, ))
				r = cur.fetchone()
				if r[0] != 1:
					cur.execute('UPDATE messages SET is_read=1 WHERE id=%s', (no, ))
				msg = "read"
			except Exception as e:
				msg = "Error occured during transaction"
				print(str(e))
				db.rollback()
				pass
			finally:
				db.commit()
				db.close()
			return msg
		if mode=="readall":
			msg = None
			user = request.form["email"];
			try:
				while True:
					try:
						db = connector()
						break
					except:
						pass
				cur = db.cursor(buffered=True)
				cur.execute('SELECT id FROM notifications WHERE is_read is NULL or is_read=0')
				res = cur.fetchall()
				for r in res:
					cur.execute('UPDATE notifications SET is_read=1 WHERE id=%s', (r))
				msg = "All notifications read"
				
			except Exception as e:
				msg = "Error occured during transaction"
				print(str(e))
				db.rollback()
				pass
			finally:
				db.commit()
				db.close()
			return msg
		if mode == "delete":
			msg = None
			user = request.form["id"]
			try:
				while True:
					try:
						db = connector()
						break
					except:
						pass
				cur = db.cursor(buffered=True)
				cur.execute('SELECT * FROM visitors WHERE id =%s', (user, ))
				res = cur.fetchall()
				print(res)
				if res:
					cur.execute('UPDATE visitors SET is_blocked=1 WHERE id=%s', (user, ))
					msg = "user is blocked"
				else:
					msg = "User not found"
			except Exception as e:
				msg = "Error occured during transaction"
				print(str(e))
				db.rollback()
				pass
			finally:
				db.commit()
				db.close()
			return msg
		if mode == "unblock":
			msg = None
			user = request.form["id"]
			try:
				while True:
					try:
						db = connector()
						break
					except:
						pass
				cur = db.cursor(buffered=True)
				cur.execute('SELECT * FROM visitors WHERE id =%s', (user, ))
				res = cur.fetchall()
				if res:
					cur.execute('UPDATE visitors SET is_blocked=0 WHERE id=%s', (user, ))
					msg = "user is unblocked"
				else:
					msg = "User not found"
			except Exception as e:
				msg = "Error occured during transaction"
				print(str(e))
				db.rollback()
				pass
			finally:
				db.commit()
				db.close()
			return msg
		if mode == "order":
			user = request.form["email"]
			title = request.form["title"]
			des = request.form["description"]
			msg = None
			date = str(datetime.datetime.now())
			try:
				while True:
					try:
						db = connector()
						break
					except:
						pass
				cur = db.cursor(buffered=True)
				cur.execute('INSERT INTO orders (user, title, description) VALUES(%s, %s, %s)', (user, title, des, ))
				msg = "order placed successfully"
			except:
				msg = "error during transaction"
				db.rollback()
				pass
			finally:
				db.commit()
				db.close()
			return msg
		if mode == "review":
			user = request.form["email"]
			des = request.form["review"]
			msg = None
			s = str(datetime.datetime.now())
			s = s.split(" ")
			date = s[0]
			try:
				while True:
					try:
						db = connector()
						break
					except:
						pass
				cur = db.cursor(buffered=True)
				cur.execute('INSERT INTO reviews (user, review, time) VALUES(%s, %s, %s)', (user, des, date, ))
				msg = "Review submitted"
				notification(user+" submitted a review")
			except:
				msg = "error during transaction"
				db.rollback()
				pass
			finally:
				db.commit()
				db.close()
			return msg
		if mode == 'reply':
			msg = None
			msgno = request.form["id"]
			reply = request.form["reply"]
			try:
				while True:
					try:
						db = connector()
						break
					except:
						pass
				cur = db.cursor(buffered=True)
				cur.execute("SELECT user FROM messages WHERE id =%s or user=%s", (str(msgno), str(msgno), ))
				user = cur.fetchone()
				if user:
					user = user[0];
					print(user)
					cur.execute('INSERT INTO messages (user, to_user, message) VALUES(%s, %s, %s)', (user, 'user', reply, ))
					msg = "response sent"
				else:
					msg = "response not sent"
			except Exception as e:
				print(str(e))
				msg = "error during transaction"
				db.rollback()
				pass
			finally:
				db.commit()
				db.close()
			return msg
		if mode == 'new_message':
			msg = None
			message = request.form["msg"]
			try:
				while True:
					try:
						db = connector()
						break
					except:
						pass
				cur = db.cursor(buffered=True)
				cur.execute('INSERT INTO messages (user, to_user, message) VALUES(%s, %s, %s)', ('admin@blogspot.com', 'users', message, ))
				msg = "message sent"
			except Exception as e:
				print(str(e))
				msg = "message not sent"
				db.rollback()
				pass
			finally:
				db.commit()
				db.close()
			return msg
		
		if mode == "upload":
			fp = request.files["upload"]
			print(fp)
			code = fp.read()
			return code
	
	if mode == "reviews":
			try:
				while True:
					try:
						db = connector()
						break
					except:
						pass
				cur = db.cursor(buffered=True)
				cur.execute('SELECT * FROM reviews ORDER BY time DESC')
				reviews = cur.fetchall()
				msg = "Review submitted"
			except:
				msg = "error during transaction"
				db.rollback()
				pass
			finally:
				db.close()
			return render_template("reviews.html", n=len(reviews), reviews=reviews)
	if mode == "get_code":
		if session.get("loggedin") != None and session.get("loggedin") == "blogger":
			msg = "Transaction not complete"
			verificationcode = random.randint(1000, 9999)
			try:
				while True:
					try:
						db = connector()
						break
					except:
						pass
				cur = db.cursor(buffered=True)
				cur.execute('UPDATE bloggers SET verification=%s WHERE email_id=%s or user=%s', (str(verificationcode), session["user"], session["user"], ))
				msg = "success"
				x = alert("your login code is "+str(verificationcode))
			except:
				msg = "error during transaction"
				db.rollback()
				pass
			finally:
				db.commit()
				db.close()
		#print(verification)
		return msg
	if mode == "new-msgs":
		getmessages()
		contacts = send_end["messages"][0]
		return render_template("contact-messages.html", contacts=contacts)
	if mode == "dash-msgs":
		getmessages()
		messages = send_end["messages"][0]
		return render_template("dashboard-messages.html", messages = messages)
	if mode == "events":
		try:
			while True:
				try:
					db = connector()
					break
				except:
					pass
			cur = db.cursor(buffered=True)
			cur.execute('SELECT * FROM events WHERE is_completed=0 ORDER BY TIME ASC')
			events = cur.fetchall()
		except Exception as e:
			db.rollback()
			print(str(e))
			pass
		finally:
			db.close()
		return render_template("loadevents.html", events=events)
@app.route("/api/v/chat/<no>", methods=['GET'])
def fetchmessages(no):
	messages = []
	if no:
		try:
			while True:
				try:
					db = connector()
					break
				except:
					pass
			cur = db.cursor(buffered=True)
			cur.execute('SELECT * FROM messages WHERE id=%s or user=%s ORDER BY TIME ASC', (no, no, ))
			messages = cur.fetchall()
		except Exception as e:
			db.rollback()
			print(str(e))
			pass
		finally:
			db.close()
		return render_template("messages.html", messages=messages, n=len(messages))
@app.route("/api/v/admin", methods=['GET', 'POST'])
def admin_role():
	global verification
	print(session.get("admin-logged"))
	if session.get("loggedin") == "blogger":
		if request.method == 'POST':
			msg = None
			verifcode = request.form["code"]
			
			try:
				while True:
					try:
						db = connector()
						break
					except:
						pass
				cur = db.cursor(buffered=True)

				cur.execute('SELECT * FROM bloggers WHERE email_id=%s or user=%s and verification=%s', (session["user"], session["user"], verifcode, ))
				exists = cur.fetchone()
				if exists:
					msg = "success"
					session['admin-logged'] = True
					return msg
				else:
					return "Code not valid"
			except Exception as e:
				db.rollback()
				print(str(e))
				pass
			finally:
				db.close()
			return msg
		else:	
			return render_template("admin.html", **locals())
	else:
		return redirect("/api/fx/signin")
def run_parallel(*functions):
    '''
    Run functions in parallel
    '''
    global send_end
    from multiprocessing import Process
    import time
    pipe_list = []
    processes = []
    start = time.perf_counter()
    for function in functions:
        function()
    end = time.perf_counter()
    #result_list = [x.recv() for x in pipe_list]

@app.route("/api/v/blogger/templates", methods=['GET'])
def dashboard_templates():
	if session.get("admin-logged") is None or session.get("admin-logged") == False:
			return redirect("/api/v/admin")
	getmessages()
	all_messages = send_end["messages"]
	messages = all_messages[0]
	your_messages = all_messages[1]
	notifications = all_messages[2]
	path = '/home/korg'
	stat = []#shutil.disk_usage(path)
	cpu_percent = psutil.cpu_percent(4)
	mem_percent = psutil.virtual_memory()[2]
	disk_percent = 90
	return render_template("dashboard-templates.html", **locals())
    
@app.route("/api/v/<mode>", methods=['POST', 'GET'])
def dashboard(mode):
	
	try:
		if session.get("admin-logged") is None or session.get("admin-logged") == False:
				return redirect("/api/v/admin")
		global send_end	
		run_parallel(visitors, order, donation, getmessages)
		visits = send_end["visitors"]
		orders = send_end["orders"]
		don = send_end["donations"]
		all_messages = send_end["messages"]
		no_users = visits[0]
		user_progress = visits[1]
		new_visits = visits[3]
		all_visits = visits[2]
		visits_progress = user_progress
		order_progress = orders[1]
		no_orders = orders[0]
		donations = don[1]
		donations_today = don[0]
		messages = all_messages[0]
		your_messages = all_messages[1]
		notifications = all_messages[2]
		contacts = all_messages[0]
		deleted_messages = all_messages[4]
		date_time = date.today()
		tday = datetime.date.today()
		daytoday = tday.ctime()
		#perfomance = h.heap()
		path = '/home/korg'
		stat =[40,70] #shutil.disk_usage(path)
		cpu_count = os.cpu_count()
		perfomance = []
		perfomance.append("The Server CPU count is : "+str(cpu_count))
		perfomance.append("Cpu Usage is : "+str(psutil.cpu_percent(4))+" <i>(measured within four seconds using psutil cpu percent)</i>")
		load1, load5, load15 = psutil.getloadavg()
		total_memory, used_memory, free_memory = map(int, os.popen('free -t -m').readlines()[-1].split()[1:])
		cpu_usage = (load15/os.cpu_count()) * 100
		perfomance.append("Cpu Usage is : "+str(cpu_usage)+" <i>(measured using os loadavg info tool)</i>")
		mem_perfomance = []
		mem_perfomance.append('RAM memory % used is : '+str(psutil.virtual_memory()[2])+" <i>(measured using psutil module)</i>")
		mem_perfomance.append('RAM memory % used is : '+str(round((used_memory/total_memory) * 100, 2))+" <i>(measured using the os module)</i>")
		mem_perfomance.append('RAM Used in (GB) : '+str(psutil.virtual_memory()[3]/1000000000))
		
		cpu_percent = psutil.cpu_percent(4)
		mem_percent = psutil.virtual_memory()[2]
		disk_percent = 100 - (stat[1]/1000000000)/(stat[0]/1000000000)*100 
		disk_perfomance = []
		disk_perfomance.append("Disk Usage ("+path+") in GB <br><p> total size : "+str(stat[0]/1000000000)+"</p><p> Used size : "+str(stat[1]/1000000000)+" </p><p> Free size : "+str(stat[2]/1000000000)+"</p><br>")
		disk_used = "<p>Disk size used: "+str(stat[1]/1000000000)+" GB </p>"
		articles = [" Message From Bradone", "Success is key"]
		day1_visits = visits[4]
		day2_visits = visits[5]
		day3_visits = visits[6]
		first = len(day1_visits)
		second =  len(day2_visits)
		third = len(day3_visits)
		if third == 0:
			third = 1
		if second == 0:
			second = 1
		if first == 0:
			first = 1
		user_progress = (first*100)/second 
		data = [["Days", "Visits Perfomance"],['Today', first],['Yesterday', second],['Last 3 days', third]]
		data_one = [["Days", "Order Perfomance"],['Today', first],['Yesterday', second],['Last 3 days', third]]
		data_two = [["Disk", "Disk Perfomance"],['Total size', stat[0]/1000000000],['Used size', stat[1]/1000000000],['Free size', stat[2]/1000000000]]
		data_three = [["Days", "Device usage"],['Desktop', 30],['Mobile', 22]]
		if mode:
			if mode == "new-message":
				return render_template("new-message.html", **locals())
			if mode == "dashboard":
				return render_template("dashboard.html", **locals())
			if mode == "all-messages":
				return render_template("all_messages.html", **locals())
			if mode == "perfomance":
				return render_template("perfomance.html", **locals())
			if mode == "new-blog":
				return render_template("new.html", **locals())
			if mode == "blogs":
				return render_template("new.html", **locals())
			if mode == "orders":
				return render_template("orders.html", **locals())
			if mode == "visits":
				
				return render_template("visits.html", **locals())
			if mode == "notifications":
				all_notifications = all_messages[3]
				return render_template("notifications.html", **locals())
	except IndexError:
		abort(404)
		

@app.route("/api/fx/signup", methods=['GET', 'POST'])
def signup():
	msg = None
	if request.method == 'POST':
		if 'joinus' in request.form:
			username = request.form["username"]
			email = request.form["email"]
			password = request.form["password"]
			mode = request.form["joinus"]
			key = Fernet.generate_key()
			if mode == "user":
				try:
					while True:
						try:
							db = connector()
							break
						except:
							pass
					cur = db.cursor(buffered=True)
					cur.execute("SELECT * FROM users WHERE key_ID=%s", (key, ))
					keys = cur.fetchone()
					if keys:
						msg = "An error occured on our side, try again"
						return render_template("signup.html", **locals())
					cur.execute('SELECT * FROM users WHERE email_id=%s ', (email, ))
					exists = cur.fetchone()
					if exists:
						msg = "Username not available"
						return render_template("signup.html", **locals())
					cur.execute('SELECT * FROM users WHERE name=%s', (username, ))
					existss = cur.fetchone()
					if existss:
						msg = "Email account already exists"
						return render_template("signup.html", **locals())
					cur.execute('INSERT INTO users (key_ID, email_id, name) VALUES(%s, %s, %s)', (key, email, username,))
					cur.execute('INSERT INTO rooms (email_id, name, dkey) VALUES(%s, %s, %s)', (email, username, key, ))
					msg = "success"
				except Exception as e:
					print(str(e))
					msg = "An error occured on our side, try again"
					db.rollback()
					pass
				finally:
					db.commit()
					db.close()
			elif mode == "blogger":
				pass
			else:
				msg = "An error occured on our side, try again"	
			return render_template("signup.html", **locals())
		else:
			msg = "Fill out all required fileds"
	return render_template("signup.html", **locals())
@app.route("/api/fx/signin", methods=['GET', 'POST'])
def signin():
	returnurl = None
	call_back = request.args.get("callback_url")
	if call_back != None:
		returnurl = call_back
	msg = None
	if request.method == 'POST' and 'username' in request.form:
		if 'username' in request.form:
			username = request.form['username']
			try:
				while True:
					try:
						db = connector()
						break
					except:
						pass
				cur = db.cursor(buffered=True)

				cur.execute('SELECT * FROM bloggers WHERE email_id=%s or user=%s', (username, username, ))
				exists = cur.fetchone()
				if exists:
					session["loggedin"] = "blogger"
					session["eid"] = exists[1]
					if exists[4] == "NULL":
						session["user"] = exists[2]
					else:
						session["user"] = exists[4]
					msg = "success"
					if call_back != None: return redirect(call_back)
					else:
						returnurl = "/api/v/admin"
					return redirect(returnurl)
				
				cur.execute('SELECT * FROM users WHERE email_id=%s or name=%s', (username, username, ))
				existss = cur.fetchone()
				if existss:
					session["loggedin"] = "user"
					session["user"] = existss[2]
					session["eid"] = existss[1]
					msg = "success"
					if call_back != None: return redirect(call_back)
					else:
						returnurl = "/test"
					return redirect(returnurl)
				else:
					msg = "Invalid Username or Password"
					return render_template("signin.html", **locals())
			except Exception as e:
				msg = "An error occured during the transaction"
				db.rollback()
				print(str(e))
				pass
			finally:
				db.close()
		else:		
			msg = "fill all required fields"
			return render_template("signin.html", **locals())
	
	return render_template("signin.html", **locals())
@app.route("/api/ex/signout", methods=['GET'])
def signout():
	session.clear()
	returnurl = ""
	call_back = request.args.get("callback_url")
	if call_back != None:
		returnurl = call_back
	return redirect("/api/fx/signin?callback_url="+returnurl)

@app.route("/api/fx/templates", methods=['GET'])
def get_templates():
	if session.get("loggedin") == None:
		return redirect("/api/fx/signin?callback_url=/api/fx/templates")
	if session.get("loggedin") == "blogger":
		user = session["user"]
		print(user)
		if request.method == 'GET':
			preview = request.args.get("preview")
			
			if preview != None:
				return redirect("/"+str(session["user"]))
			try:
				cart = [0]
				while True:
					try:
						db = connector()
						break
					except:
						pass
				cur = db.cursor(buffered=True)
				cur.execute('SELECT * FROM templates')
				templates = cur.fetchall()
				cur.execute('SELECT * FROM cart_template WHERE user=%s and completed=0', (user, ))
				carts = cur.fetchall()
				cart[0] = len(carts)
			except Exception as e:
				print(str(e))
				pass
			finally:
				db.close()
			return render_template("get-portfolio.html", **locals())
@app.route("/api/fx/templates/<mode>", methods=['GET', 'POST'])
def templates(mode):
	if session.get("loggedin") == None:
		return redirect("/api/fx/signin?callback_url=/api/fx/templates/"+mode)
	mssg = Vars.mssg
	p1 = Payements("paypal", 0)
	if mode == "add":
		msg = None
		if request.method == 'POST' and 'template' in request.form:
			template = request.form["template"]
			try:
				while True:
					try:
						db = connector()
						break
					except:
						pass
				cur = db.cursor(buffered=True)
				cur.execute('SELECT price FROM templates WHERE template_id=%s', (template, ))
				price = cur.fetchone()
				cur.execute('SELECT * FROM cart_template WHERE user=%s and template_id=%s', (session["user"], template, ))
				avail = cur.fetchall()
				if avail:

					return "available"
				cur.execute('INSERT INTO cart_template(user, template_id, price) VALUES(%s, %s, %s)', (session["user"], template, price[0], ))
				msg = "success"
			except Exception as e:
				db.rollback()
				msg = "error during transaction"
				print(str(e))
				pass	
			finally:
				db.commit()
				db.close()
		
		return str(msg)
	if mode == "remove":
		msg = None
		if request.method == 'POST' and 'template' in request.form:
			template = request.form["template"]
			try:
				while True:
					try:
						db = connector()
						break
					except:
						pass
				cur = db.cursor(buffered=True)
				cur.execute('SELECT * FROM cart_template WHERE user=%s and template_id=%s', (session["user"], template, ))
				price = cur.fetchall()
				if price:
					cur.execute('DELETE FROM cart_template WHERE user=%s and template_id=%s', (session["user"], template, ))
					msg = "success"
			except Exception as e:
				db.rollback()
				msg = "error during transaction"
				print(str(e))
				pass	
			finally:
				db.commit()
				db.close()
		
		return str(msg)
	if mode == "checkout-cart":
		print(p1.paytype)
		if request.method=='POST' and 'cardnumber' in request.form:
			p1.paytype = "Card Payement";
			try:
				while True:
					try:
						db = connector()
						break
					except:
						pass
				cur = db.cursor(buffered=True)

				cur.execute('SELECT * FROM cart_template WHERE user=%s and completed is NULL or completed=0', (session["user"], ))
				items = cur.fetchall()
				it = ""
				for item in items:
					it = it+str(item[2])+", "
				cardnumber = request.form["cardnumber"]
				try:
					cardnumber.replace(" ", "")
				except:
					pass
				cardname = request.form["cardholder"]
				cardname = cardname.split(" ")
				carddate = request.form["date"]
				carddate = str(carddate)
				total = request.form["totalprice"]
				if "/" in carddate:
					carddate = carddate.replace("/", "-")
				cardcvv = request.form["cvv"]
				cardaddress = request.form["address"]
				cardcity = request.form["city"]
				cardcode = request.form["code"]
				user = request.form["user"]
				print(float(total))
				inv = user+"@BlogSpot"
				p1.amount=float(total)
				if user != "" and user != None:
					x = charge(email=user, amount = float(total), name=cardname, card_number=cardnumber, carddate = carddate, cvv = cardcvv, postal = cardcode, city = cardcity, description="Template Purchase for items "+str(it), items=it, address=cardaddress, invoice=inv)
					
					if x.is_success:
						mssg[0] = True
						mssg.append(x.messages)
						purchase(items)
						return "success"
					else:
						mssg.append(x.messages)
			except Exception as e:
				print(str(e))
				pass
			if mssg[0] == None:
				return "fail"	
	if mode == "checkout":
		f = open("countries.txt", "r")
		countries = f.readlines()
		f.close()
		msg = None
		success = request.args.get("success")
		if success != None:
			return render_template("success-payement.html", **locals())
		loading = request.args.get("loading")
		if loading != None:
			return render_template("loading.html")
		fail = request.args.get("fail")
		if fail != None:
			return render_template("error-payement.html", **locals())
		if request.method == 'POST':
			if 'email' in request.form:
				email = request.form["email"]
				amount = request.form["amount"]
				url = request.form["url"]
				if email != "" and amount != "":
					x = Pay(email, amount,  "Template Purchase", url)
					print(x)
					p1.paytype = "Paypal Payement";p1.amount=float(amount)
					amt = float(amount)
					return x
				else:
					return "error during transaction"
			
		orders = None
		cart = [0]
		try:
			while True:
				try:
					db = connector()
					break
				except:
					pass
			cur = db.cursor(buffered=True)

			cur.execute('SELECT * FROM cart_template WHERE user=%s and completed is NULL or completed=0', (session["user"], ))
			orders = cur.fetchall()
			cart[0] = len(orders)
		except Exception as e:
			db.rollback()
			print(str(e))
			pass	
		finally:
			db.close()
		return render_template("cart.html", **locals())

def purchase(items):
	if session.get("loggedin") == "blogger":
		user = session["user"]
		
		try:
			while True:
				try:
					db = connector()
					break
				except:
					pass
			cur = db.cursor(buffered=True)
			for item in items:
				cur.execute("SELECT * FROM bloggers WHERE user=%s or email_id=%s")
				found =cur.fetchone()
				if found:
					cur.execute("UPDATE cart_template SET completed=%s WHERE id=%s", (1, item[0], ))
					cur.execute('INSERT INTO completed_orders(key_ID, email_id, user, template_id, price)', (found[0], found[1], item[1], item[2],items[3], ))
		except Exception as e:
			print(str(e))
			pass

def setOnline(newCookies):
	if session.get("loggedin") != None and session.get("user") != None:
		if newCookies == True:
			user = session["user"]
			try:
				while True:
					try:
						db = connector()
						break
					except:
						pass
				cur = db.cursor(buffered=True)
				if session["loggedin"] == "blogger":
					cur.execute('UPDATE bloggers SET time=CURRENT_TIMESTAMP WHERE email_id=%s and blogname=%s or user=%s', (session["eid"], user, user, ))
				if session["loggedin"] == "user":
					cur.execute('update users set last_online=CURRENT_TIMESTAMP where email_id=%s and name=%s', (session["eid"], user, ))
			except Exception as e:
				print(str(e))
				pass
			finally:
				db.commit()
				db.close()

@app.route("/api/fx/request/<mode>", methods=['POST', 'GET'])
def api_request(mode):
	newCookies = CK()
	if session.get("loggedin") != None:
		newCookies.setCookie("loggedin", True)
	if mode == "setonline":
		if request.method == 'POST' and 'email' in request.form:
			if session.get("eid") == request.form["email"]:
				print("setting user online...")
				newCookies.setCookie("loggedin", True)
				setOnline(newCookies.getCookie("loggedin"))
			return "success"
	if mode == "upload":
		import time
		if request.method == 'POST':
			time.sleep(20)
			return "success"
	if mode=="textbox":
		if session.get("rooms-user") != None:
			return render_template("textbox.html")
	if mode == "create-room":
		pass
	if mode == "join-room":
		if request.method == 'POST' and 'email' in request.form:
			msg = "error during transaction"
			email = request.form["email"]
			if email == "":
				return "Email input required"
			key = Fernet.generate_key()
			verificationcode = random.randint(100000, 999999)
			code = verificationcode
			try:
				while True:
					try:
						db = connector()
						break
					except:
						pass
				cur = db.cursor(buffered=True)

				cur.execute('SELECT * FROM users WHERE email_id=%s or name=%s', (email, ))
				exists = cur.fetchone()
				if exists:
					cur.execute('UPDATE rooms SET verification=%s WHERE email_id=%s or name=%s and dkey=%s', (str(code), email, exists[4]))
				else:
					cur.execute('INSERT INTO users (key_ID, email_id, name) VALUES(%s, %s, %s)', (key, email, email, ))
					cur.execute('INSERT INTO rooms (email_id, verification, dkey) VALUES(%s, %s, %s)', (email, str(code), key, ))
				
			except Exception as e:
				db.rollback()
				print(str(e))
				pass	
			finally:
				db.commit()
				db.close()
			try:
				while True:
					try:
						db = connector()
						break
					except:
						pass
				cur = db.cursor(buffered=True)

				cur.execute('SELECT verification FROM rooms WHERE email_id=%s and dkey=%s', (email, key, ))
				code = cur.fetchone()
				if code:
					msg = mail(email, str(code[0]))
			except Exception as e:
				db.rollback()
				print(str(e))
				pass
			finally:
				db.close()
			return msg
	if mode == "validate":
		if request.method == 'POST' and 'email' in request.form and 'code' in request.form:
			email = request.form["email"]
			code = request.form["code"]
			if email == "" or code == "":
				return "Invalid values"
			try:
				while True:
					try:
						db = connector()
						break
					except:
						pass
				cur = db.cursor(buffered=True)

				cur.execute('SELECT * FROM rooms WHERE email_id=%s and verification=%s', (email, code, ))
				exists = cur.fetchone()
				if exists:
					session["loggedin"] = "user"
					session["rooms-user"] = email
					session["room-name"] = exists[3]
					return "success"
				else:
					return "Code not valid"
			except Exception as e:
				db.rollback()
				print(str(e))
				pass
			finally:
				db.close()
	if mode == "search":
		last_online = datetime.datetime.now() - timedelta(minutes=2)
		if session.get("rooms-user") != None:
			user = request.args.get("user")
			group = request.args.get("group")
			if user != None:
				try:
					while True:
						try:
							db = connector()
							break
						except:
							pass
					cur = db.cursor(buffered=True)

					cur.execute('SELECT * FROM users WHERE email_id LIKE %s or name LIKE %s', (user, user, ))
					users = cur.fetchall()
				except Exception as e:
					db.rollback()
					print(str(e))
					pass
				finally:
					db.close()
				return render_template("userquery.html", users=users, n = len(users), last_online=last_online)
			if group != None:
				try:
					while True:
						try:
							db = connector()
							break
						except:
							pass
					cur = db.cursor(buffered=True)

					cur.execute('SELECT * FROM group_rooms WHERE email_id LIKE %s or name LIKE %s or title LIKE %s or description LIKE %s', (group, group, group, group,  ))
					groups = cur.fetchall()
					
				except Exception as e:
					db.rollback()
					print(str(e))
					pass
				finally:
					db.close()
				return render_template("groupquery.html", groups = groups, n = len(groups))
	if mode == "loadroom":
		if session.get("room-name") != None and session.get("room-name") != "NULL":
			user = request.args.get("active")
			if user != None:
				from_user = session["room-name"]
				messages = []
				if user != None:
					try:
						while True:
							try:
								db = connector()
								break
							except:
								pass
						cur = db.cursor(buffered=True)
						cur.execute('SELECT * FROM users WHERE email_id=%s or name=%s', (from_user, from_user, ))
						eid = cur.fetchone()
						if eid:
							cur.execute('SELECT * FROM users WHERE email_id=%s or name=%s', (user, user, ))
							eiid = cur.fetchone()
							if eiid:
								cur.execute('SELECT * FROM room_messages WHERE id=%s and reciever_id=%s or id=%s and reciever_id=%s', (eid[0], eiid[0], eiid[0], eid[0], ))
								messages = cur.fetchall()
						n = len(messages)
					except Exception as e:
						db.rollback()
						print(str(e))
						pass
					finally:
						db.close()
			return render_template("room-messages.html", Fernet=Fernet, **locals())
	if mode == "loadmessages":
		last_online = datetime.datetime.now() - timedelta(minutes=2)
		if session.get("room-name") != None and session.get("room-name") != "NULL" and session.get("rooms-user") != None:
			user = session["room-name"]
			if user != None:
				messages = []
				if user != None:
					try:
						while True:
							try:
								db = connector()
								break
							except:
								pass
						cur = db.cursor(buffered=True)
						cur.execute('SELECT * FROM users WHERE email_id=%s or name=%s', (user, user, ))
						eid = cur.fetchone()
						if eid:
							cur.execute('SELECT * FROM room_messages WHERE id=%s or reciever_id=%s ORDER BY time DESC', (eid[0], eid[0], ))
							messages = cur.fetchall()
						n = len(messages)
					except Exception as e:
						db.rollback()
						print(str(e))
						pass
					finally:
						db.close()
			return render_template("load-messages.html", Fernet=Fernet, **locals())
	if mode == "sendmessage":
		if session.get('rooms-user') == None:
			return redirect("/api/fx/rooms")
		if session.get('room-name') != None or session.get('room-name') != "NULL":
			msg = "Anauthorised Request - 404 -"
			if request.method == 'POST' and 'to' in request.form and 'msg' in request.form:
				reciever = None
				msg = "transaction not complete"
				key = Fernet.generate_key()
				fernet = Fernet(key)
				user = session["room-name"]
				message = request.form['msg']
				to_user = request.form["to"]
				encMessage = fernet.encrypt(message.encode())
				try:
					while True:
						try:
							db = connector()
							break
						except:
							pass
					cur = db.cursor(buffered=True)
					cur.execute('SELECT * FROM users WHERE email_id=%s or name=%s', (to_user, to_user, ))
					users = cur.fetchone()
					if users:
						cur.execute('SELECT * FROM users WHERE email_id=%s or name=%s', (user, user, ))
						userss = cur.fetchone()
						if userss:
							cur.execute('INSERT INTO room_messages (id, from_user, to_user, message, dkey, reciever_id) VALUES(%s, %s, %s, %s, %s, %s)', (userss[0], user, to_user, encMessage, key, users[0], ))	
							msg = "success"
						else:
							msg = "The user "+str(user)+" has not registered in rooms"
					else:
						msg = "The user "+str(to_user)+" has not registered in rooms"		
									
				except Exception as e:
					msg = "An Error occured during the transaction"
					db.rollback()
					print(str(e))
					pass
				finally:
					db.commit()
					db.close()
			else:
				msg = "Anauthorised Request - 404 -"
			if msg == "success" and reciever != None:
				
				try:
					notify(reciever, session["room-name"], message, request.host)
				except Exception as e:
					print(str(e))
					pass
		return msg
	if mode == "loadgroup":
		if session.get("room-name") != None and session.get("room-name") != "NULL":
			user = request.args.get("active")
			if user != None and user != "":
				messages = []
				if user != None:
					try:
						while True:
							try:
								db = connector()
								break
							except:
								pass
						cur = db.cursor(buffered=True)
						cur.execute('SELECT * FROM group_rooms WHERE email_id=%s or name=%s', (user, user, ))
						eid = cur.fetchone()
						if eid:
							cur.execute('SELECT * FROM group_messages WHERE id=%s', (eid[0], ))
							messages = cur.fetchall()
						else:
							messages.append("error")
						n = len(messages)
					except Exception as e:
						db.rollback()
						print(str(e))
						pass
					finally:
						db.close()
			return render_template("group-messages.html", Fernet=Fernet, **locals())
	if mode == "loadgroups":
		if session.get("room-name") != None and session.get("room-name") != "NULL":
			user = session["room-name"]
			data = {}
			if user != None:
				messages = []
				if user != None:
					try:
						while True:
							try:
								db = connector()
								break
							except:
								pass
						cur = db.cursor(buffered=True)
						cur.execute('SELECT * FROM group_messages WHERE id=%s or name=%s', (user, user, ))
						messages = cur.fetchall()
						count = 0
						if messages:
							for message in messages:
								count = count + 1
								cur.execute('SELECT COUNT(id) FROM group_messages WHERE id=%s', (message[0], ))
								cn = cur.fetchone()[0]
								print(cn);print(message[0])
								cur.execute("select * from group_rooms where email_id=%s", (message[0], ))
								groups = cur.fetchall()
								for g in groups:
									arr = {count: [g[1], g[4], g[5], g[2], cn]}
									data.update(arr)
					except Exception as e:
						db.rollback()
						print(str(e))
						pass
					finally:
						db.close()
				n = len(messages)
			return render_template("loadgroups.html", **locals())
	if mode == "sendgroupmessage":
		if session.get('rooms-user') == None:
			return redirect("/api/fx/rooms")
		if session.get('room-name') != None or session.get('room-name') != "NULL":
			msg = "Anauthorised Request - 404 -"
			if request.method == 'POST' and 'to' in request.form and 'msg' in request.form:
				msg = "transaction not complete"
				to_group = request.form["to"]
				message = request.form["msg"]
				name = session["room-name"]
				key = Fernet.generate_key()
				fernet = Fernet(key)	
				encMessage = fernet.encrypt(message.encode())	
				try:
					while True:
						try:
							db = connector()
							break
						except:
							pass
					cur = db.cursor(buffered=True)
					cur.execute('SELECT email_id FROM group_rooms WHERE email_id LIKE %s or name LIKE %s', (to_group, to_group, ))
					reciever = cur.fetchone()
					if reciever:
						cur.execute('INSERT INTO group_messages (id, message, dkey, name) VALUES(%s, %s, %s, %s)', (reciever[0], encMessage, key, name, ))	
						msg = "success"
					else:
						msg = "Erro! The group "+str(to_group)+" has not registered in rooms"				
				except Exception as e:
					msg = "An Error occured during the transaction"
					db.rollback()
					print(str(e))
					pass
				finally:
					db.commit()
					db.close()	
		return msg
	if mode == "setname":
		if session.get('rooms-user') == None:
			return redirect("/api/fx/rooms")
		if request.method == 'POST' and 'name' in request.form:
			name = request.form["name"]
			email = session["rooms-user"]
			msg = "Transaction not completed"
			try:
				while True:
					try:
						db = connector()
						break
					except:
						pass
				cur = db.cursor(buffered=True)
				cur.execute('SELECT * FROM rooms WHERE name=%s', (name, ))
				exs = cur.fetchone()
				if exs:
					msg = "username not available"
				else:
					cur.execute('SELECT * FROM rooms WHERE email_id=%s', (email, ))
					exs = cur.fetchone()
					if exs:
						cur.execute('UPDATE rooms SET name=%s WHERE email_id=%s', (name, email, ))
						session["room-name"] = name
			except Exception as e:
				msg = "Error during transaction"
				db.rollback()
				print(str(e))
				pass
			finally:
				msg = "success"
				db.commit()
				db.close()
			return msg
	if mode == "shownotifications":
		if session.get('user') == None:
			return redirect("/api/fx/rooms")
		if session.get("loggedin") != None:
			try:
				while True:
					try:
						db = connector()
						break
					except:
						pass
				cur = db.cursor(buffered=True)
				cur.execute('SELECT * FROM users WHERE email_id=%s or name=%s', (session["user"], session["user"], ))
				exists = cur.fetchone()
				if exists:
					cur.execute('SELECT * FROM notifications WHERE to_user=%s', (exists[0], ))
					notifications = cur.fetchall()
			except Exception as e:
				db.rollback()
				print(str(e))
				pass
			finally:
				db.close()
			return render_template("load-notifications.html", **locals())	
@app.route("/api/nx/rooms", methods=['GET', 'POST'])
def room():
	if session.get("loggedin") == None:
		group = request.args.get("b")
		if group != None:
			return redirect("/api/fx/signin?callback_url=/api/nx/rooms?b="+group+"");
		else:
			return redirect("/api/fx/signin?callback_url=/api/nx/rooms");
	if session["loggedin"] == "blogger":
		session["rooms-user"] = session["eid"]
		session["room-name"] = session["user"]
	if session["loggedin"] == "user":
		session["rooms-user"] = session["eid"]
		session["room-name"] = session["user"]
	
	return render_template("rooms.html")

@app.route("/api/nx/rooms/load", methods=['GET'])
def getChat():
	messages = [None]
	if session.get("rooms-user") != None:
		req = session["rooms-user"]
		try:
			while True:
				try:
					db = connector()
					break
				except:
					pass
			cur = db.cursor(buffered=True)
			cur.execute('SELECT * FROM messages WHERE user =%s', (req, ))
			messages = cur.fetchall()
		except Exception as e:
			db.rollback()
			print(str(e))
			pass
		finally:
			db.close()
	return render_template("chat-messages.html", Fernet=Fernet, **locals())

@app.route("/rooms")
def rooms():
	return redirect("api/nx/rooms/chat")

@app.route("/api/nx/rooms/chat", methods=['GET'])
def blogChat():
	messages = [None]
	if session.get("rooms-user") != None:
		return render_template("portfolio-chat.html", **locals())
@app.route("/nx/home", methods=['GET'])
def blogHome():
	mode = request.args.get("new_post")
	if mode != None:
		return render_template("new_post.html", **locals())
	return render_template("homelanding.html", **locals())

@app.route("/nx/blogs", methods=['GET'])
def allBlogs():
	return render_template("all-blogs.html", **locals())

@app.route("/api/nx/profile/<mode>", methods=['POST', 'GET'])
def profile(mode):	
	getmessages()
	if mode == "home" or mode == "my-profile":
		return render_template("profile.html", **locals())
	if mode == "mails":
		return render_template("mails.html", **locals())
	
@app.route("/test", methods=['GET'])
def test():
	if request.method=='GET':
		name = None
		try:
			while True:
				try:
					db = connector()
					break
				except:
					pass
			cur = db.cursor(buffered=True)
			cur.execute('SELECT name FROM group_rooms WHERE email_id=%s', ('omwitsabradone@gmail.com', ))
			exs = cur.fetchone()
			if exs:
				name = exs[0]
		except:
			db.rollback()
			pass
		finally:
			db.close()
		return render_template("templates/template_2.html", **locals())
def visitors():	
	#global send_end	
	today = date.today()
	yesterday = today - timedelta(days = 1)
	try:
		while True:
			try:
				db = connector()
				break
			except:
				pass
		cur = db.cursor(buffered=True)
		cur.execute('SELECT * FROM visitors ORDER BY time DESC')
		all_visitors = cur.fetchall()
		cur.execute('SELECT * FROM visitors WHERE DATE_SUB(CURDATE(),INTERVAL 1 DAY) <= time')
		visitors = cur.fetchall()
		cur.execute('SELECT * FROM visitors WHERE DATE_SUB(CURDATE(),INTERVAL 2 DAY) <= time')
		visitorsyesterday = cur.fetchall()
		cur.execute('SELECT * FROM visitors WHERE DATE_SUB(CURDATE(),INTERVAL 3 DAY) <= time')
		day3_visits = cur.fetchall()
		cur.execute('SELECT * FROM visitors where is_new=0')
		new_visits = cur.fetchall()
	except Exception as e:
		db.rollback()
		print(str(e))
		pass
	finally:
		db.close()
	v = len(visitors)
	y = len(visitorsyesterday)
	if y > 0:
		progress = (v/y)*100 - 100;
	else:
		progress = 0.0
	visits = {"visitors": []};
	send_end.update(visits)
	send_end["visitors"] += [v, progress, all_visitors, len(new_visits), visitors, visitorsyesterday, day3_visits]
	#return [v, progress, all_visitors, len(new_visits), visitors, visitorsyesterday, day3_visits]
def order():
	global send_end
	today = date.today()
	yesterday = today - timedelta(days = 1)
	try:
		while True:
			try:
				db = connector()
				break
			except:
				pass
		cur = db.cursor(buffered=True)
		cur.execute('SELECT * FROM orders')
		all_orders = cur.fetchall()
		cur.execute('SELECT * FROM orders WHERE DATE_SUB(CURDATE(),INTERVAL 1 DAY) <= time')
		orders = cur.fetchall()
		cur.execute('SELECT * FROM orders WHERE DATE_SUB(CURDATE(),INTERVAL 1 DAY) < time')
		ordersyesterday = cur.fetchall()
	except Exception as e:
		db.rollback()
		print(str(e))
		pass
	finally:
		db.close()
	v = len(orders)
	y = len(ordersyesterday)
	if y > 0:
		progress = (v/y)*100 - 100;
	else:
		progress = 0.0
	orderr = {"orders": []};
	send_end.update(orderr)
	send_end["orders"] += [v, progress, orders]
	#return [v, progress, orders]
def donation():	
	global send_end
	today = date.today()
	yesterday = today - timedelta(days = 1)
	try:
		while True:
			try:
				db = connector()
				break
			except:
				pass
		cur = db.cursor(buffered=True)
		cur.execute('SELECT amount FROM donations')
		all_donations = cur.fetchall()
		cur.execute('SELECT amount FROM donations WHERE DATE_SUB(CURDATE(),INTERVAL 1 DAY) <= time')
		donations = cur.fetchall()
	except Exception as e:
		db.rollback()
		print(str(e))
		pass
	finally:
		db.close()
	donation = 0
	donationtoday = 0
	if all_donations:
		for amount in all_donations:
			donation = donation + float(amount[0])
	if donations:
		for amount in donations:
			donationtoday = donationtoday + float(amount[0])
	order = {"donations": [donationtoday, donation]};
	send_end.update(order)
	return order
	#return [donationtoday, donation]
def getmessages():
	global send_end
	try:
		while True:
			try:
				db = connector()
				break
			except:
				pass
		cur = db.cursor(buffered=True)
		cur.execute('SELECT * FROM messages WHERE to_user="admin" ORDER BY time DESC')
		messages = cur.fetchall()
		cur.execute('SELECT * FROM messages WHERE to_user="user" ORDER BY time DESC')
		responses = cur.fetchall()
		cur.execute('SELECT * FROM notifications WHERE is_read is NULL or is_read=0 ORDER BY time DESC')
		notifications = cur.fetchall()
		cur.execute('SELECT * FROM notifications ORDER BY time DESC')
		all_notifications = cur.fetchall()
		cur.execute('SELECT * FROM deleted WHERE to_user="admin" ORDER BY time DESC')
		deleted_messages = cur.fetchall()
	except Exception as e:
		db.rollback()
		print(str(e))
		pass
	finally:
		db.close()
	order = {"messages": [messages, responses, notifications, all_notifications, deleted_messages]};
	send_end.update(order)
	return order
	#return [messages, responses, notifications]
app.run(host="0.0.0.0", debug=True)