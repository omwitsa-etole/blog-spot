import sched, time
s = sched.scheduler(time.time, time.sleep)
def do_something(sc): 
    print("Doing stuff...")
    # do your stuff
    sc.enter(60, 1, do_something, (sc,))



s.enter(1, 1, do_something, (s,))
s.run()
while True:
	time.sleep(4)
	print("hoop hoop\nhooray\n")