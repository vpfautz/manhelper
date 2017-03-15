#!/usr/bin/env python2
#coding: UTF-8

import os
from os.path import join
import gzip
from subprocess import Popen, PIPE
import re
import sys
from collections import defaultdict
import string


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

# Returns the man page of a given programm or None, if it don't exists.
def read_manpage(prog):
	p = Popen(["man", prog], stdout=PIPE, stderr=PIPE)
	stdout,stderr = p.communicate()
	if p.returncode != 0:
		print "[ERROR]",stderr.strip()
		return None

	return stdout

# An IndentionException will be raised, if the most commen indention
# is not like we expect it.
class IndentionException(Exception):
	def __init__(self, err):
		super(IndentionException, self).__init__()
		self.err = err

# Returns the most commen indention of keys.
def get_key_indention(lines):
	count = defaultdict(int)
	for l in lines:
		if not l.strip().startswith("-"):
			continue

		count[get_indent(l)] += 1

	if len(count) == 0:
		raise IndentionException("no normal parameters")

	key_indention = max(count.items(), key=lambda (x,y):y)[0]
	debug("key_indention: %s" % key_indention)
	return key_indention

# Returns the indention of most commen descriptions.
def get_descr_indention(lines):
	count = defaultdict(int)
	for i,l in enumerate(lines):
		if i==0:
			continue

		if not lines[prev(i)].strip().startswith("-"):
			continue

		count[get_indent(l)] += 1

	if len(count) == 0:
		raise IndentionException("no normal description")

	descr_indention = max(count.items(), key=lambda (x,y):y)[0]
	debug("descr_indention: %s" % descr_indention)
	return descr_indention

# Annotates the given lines as key or description.
def annotate_lines(lines, key_indention, descr_indention):
	key_prefix = " "*key_indention+"-"

	key_lines = set()
	descr_lines = set()

	debug("lines: %s" % len(lines))

	for i,l in enumerate(lines):
		if l.startswith(key_prefix):
			k = i + 1
			while lines[k].startswith(key_prefix) or len(lines[k].strip()) == 0:
				k += 1
			if get_indent(lines[k]) == descr_indention:
				if descr_indention < len(l) and l[descr_indention] in string.ascii_letters and l[descr_indention-1] == " ":
					descr_lines.add(i)
				key_lines.add(i)

		elif get_indent(l) == descr_indention:
			if prev(i) in key_lines or prev(i) in descr_lines:
				descr_lines.add(i)

		elif get_indent(l) > descr_indention:
			if prev(i) in descr_lines:
				descr_lines.add(i)

		# debug output
		if i in key_lines and i in descr_lines:
			debug(clr(l[:descr_indention], Color.BLUE) +
			      clr(l[descr_indention:], Color.GREEN))
		elif i in key_lines:
			debug(clr(l, Color.BLUE))
		elif i in descr_lines:
			debug(clr(l, Color.GREEN))
		else:
			debug(l)

	return (key_lines, descr_lines)

# Converts a long key like "-a <b>" to a short key like "-a".
def short_key(key):
	rem = re.findall("( .+$)|=(.+$)|(<.+?>)|(\[.+?\])", key)
	for a,b,c,d in rem:
		key = key.replace(a, "")
		key = key.replace(b, "")
		key = key.replace(c, "")
		key = key.replace(d, "")
	return key

# An Option represents a cli Option, which can have multiple keys and a
# multiline description.
class Option(object):
	def __init__(self, keys):
		super(Option, self).__init__()
		self.keys = []
		self.keys_short = []
		self.add_keys(keys)
		self.descr = []

	# Parse given keys
	def parse_keys(self, keys):
		return map(lambda x:x.strip(), keys.split(", "))

	# Returns true if this already has some description.
	def has_descr(self):
		return len(self.descr) > 0

	# Add a keyline from manpage to keys.
	def add_keys(self, keys):
		new = self.parse_keys(keys)
		self.keys += new
		for k in new:
			self.keys_short.append(short_key(k))

	# Add a description line.
	def add_descr(self, description):
		self.descr.append(description)

	def __repr__(self):
		r = ""
		r += "keys:  %s\n" % self.keys
		r += "short: %s\n" % self.keys_short
		r += "descr: \n%s" % "\n".join(self.descr)
		return r

# Parse the given lines and return a dictionary key -> Option.
def lines_to_options(lines):
	key_indention = get_key_indention(lines)
	descr_indention = get_descr_indention(lines)

	if descr_indention <= key_indention:
		raise IndentionException("descr_indention <= key_indention!")

	key_lines,descr_lines = annotate_lines(lines, key_indention, descr_indention)

	options = {}
	curr_key = None

	for i,l in enumerate(lines):
		if i in key_lines and not i in descr_lines:
			if curr_key is None or (not curr_key is None and options[curr_key].has_descr()):
				curr_key = l.strip()
				options[curr_key] = Option(curr_key)
			else:
				options[curr_key].add_keys(l.strip())

		elif i in key_lines and i in descr_lines:

			if curr_key is None or (not curr_key is None and options[curr_key].has_descr()):
				curr_key = l[:descr_indention].strip()
				options[curr_key] = Option(curr_key)
			else:
				options[curr_key].add_keys(l[:descr_indention].strip())

			options[curr_key].add_descr(l[descr_indention:])
		elif i in descr_lines:
			options[curr_key].add_descr(l)

	return options

# Generate lookuptable option -> Option, from given manpage lines.
def gen_lookup(lines):
	options = lines_to_options(lines)

	all_shorts = {}
	for o in options:
		for s in options[o].keys_short:
			if s in all_shorts:
				debug("collision:")
				debug(all_shorts[s])
				debug(options[o])
				# TODO maybe show both?
				del all_shorts[s]
			else:
				all_shorts[s] = options[o]

	return all_shorts

def possible_multi_param(param):
	return not re.search("^(-\w\w+)$", param) is None

assert possible_multi_param("-a") == False
assert possible_multi_param("a") == False
assert possible_multi_param("aaaaa") == False
assert possible_multi_param("--aaaaa") == False
assert possible_multi_param("--a") == False
assert possible_multi_param("-ab") == True
assert possible_multi_param("-abc") == True

first = True

def print_key_descr(key, lookup):
	global first
	if key in lookup:
		o = lookup[key]
		if not first:
			print ""
		first = False
		print "option: %s" % ", ".join(o.keys)
		print "descr:  %s" % "\n        ".join(map(lambda x:x.strip(),o.descr))
		return

	if not possible_multi_param(key):
		if not first:
			print ""
		first = False
		print "unknown param:",key
		return

	for single in key[1:]:
		print_key_descr("-%s" % single, lookup)


if __name__ == '__main__':
	if len(sys.argv) < 2:
		print "usage: %s cli" % sys.argv[0]
		exit(1)

	prog = sys.argv[1]
	params = sys.argv[2:]
	debug("cli: %s %s" % (prog, " ".join(params)))

	manpage = read_manpage(prog)
	if manpage is None:
		exit(1)
	lines = manpage.split("\n")

	try:
		lookup = gen_lookup(lines)
	except IndentionException as e:
		print "[ERROR]", e.err
		exit(1)

	for param in params:
		key = short_key(param)
		if not key.startswith("-"):
			# skip parameters without - beginning
			continue

		print_key_descr(key, lookup)


