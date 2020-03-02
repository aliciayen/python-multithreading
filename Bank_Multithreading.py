# Alicia Yen

from threading import Semaphore, Thread, Lock
from queue import Queue, Empty
from random import randint
from time import sleep

max_customers_in_bank = 10 # maximum number of customers that can be in the bank at one time
max_customers = 30 # number of customers that will go to the bank today
max_tellers = 3 # number of tellers working today
teller_timeout = 10 # longest time that a teller will wait for new customers

class Customer():
	def __init__(self, name):
		self.name = name

	def __str__(self):
		return f"'{self.name}'"

class Teller():
	def __init__(self, name):
		self.name = name

	def __str__(self):
		return f"'{self.name}'"

def bank_print(lock, msg):
	with lock:
		print(msg)

def wait_outside_bank(customer, guard, teller_line, printlock):
	bank_print(printlock, f"(C) {customer} waiting outside bank")
	guard.acquire()
	bank_print(printlock, f"<G> Security guard letting {customer} inside bank")
	bank_print(printlock, f"(C) {customer} getting into line")
	teller_line.put(customer)

def teller_job(teller, guard, teller_line, printlock):
	bank_print(printlock, f"[T] {teller} starting work")
	while True:
		try:
			c = teller_line.get(timeout=teller_timeout)
			bank_print(printlock, f"[T] {teller} is now helping {c}")
			sleep(randint(1,4))
			bank_print(printlock, f"[T] {teller} done helping {c}")
			bank_print(printlock, f"<G> Security guard is letting {c} out of the bank")
			guard.release()
		except Empty:
			bank_print(printlock, f"[T] Nobody is in line, {teller} going on break")
			break

if __name__ == "__main__":
	printlock = Lock()
	teller_line = Queue(maxsize=max_customers_in_bank)
	guard = Semaphore(max_customers_in_bank)
	bank_print(printlock, "<G> Security guard starting their shift")
	bank_print(printlock, "*B* Bank open")

	customer_jobs = []
	for i in range(1, max_customers+1):
		customer_name = 'Customer ' + str(i)
		customer = Customer(customer_name)
		c = Thread(target=wait_outside_bank, args=(customer, guard, teller_line, printlock))
		c.start()
		customer_jobs.append(c)
	sleep(5)

	bank_print(printlock, f"*B* Tellers starting work now")
	teller_jobs = []
	for i in range(1, max_tellers+1):
		teller_name = 'Teller ' + str(i)
		teller = Teller(teller_name)
		t = Thread(target=teller_job, args=(teller, guard, teller_line, printlock))
		t.start()
		teller_jobs.append(t)
	
	for cj in customer_jobs:
		cj.join()
	for tj in teller_jobs:
		tj.join()
	bank_print(printlock, f"*B* Bank closed")
