import os
from flask import Flask, request

app = Flask(__name__)

@app.route('/')
@app.route('/loanRequestApi/', methods = ['GET', 'POST'])
def loanRequest():
	if(request.method == 'GET'):
		return "GET METHOD"
	elif(request.method == 'POST'):		
		content = json.loads(request.data)
	print(str(content))
	
	return str(content)
	