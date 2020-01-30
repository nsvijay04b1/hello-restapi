#!/usr/bin/python
import argparse,sys,os


parser = argparse.ArgumentParser(prog='arg')
parser.add_argument('--foo', nargs='?')
parser.add_argument('bar', nargs='?')
args=parser.parse_args([sys.argv[1:]])
print(args['bar'])

