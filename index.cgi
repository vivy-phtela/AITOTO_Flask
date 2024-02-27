#!/usr/local/bin/python3.7
import cgitb

cgitb.enable()
from wsgiref.handlers import CGIHandler

from app import app

CGIHandler().run(app)
