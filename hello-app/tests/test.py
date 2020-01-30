#!/usr/bin/python
import sys, os
testdir = os.path.dirname(__file__)
srcdir = '../'
sys.path.insert(0, os.path.abspath(os.path.join(testdir, srcdir)))

import flask_restful
import hello
import config

def get():
   return "Hello World" 
get()

