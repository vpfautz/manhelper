import os
from os.path import join
import gzip
import subprocess


cli = "wget -i heise.de"
prog = cli.split(" ")[0]

p = subprocess.Popen(["man", "-w", prog], stdout=subprocess.PIPE)
manfile = p.stdout.read().strip()
print "manfile:",manfile

d = gzip.open(manfile, "rb").read()

def cleanup(key):
	key = key.replace("\\fB", "")
	key = key.replace("\\fR", "")
	key = key.replace("\\-", "-")
	key = key.replace("\\fI", "")
	key = key.replace("\\,", "")
	key = key.replace("\\/", "")
	key = key.replace("\"", "")
	if key.startswith(".BR "):
		key = key[4:]
	if key.startswith(".BI "):
		key = key[4:]
	if key.startswith(".B "):
		key = key[3:]
	return key

def is_key(keys):
	for k in keys:
		if k.startswith("-") and len(k) > 1:
			return True
	return False

class Color:
	RED     = '\033[91m'
	RED2    = '\033[1;91m'
	GREEN   = '\033[92m'
	GREEN2  = '\033[1;92m'
	YELLOW  = '\033[93m'
	YELLOW2 = '\033[1;93m'
	BLUE    = '\033[94m'
	BLUE2   = '\033[1;94m'
	PINK    = '\033[95m'
	PINK2   = '\033[1;95m'
	CYAN    = '\033[96m'
	CYAN2   = '\033[1;96m'
	GRAY    = '\033[1;30m'
	WHITE   = '\033[1;37m'

	BOLD      = '\033[1m'
	UNDERLINE = '\033[4m'

	ENDC   = '\033[0m'
	NORMAL = '\033[0m'

def clr(s, c):
	return "%s%s%s" % (c, s, Color.ENDC)

def check_descr_line(l):
	if not l.startswith("."):
		return True

	for b in ignore_intext:
		if l.startswith(b):
			return True

	return False

lines = d.split("\n")
i = 0
option_keywords = ["OPTIONS", "DESCRIPTION"]
scan_options = False
options = []

ignore_intext = [".B", ".IR", ".I ", ".RB", ".\\\"", ".nf", ".fi", ".br",
	".BR", ".ie", ". ", ".TS", ".el", ".na", ".TE", ".ad", ".IB"]

while i < len(lines):
	l = lines[i]
	if l.startswith(".SH"):
		print l
		scan_options = False
	if l.startswith(".SH ") and any(filter(lambda p: p in l, option_keywords)):
	# if l.startswith(".SH OPTIONS") or l.startswith(".SH DESCRIPTION"):
		scan_options = True
		i += 1
		continue
	if not scan_options:
		i += 1
		continue
	if l.startswith(".IP"):
		print l[:4]+clr(l[4:], Color.BLUE)
		keys = cleanup(l[4:]).split(", ")
		if not is_key(keys):
			i += 1
			continue

		descr = []
		i += 1
		while True:
			l = lines[i]
			if not check_descr_line(l):
				break

			print clr(lines[i], Color.GREEN)
			descr.append(lines[i])
			i += 1

		options.append((keys, descr))
	elif l.startswith(".TP"):
		print l
		keys = cleanup(lines[i+1]).split(", ")
		if not is_key(keys):
			i += 1
			continue
		print clr(lines[i+1], Color.BLUE)

		descr = []
		i += 2
		while True:
			l = lines[i]
			if not check_descr_line(l):
				break

			print clr(lines[i], Color.GREEN)
			descr.append(lines[i])
			i += 1

		options.append((keys, descr))
	else:
		print ">",l
		i += 1

# for keys,descr in options:
# 	print keys
	# print ""
	# print "keys:", keys
	# print "descr:"
	# print "> "+"\n> ".join(descr)
