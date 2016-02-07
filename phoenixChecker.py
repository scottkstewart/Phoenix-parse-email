import datetime
import smtplib
import re
import requests
import copy
import os
import imp
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from copy import deepcopy

class phoenixChecker(object):
    def __init__(self, user, password, email): #initializes variables and updates
        # get phoenixClass class
        phoenixModule = imp.load_source('phoenixClass', os.getenv("HOME") + '/.PPE/phoenixClass.py'    )
        phoenixClass = phoenixModule.phoenixClass


        self.session = requests.session()
        
        self.username = user
        self.password = password
        self.email = email

        self.classes = []
        
        self.update()
        
    def setUsername(self, user):#sets username
        self.username = user

    def setPassword(self, password):#sets password
        self.password = password

    def setEmail(self, email):#sets email
        self.email = email

    def check(self):#checks for changes
        #declare array
        tempClasses = []

        #create deep copy of classes
        for cl in self.classes:
            tempClasses.append(phoenixClass(self.session, cl.getName(), cl.getURL(), cl.getNumerator(), cl.getDenominator(), cl.getGrade(), copy.deepcopy(cl.getAssignments())))
        
        #update
        self.update()
        
        #print grades
        self.printGrades()
        
        #logs changes
        changes = []
        for i in range(len(self.classes)):#iterates through each class
            classO = tempClasses[i]
            classN = self.classes[i]
                
            #if numerator/denominator are different, log assignment changes
            if classO.getNumerator() != classN.getNumerator() or classO.getDenominator() != classN.getDenominator():
                #clears changes to this particular class
                newAs = []
                
                for assignment in classN.getAssignments():#iterates through assignments
                    new = True

                    for temp in classO.getAssignments():#if it matches any, it isn't new
                        if assignment[0] == temp[0] and assignment[1] == temp[1]:
                            new = False    

                    if new:#if it's new, add it to the list of new assignments
                        newAs.append([assignment[0], assignment[1]])
                
                #add change to log
                changes.append([classO.getName(), classO.getGrade() +  ' (' + str(classO.getNumerator()) + '/' + str(classO.getDenominator()) + ') -> ' + classN.getGrade() + ' (' + str(classN.getNumerator()) + '/' + str(classN.getDenominator()) + ')', newAs])
        
        if changes == []: #if blank, do nothing
            print('No Changes')
        else: #otherwise, print and email changes
            subject = 'Change to'
            message = 'All changes:\n'
           
            for change in changes:
                print(change[0] + ' ' + change[1])
                subject += ' ' + change[0]
                
                #give overview of course
                message += '\n\n' + change[0] + ':\n' + change[1]
                
                #add individual assignment changes
                for assignment in change[2]:
                    message += '\n' + assignment[0] + ': ' + assignment[1]
            #send the email
            self.sendMail(message, subject)
    
    def update(self):
        #get page
        req = self.session.get('https://portal.lcps.org/Login_Student_PXP.aspx')
        page = BeautifulSoup(req.text, "lxml")

        #get viewstate, eventvalidation
        viewState = page.find('input', {'name':'__VIEWSTATE'})['value']
        eventValidate = page.find('input', {'name':'__EVENTVALIDATION'})['value']

        #define dictionary of headers
        headers = {
            'Origin':'https://portal.lcps.org',
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'en-US,en;q=0.8',
            'Upgrade-Insecure-Requests':'1',
            'User-Agent':'Mozilla/5.0',
            'Content-Type':'application/x-www-form-urlencoded',
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Cache-Control':'max-age=0',
            'Referer':'https://portal.lcps.org/Login_Student_PXP.aspx',
            'Connection':'keep-alive',
        }

        #define data (incl username, password)
        data = {
            '__VIEWSTATE': viewState,
            '__EVENTVALIDATION': eventValidate,
            'username': self.username,
            'password': self.password,
        }
        #log in and get page
        logPage = self.session.post('https://portal.lcps.org/Login_Student_PXP.aspx', data=data, headers=headers)
        gradeBook = self.session.get('https://portal.lcps.org/PXP_Gradebook.aspx?AGU=0')
        req =  BeautifulSoup(gradeBook.text, 'lxml')
        self.gradeTable = req.findAll('table', {'class':'info_tbl'})
        
        count = 0

        for i in range(len(self.gradeTable)): #iterate through schools
             
             rows = self.gradeTable[i].findAll('tr') #get rows of table
             for tr in rows[i + 1:]:# workaround for multivariable calculus
                 #get columns per row
                 cols = tr.findAll('td')
                 
                 #find course title and grade
                 courseTitle = cols[1].text
                 mp2 = cols[5].text
                 
                 #remove parentheses from course title
                 parenMinus = re.search('([\nA-Za-z0-9_:{}",\-\ \. \/\[\]]+)',courseTitle)
                 #if new class, add it to the list, otherwise update URL/grade
                 if count >= len(self.classes):                     
                    self.classes.append(phoenixClass(self.session, parenMinus.group(), 'https://portal.lcps.org/'+cols[5].find('a')['href'], 0, 0, mp2, []))
                 else:
                    self.classes[count].setURL('https://portal.lcps.org/'+cols[5].find('a')['href'])
                    self.classes[count].setGrade(mp2)
                 
                 #update num/denom/assignments
                 self.classes[count].update()
                    
                 count += 1
    
    def printGrades(self):#prints summary of grades
        #print the current time
        print('\n' + str(datetime.datetime.now()))
        
        #print header
        print('*'*19 + self.username + '*'*19)
       
        #per class, print name and vertically aligned grades/num/denom
        for cl in self.classes:
            print(cl.getName() + ': ' + '\t'*(3 - int((len(cl.getName())+2)/8))+ cl.getGrade() + ' (' + str(cl.getNumerator()) + '/' + str(cl.getDenominator()) + ')')
        
        print('*'*44)

    def sendMail(self, message, subject):#sends emai
        #instantiate smtp server
        server = smtplib.SMTP('smtp.gmail.com',587)
        server.starttls()
        server.login('phoenixpythonbot@gmail.com', 'pythonpass')
        
        #create message
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = 'phoenixpythonbot@gmail.com'
        msg['To'] = self.email
        msg.attach(MIMEText(message, 'plain'))
        
        #send message and exit
        server.send_message(msg)
        server.quit()
