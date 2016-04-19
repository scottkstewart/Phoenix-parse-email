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

class phoenixChecker(object):
    def __init__(self, user, password, email): #initializes variables and updates
        # get phoenixClass class
        phoenixModule = imp.load_source('phoenixClass', os.getenv("HOME") + '/.PPE/phoenixClass.py'    )
        self.phoenixClass = phoenixModule.phoenixClass

        # instantiate requests session for web parsing
        self.session = requests.session()
        
        # instantiate basic user data
        self.username = user
        self.password = password
        self.email = email
        
        # instantiate current quarter, url in case of dual high-school enrollment, and all urls
        self.currentQuarter = 0
        self.deurl = []
        self.urls = []
        
        # instantiate array of classes
        self.classes = []
        
        # log in and set urls
        self.updatePage()
        self.urlUpdate()
        
        # update all grades
        for i in range(len(self.urls)):
            self.update(i)

    def setUsername(self, user):#sets username
        self.username = user

    def getUsername(self):# returns username
        return self.username

    def setPassword(self, password):#sets password
        self.password = password

    def getPassword(self):# returns password
        return self.password

    def setEmail(self, email):#sets email
        self.email = email

    def getEmail(self):# returns email
        return self.email

    def check(self, echo, verbose, quarter):#checks for changes
        # update all urls for gradebook pages (not classes)
        self.updatePage()
        self.urlUpdate()
        
        # if current quarter is specified (0), prep for that
        if quarter == 0:
            quarter = self.currentQuarter

        #declare array
        tempClasses = []

        #create deep copy of classes
        for ind, cl in enumerate(self.classes):
            #create class
            tempClasses.append(self.phoenixClass(self.session, cl.getName()))
            
            #set all data
            tempClasses[ind].setURL(cl.getURL()[quarter-1], quarter)
            tempClasses[ind].setDenominator(copy.copy(cl.getDenominator()))
            tempClasses[ind].setNumerator(copy.copy(cl.getNumerator()))
            tempClasses[ind].setGrade(cl.getGrade()[quarter-1], quarter)
            tempClasses[ind].setAssignments(copy.deepcopy(cl.getAssignments()))
        
        #update
        self.update(quarter)
        
        #print grades if 'echo' is specified
        if echo:
            self.printGrades(quarter, verbose)
        
        #logs changes
        changes = []
        for i in range(len(self.classes)):#iterates through each class
            classO = tempClasses[i]
            classN = self.classes[i]
                
            #if numerator/denominator are different, log assignment changes
            if classO.getNumerator() != classN.getNumerator() or classO.getDenominator() != classN.getDenominator():
                
                #clears changes to this particular class
                newAs = []
                for assignment in classN.getAssignments()[quarter-1]:#iterates through assignments
                    new = True

                    for temp in classO.getAssignments()[quarter-1]:#if it matches any, it isn't new
                        if assignment[0] == temp[0] and assignment[1] == temp[1]:
                            new = False    

                    if new:#if it's new, add it to the list of new assignments
                        newAs.append([assignment[0], assignment[1]])
                
                #add change to log
                changes.append([classO.getName(), classO.getGrade()[quarter-1] +  ' (' + str(classO.getNumerator()[quarter-1]) + '/' + str(classO.getDenominator()[quarter-1]) + ') -> ' + classN.getGrade()[quarter-1] + ' (' + str(classN.getNumerator()[quarter-1]) + '/' + str(classN.getDenominator()[quarter-1]) + ')', newAs])
        
        if changes == []: #if blank, do nothing
            if echo:
                print('No Changes')
        else: #otherwise, print, log, and email changes
            subject = 'Change to'
            message = 'All changes:\n'
            
            # read log and delete lines past 1000
            logfile = open(os.getenv("HOME") + '/.PPE/log', 'r')
            log = logfile.readlines()
            logfile.close()
            if len(log) + len(changes) > 1000:
                log = log[(-1000+len(changes)):]

            new = []
            for change in changes:
                # add change to log
                new.append('[' + self.username + '] [' + str(datetime.datetime.now()) + '] Q' + str(quarter) + ' ' + change[0] + ' ' + change[1])
                 
                # print change
                if echo:
                    print('Q' + quarter + ' ' + change[0] + ' ' + change[1])
                
                # add to subject
                subject += ' ' + change[0]
                
                #give overview of course
                message += '\n\n' + change[0] + ':\n' + change[1]
                
                #add individual assignment changes
                for assignment in change[2]:
                    message += '\n' + assignment[0] + ': ' + assignment[1]
           
            # overwrite log file with new file
            logfile = open(os.getenv("HOME") + '/.PPE/log', 'w')
            logfile.write(''.join(log) + "\n".join(new) + "\n")
            logfile.close()

            # add quarter to subject
            subject += ' in quarter ' + str(quarter)

            #send the email
            self.sendMail(message, subject)
   
    def updatePage(self):
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
        #log in
        logPage = self.session.post('https://portal.lcps.org/Login_Student_PXP.aspx', data=data, headers=headers)

    def update(self, quarter):
        # if current quarter is specified, prep for that
        if quarter == 0:
            quarter = self.currentQuarter
        
        # get page based on quarter
        gradeBook = self.session.get(self.urls[quarter-1])
        req =  BeautifulSoup(gradeBook.text, 'lxml')
        self.gradeTable = req.findAll('table', {'class':'info_tbl'})
        
        # if enrolled in two schools, append earlier table
        if len(self.deurl) > 0:
            gradeBook = self.session.get(self.deurl[quarter-1])
            req =  BeautifulSoup(gradeBook.text, 'lxml')
            self.gradeTable[0] = req.find('table', {'class':'info_tbl'})

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
                #if new class, add it to the list
                if count >= len(self.classes):                     
                    self.classes.append(self.phoenixClass(self.session, parenMinus.group()))
                
                # update grade/url
                self.classes[count].setGrade(mp2, quarter)
                self.classes[count].setURL('https://portal.lcps.org/'+cols[5].find('a')['href'], quarter)
                #update num/denom/assignments
                self.classes[count].update(quarter) 
                    
                count += 1
    
    def urlUpdate(self):
        #get general page
        gradeBook = self.session.get('https://portal.lcps.org/PXP_Gradebook.aspx?AGU=0')
        req =  BeautifulSoup(gradeBook.text, 'lxml')
        pageURLS = req.findAll('div', {'class':'heading_breadcrumb'})
       
        
        self.currentQuarter = 0
        self.deurl = []
        if len(pageURLS) == 2:# if multiple sets of urls, set urls to quarters for other school
            # set url to later class after this one
            pageURL = pageURLS[1]
            
            
            rawurls = []
            currentQuarterBool = [True for i in range(4)]
            for mp in pageURLS[0].findAll('a'):# find current quarter and rawurls
                rawurls.append('https://portal.lcps.org/'+mp['href'])
            
                for i in range(1, 5):
                    if int(mp.text[15]) == i:
                        currentQuarterBool[i-1] = False
            
            # convert current quarter to number
            for ind, cur in enumerate(currentQuarterBool):
                if cur:
                    self.currentQuarter = ind
            
            # append urls to list, appending home page at current quarter
            for ind, url in enumerate(rawurls):
                if ind == self.currentQuarter:
                    self.deurl.append('https://portal.lcps.org/PXP_Gradebook.aspx?AGU=0')

                self.deurl.append(url)
        else:# if no other school, set list of urls to first list
            pageURL = pageURLS[0]
        
        rawurls = []
        
        # specify whether current quarter has already been found
        noDE = self.currentQuarter == 0

        if noDE:
            currentQuarterBool = [True for i in range(4)]
        
        for mp in pageURL.findAll('a'):# get raw urls, current quarter if not already found
            rawurls.append('https://portal.lcps.org/'+mp['href'])
            
            if noDE:
                for i in range(1, 5):
                    if int(mp.text[15]) == i:
                        currentQuarterBool[i-1] = False
        
        if noDE:# convert current quarter to int if not already found
            self.currentQuarter = 0
            for ind, cur in enumerate(currentQuarterBool):
                if cur:
                    self.currentQuarter = ind
        
        self.urls = []
        for ind, url in enumerate(rawurls):# append urls, with homepage for current quarter
            if ind == self.currentQuarter:
                self.urls.append('https://portal.lcps.org/PXP_Gradebook.aspx?AGU=0')

            self.urls.append(url)
        
        # increment current quarter for human readibility (over list index notation)
        self.currentQuarter += 1

    def printGrades(self, quarter, verbose):#prints summary of grades
        if quarter == 0:
            quarter = self.currentQuarter
        #print the current time
        print('\n' + str(datetime.datetime.now()))
        
        #print header
        print('*'*19 + self.username + ' Q' + str(quarter) + '*'*20)
        
        #per class, print name and vertically aligned grades/num/denom
        for cl in self.classes:
            print(cl.getName() + ': ' + '\t'*(3 - int((len(cl.getName())+2)/8)) + str(cl.getGrade()[quarter-1]) + ' (' + str(cl.getNumerator()[quarter-1]) + '/' + str(cl.getDenominator()[quarter-1]) + ')')
            if verbose:# if verbosity is specified, print individual assignments
                cl.printAssignments(quarter)
        print('*'*48)

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
