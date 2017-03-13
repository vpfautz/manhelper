import os
from os.path import join
import gzip
import subprocess
import re
import sys
from collections import defaultdict
import string

"""
# cli = "wget -i heise.de"
# cli = "wget -O /dev/null http://cachefly.cachefly.net/100mb.test"
cli = "ag -i"
prog = cli.split(" ")[0]
params = cli.split(" ")[1:]
"""

prog = sys.argv[1]
params = sys.argv[2:]
print "cli: %s %s" % (prog, " ".join(params))


DEBUG = False
def debug(s):
	if DEBUG:
		print s

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

def get_indent(l):
	indent = re.search("^( *)", l).group(1)
	return len(indent)

def prev(i):
	i -= 1
	while len(lines[i].strip()) == 0:
		i -= 1
	return i


p = subprocess.Popen(["man", prog], stdout=subprocess.PIPE)
manfile = p.stdout.read().strip()

lines = manfile.split("\n")

# get cmd indention
count = defaultdict(int)
for l in lines:
	if not l.strip().startswith("-"):
		continue

	count[get_indent(l)] += 1

if len(count) == 0:
	print "no normal parameters"
	exit()

cmd_indention = max(count.items(), key=lambda (x,y):y)[0]
debug("cmd_indention: %s" % cmd_indention)

# get descr indention
count = defaultdict(int)
for i,l in enumerate(lines):
	if i==0:
		continue

	if not lines[prev(i)].strip().startswith("-"):
		continue

	count[get_indent(l)] += 1

descr_indention = max(count.items(), key=lambda (x,y):y)[0]
debug("descr_indention: %s" % descr_indention)

cmd_prefix = " "*cmd_indention+"-"

cmd_lines = set()
descr_lines = set()

debug("lines: %s" % len(lines))


for i,l in enumerate(lines):
	if l.startswith(cmd_prefix):
		k = i + 1
		while lines[k].startswith(cmd_prefix) or len(lines[k].strip()) == 0:
			k += 1
		if get_indent(lines[k]) == descr_indention:
			if descr_indention < len(l) and l[descr_indention] in string.ascii_letters and l[descr_indention-1] == " ":
				debug(clr(l[:descr_indention], Color.BLUE) + clr(l[descr_indention:], Color.GREEN))
				descr_lines.add(i)
			else:
				debug(clr(l, Color.BLUE))
			cmd_lines.add(i)
		else:
			debug(l)
	elif get_indent(l) == descr_indention:
		if prev(i) in cmd_lines or prev(i) in descr_lines:
			descr_lines.add(i)
			debug(clr(l, Color.GREEN))
		else:
			debug(l)
	elif get_indent(l) > descr_indention:
		if prev(i) in descr_lines:
			descr_lines.add(i)
			debug(clr(l, Color.GREEN))
		else:
			debug(l)
	else:
		debug(l)

def short_key(key):
	rem = re.findall("([ =].+$)|(<.+?>)|(\[.+?\])", key)
	for a,b,c in rem:
		key = key.replace(a, "")
		key = key.replace(b, "")
		key = key.replace(c, "")
	return key

class Option(object):
	def __init__(self, keys):
		super(Option, self).__init__()
		self.keys = []
		self.keys_short = []
		self.add_keys(keys)
		self.descr = []

	def parse_keys(self, keys):
		return map(lambda x:x.strip(), keys.split(", "))

	def has_descr(self):
		return len(self.descr) > 0

	def add_keys(self, keys):
		new = self.parse_keys(keys)
		self.keys += new
		for k in new:
			self.keys_short.append(short_key(k))

	def add_descr(self, d):
		self.descr.append(d)

	def __repr__(self):
		r = ""
		r += "keys:  %s\n" % self.keys
		r += "short: %s\n" % self.keys_short
		r += "descr: \n%s" % "\n".join(self.descr)
		return r

options = {}
curr_key = None

for i,l in enumerate(lines):
	if i in cmd_lines and not i in descr_lines:
		if curr_key is None or (not curr_key is None and options[curr_key].has_descr()):
			curr_key = l.strip()
			options[curr_key] = Option(curr_key)
		else:
			options[curr_key].add_keys(l.strip())

	elif i in cmd_lines and i in descr_lines:

		if curr_key is None or (not curr_key is None and options[curr_key].has_descr()):
			curr_key = l[:descr_indention].strip()
			options[curr_key] = Option(curr_key)
		else:
			options[curr_key].add_keys(l[:descr_indention].strip())

		options[curr_key].add_descr(l[descr_indention:])
	elif i in descr_lines:
		options[curr_key].add_descr(l)

all_shorts = {}
for o in options:
	# print "-"*40
	# print options[o]
	for s in options[o].keys_short:
		if s in all_shorts:
			print "collision:"
			print all_shorts[s]
			print options[o]
			exit()
		else:
			all_shorts[s] = options[o]


for p in params:
	print ""
	k = short_key(p)
	if k in all_shorts:
		o = all_shorts[k]
		print "keys:   %s" % ", ".join(o.keys)
		print "descr:  %s" % "\n        ".join(map(lambda x:x.strip(),o.descr))
	else:
		print "unknown param:",k


