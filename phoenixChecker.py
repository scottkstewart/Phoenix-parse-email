import datetime
import smtplib
import re
import json
import requests
import time
import copy
from time import sleep
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class phoenixChecker(object):
    def __init__(self, user, password, email): #3-arg constructor
        self.session = requests.session()
        
        self.username = user
        self.password = password
        self.email = email

        self.numDenom = [[0 for j in range(2)] for i in range(7)]
        self.grades = [['' for j in range(2)] for i in range(7)]

        self.update()

    def setUsername(self, user):#sets username
        self.username = user

    def setPassword(self, password):#sets password
        self.password = password

    def setEmail(self, email):#sets email
        self.email = email

    def check(self):#checks for changes
        #create copy and update
        tempNum = [[0 for i in range(2)] for j in range(7)]
        tempTable = []

        for i in range(len(tempNum)):
            for j in range(len(self.numDenom[i])):
                tempNum[i][j] = self.numDenom[i][j]
        
        for rows in self.gradeTable:
            tempTable.append(rows)

        self.update()
        #print
        self.printGrades()
        
        #if different, emails differences
        if tempNum != self.numDenom:
            changes = []
            for i in range(len(self.gradeTable)):#iterates through each row
                rowsO = tempTable[i].findAll('tr')
                rowsN = self.gradeTable[i].findAll('tr')
                for j in range(len(rowsO[i + 1:])):#find each percentage
                    colsO = rowsO[j+1].findAll('td')
                    colsN = rowsN[j+1].findAll('td')
                    
                    mp2O = colsO[5]
                    mp2N = colsN[5]
                   
                    parenMinus = re.search('([\nA-Za-z0-9_:{}",\-\ \. \/\[\]]+)',colsO[1].text)

                    #add changes to list of strings
                    if tempNum[j] != self.numDenom[j]:
                        changes.append(parenMinus.group() + ' ' + mp2O.text +  ' (' + str(tempNum[j][0]) + '/' + str(tempNum[j][1]) + ') -> ' + mp2N.text + ' (' + str(self.numDenom[j][0]) + '/' + str(self.numDenom[j][1]) + ')')
                        
            #print and email changes
            time = str(datetime.datetime.now())
            for change in changes:
                print(change)
                self.sendMail(change, 'GRADE UPDATE')
        else:
            print('No Changes')
    
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

        for i in range(len(self.gradeTable)):
             
             rows = self.gradeTable[i].findAll('tr')
             for tr in rows[i + 1:]:
                 cols = tr.findAll('td')
                 courseTitle = cols[1].text
                 mp2 = cols[5].text
                 
                 parenMinus = re.search('([\nA-Za-z0-9_:{}",\-\ \. \/\[\]]+)',courseTitle)
                 
                 self.grades[count][0] = parenMinus.group()
                 self.grades[count][1] = mp2

                 count += 1
        
        self.updateNumDenom()

    def printGrades(self):#prints summary of grades
        now = datetime.datetime.now()
        
        print()
        print(str(now))
        print('*'*19 + self.username + '*'*19)
        
        for i in range(len(self.grades)):
            print(self.grades[i][0] + ': ' + '\t'*(3 - int((len(self.grades[i][0])+2)/8))+ str(self.grades[i][1]) + ' (' + str(self.numDenom[i][0]) + '/' + str(self.numDenom[i][1]) + ')')
        print('*'*44)

    def sendMail(self, message, subject):#sends emai
        server = smtplib.SMTP('smtp.gmail.com',587)
        server.starttls()
        server.login('phoenixpythonbot@gmail.com', 'pythonpass')
        
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = 'phoenixpythonbot@gmail.com'
        msg['To'] = self.email
        msg.attach(MIMEText(message, 'plain'))

        server.send_message(msg)
        server.quit()

    def updateNumDenom(self):#updates every course's numerator and denominator
        ind = 0
        for i in range(len(self.gradeTable)):
            rows = self.gradeTable[i].findAll('tr')

            for tr in rows[i + 1:]:
                cols = tr.findAll('td')
                self.pageNumDenom(ind, 'https://portal.lcps.org/' +  cols[5].find('a')['href'])
                ind += 1

    def pageNumDenom(self, ind,  url):#updates single course's numerator and denominator
        page = self.session.get(url)
        req = BeautifulSoup(page.text, 'lxml')
        tempTable = req.findAll('table', {'class':'info_tbl'})
        if len(tempTable) == 3:
            rows = tempTable[1].findAll('tr')
        else:
            rows = tempTable[0].findAll('tr')
        
        self.numDenom[ind][0] = self.numDenom[ind][1] = 0
        
        for tr in rows[2:-1]:
            cols = tr.findAll('td')
            
            score = cols[4].text
            if score[0].isnumeric():
                if score[1] == ' ':
                    self.numDenom[ind][0] += float(score[0])
                    self.numDenom[ind][1] += float(score[9:])
                elif score[2] == ' ':
                    self.numDenom[ind][0] += float(score[0:2])
                    self.numDenom[ind][1] += float(score[10:])
                else:
                    self.numDenom[ind][0] += float(score[0:3])
                    self.numDenom[ind][1] += float(score[11:])
