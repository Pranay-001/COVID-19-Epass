import os
from flask import Flask,request
app = Flask(__name__)
from flask import render_template
import requests
import json
import string
from twilio.rest import Client 
import re
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from config import *

client = Client(account_sid, auth_token) 
@app.route('/',methods=["GET","POST"])
@app.route('/index',methods=["GET","POST"])
def index():
    try:
        data = requests.get(url_data).content
        data=json.loads(data)
        dict={}
        states=[]
        for t_dict in data['statewise'][1:-1]:
            states.append(t_dict["state"].lower())
            dict[t_dict["state"].lower()]=t_dict["active"]
            dict[states[-1]+" recovered"]=t_dict["recovered"]
            dict[states[-1]+" confirmed"]=t_dict["confirmed"]
        states.sort()
        # print(dict)
        if(request.method=='POST'):
            details={}
            details["Name"]=string.capwords(request.form.get("name"))
            details["Email"]=string.capwords(request.form.get("email"))
            details["Phone Number"]=request.form.get("phone")
            details["From State"]=string.capwords(request.form.get("from-place"))
            details["To State"]=string.capwords(request.form.get("to-place"))    
            details["From Date"]=request.form.get("date-start")
            details["To Date"]=request.form.get("date-end")
            details["Adults"]=request.form.get("adults")
            details["Childrens"]=request.form.get("childrens")
            send_mail=request.form.get("sendMail")
            send_whatsapp=request.form.get("sendWhatsapp")
            details[details["From State"]+" Active Cases"],details[details["To State"]+" Active Cases"]=dict[details["From State"].lower()],dict[details["To State"].lower()]
            details["Status"]="REJECTED"
            from_recovered_ratio=(int(dict[request.form.get("from-place")+" recovered"])/int(dict[request.form.get("from-place")+" confirmed"]))*100
            to_recovered_ratio=(int(dict[request.form.get("to-place")+" recovered"])/int(dict[request.form.get("to-place")+" confirmed"]))*100
            # print(send_whatsapp,send_mail)
            if(not re.search(regex,details["Email"]) or not details["Childrens"].isnumeric() or not details["Adults"].isnumeric() or not details["Phone Number"].isnumeric() or len(details["Phone Number"])!=10):
                raise Exception('Wrong data') 

            if(from_recovered_ratio>=80 and  to_recovered_ratio>=80):
                details["Status"]="CONFIRMED"
            content="Epass Details\n"\
                    "Name: {}\n".format(details["Name"])+""\
                    "Email: {}\n".format(details["Email"])+""\
                    "From State: {}\n".format(details["From State"])+""\
                    "To State: {}\n".format(details["To State"])+""\
                    "From Date: {}\n".format(details["From Date"])+""\
                    "To Date: {}\n".format(details["To Date"])+""\
                    "Adults: {}\n".format(details["Adults"])+""\
                    "Childrens: {}\n".format(details["Childrens"])+""\
                    "From State Active Cases: {}\n".format(details[details["From State"]+" Active Cases"])+""\
                    "To State Active Cases: {}\n".format(details[details["To State"]+" Active Cases"])+""\
                    "Status: {}".format(details["Status"])
            
            # print(from_death_ratio,to_death_ratio)
            # sms
            message = client.messages.create(   
                        body=content, 
                        from_=sender_sms,     
                        to=rec
                    ) 
            # #whatsapp
            if(send_whatsapp=="true"):
                message = client.messages.create(   
                            body=content, 
                            from_='whatsapp:'+sender_wa,     
                            to='whatsapp:'+rec
                        ) 
            # #email
            if(send_mail=="true"):
                message=Mail(from_email='pc2282001@gmail.com',
                        to_emails='namirafatima28@gmail.com',
                        subject='Epass',
                        html_content=content)
                sg=SendGridAPIClient(email_api_key)
                response=sg.send(message)
            
            return render_template('eticket.html',details=details)
        else:
            return render_template('index.html',states=states,string=string)
    except Exception as error:
        print('Caught this error: ' + repr(error))
        return "<h1>Error Occured "+repr(error)+"</h1>" 
    
if __name__ == '__main__':
    app.debug(True)
    app.run()