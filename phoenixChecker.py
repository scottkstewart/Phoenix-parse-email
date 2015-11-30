import datetime
import smtplib
import re
import json
import requests
import time
from time import sleep
from bs4 import BeautifulSoup
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
        tempNum = self.numDenom
        self.update()
        
        #print
        self.printGrades()
        
        #if different, emails differences
        if tempNum != self.numDenom:
            count = 0
            changes[0] = 'error: misfire'
            for i in range(len(temp)):#iterates through each row
                rowsO = temp[i].findAll('tr')
                rowsN = self.gradeTable[i].findAll('tr')
                for j in range(len(rows[i + 1:])):#find each percentage
                    colsO = rowsO[j].findAll('td')
                    colsN = rowsN[j].findAll('td')
                    
                    mp2O = colsO[5]
                    mp2N = colsN[5]
                    #add changes to list of strings
                    if tempNum[i] != self.numDenom[i]:
                        changes[count] = colsO[1].text + ' (' + str(tempNum[i][0]) + '/' + str(tempNum[i][1]) + ') : ' + mp2O.text + ' -> ' + mp2N.text + ' (' + str(self.numDenom[i][0]) + '/' + str(self.numDenum[i][1]) + ')'
                        count += 1
            
            #print and email changes
            print(changes)
            self.sendMail(changes)
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
        print('*'*44)
        
        for i in range(len(self.grades)):
            print(self.grades[i][0] + ': ' + '\t'*(3 - int((len(self.grades[i][0])+2)/8))+ str(self.grades[i][1]) + ' (' + str(self.numDenom[i][0]) + '/' + str(self.numDenom[i][1]) + ')')
        print('*'*44)

    def sendMail(self, message):#sends emai
        server = smtplib.SMTP('smtp.gmail.com')
        server.starttls()
        server.login('phoenixpythonbot@gmail.com', 'pythonpass')
        server.sendmail('phoenixpythonbot@gmail.com', self.email, message)
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
                    self.numDenom[ind][1] += f(score[11:])
