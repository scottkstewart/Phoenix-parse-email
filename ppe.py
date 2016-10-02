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

# individual classes
class PhoenixClass(object):
    def __init__(self, session, name):#instantiate data
        # set requests session
        self.session = session
        
        # set classname
        self.name = name

        # set list of urls by quarter
        self.url = ['' for i in range(4)]
        
        # set listss of num/denom by quarter
        self.numerator = [0 for i in range(4)]
        self.denominator = [0 for i in range(4)]
        
        # set lists of grades and assignments lists by quarter
        self.grade = ["" for i in range(7)] #q1, 2, 3, 4, s1, s2, f
        self.assignments = [[] for i in range(4)]

    def setName(self, name):# set classname
        self.name = name

    def getName(self):#return course title
        return self.name

    def setURL(self, url, quarter):#set url to course page by quarter
        self.url[quarter-1] = url

    def getURL(self):#return url to course page
        return self.url

    def setNumerator(self, num):# set array of numerators
        self.numerator = num

    def getNumerator(self):#return numerator to grade
        return self.numerator

    def setDenominator(self, num):# set array of denominators
        self.denominator = num

    def getDenominator(self):#return denominator to grade
        return self.denominator

    def setGrade(self, grade, quarter):#set overall grade by quarter
        self.grade[quarter-1] = grade

    def getGrade(self):#return overall grade
        return self.grade

    def setAssignments(self, assignments):#set list of assignments
        self.assignments = assignments
    
    def getAssignments(self):#return list of assignments
        return self.assignments

    def printAssignments(self, quarter):
        for assignment in self.assignments[quarter-1]:
            print("------>\t" + assignment[0] + ": " + assignment[1])

    def getScore(self, text):
        '''Helper method to get score from 'n out of n' style strings, returns tuple of numerator,
        denominator.'''
        score = re.split(' ', text)
        if score[0] == '':
            offset = 1
        else:
            offset = 0
        return (float(score[offset]), float(score[3+offset]))

    def update(self, quarter):#update assignments/num/denom
        #instantiate session/get page
        page = self.session.get(self.url[quarter-1])
        req = BeautifulSoup(page.text, 'lxml')
        tempTable = req.findAll('table', {'class':'info_tbl'})
        
        if len(tempTable) == 3:#workaround for weight tables in weighted classes
            rows = tempTable[1].findAll('tr')
        else:
            rows = tempTable[0].findAll('tr')

        #set num/denom to floats
        if len(rows) > 2:
            self.numerator[quarter-1], self.denominator[quarter-1] = self.getScore(rows[-1].findAll('td')[1].text)
        else:
            self.numerator[quarter-1] = self.denominator[quarter-1] = 0

        for ind, tr in enumerate(rows[2:-1]):#iterate through each assignment
            cols = tr.findAll('td')

            if cols[4].text[0].isnumeric():#interpret score as numerator/denominator
                num, denom = self.getScore(cols[4].text) 
            else:
                num = denom = '0'

            #instantiate assignment as tuple
            assignment = (cols[1].text, '({}/{})'.format(num, denom))
            
            #if it's new, either add to or replace from assignment list1
            if ind >= len(self.assignments[quarter-1]):
                self.assignments[quarter-1].append(assignment)
            elif self.assignments[quarter-1][ind] != assignment:
                self.assignments[quarter-1][ind] = assignment

# individual student
class PhoenixChecker(object):
    def __init__(self, user, password, email, classes=[]): #initializes variables and updates
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
        self.classes = classes
        
        # log in and set urls
        self.updatePage()
        self.urlUpdate()
        
        # update all grades
        for i in range(len(self.urls)):
            self.update(i+1)

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

    def check(self, echo=False, verbose=False, quarter=0):#checks for changes
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
            tempClasses.append(PhoenixClass(self.session, cl.getName()))
            
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
                            break

                    if new:#if it's new, add it to the list of new assignments
                        newAs.append([assignment[0], assignment[1]])
                
                #add change to log
                changes.append((classO.getName(), '{} ({}/{}) -> {} ({}/{})'.format(str(classO.getGrade()[quarter-1]), str(classO.getNumerator()[quarter-1]), str(classO.getDenominator()[quarter-1]), str(classN.getGrade()[quarter-1]), str(classN.getNumerator()[quarter-1]), str(classN.getDenominator()[quarter-1])), newAs))
        if changes == []: #if blank, do nothing
            if echo:
                print('No Changes')
        else: #otherwise, print, log, and email changes
            subject = 'Change to'
            message = 'All changes:\n'
            
            # read log and delete lines past 1000
            logfile = open('/etc/ppe/log', 'r')
            log = logfile.readlines()
            logfile.close()
            if len(log) + len(changes) > 1000:
                log = log[(-1000+len(changes)):]

            new = []
            for change in changes:
                # add change to log
                new.append('[{}] [{}] Q{} {} {}'.format(self.username, str(datetime.datetime.now()), str(quarter), change[0], change[1]))

                # print change
                if echo:
                    print('Q{} {} {}'.format(quarter, change[0], change[1]))
                
                # add to subject
                subject += ' ' + change[0]
                
                #give overview of course
                message += '\n\n{}:\n{}'.format(change[0], change[1])
                
                #add individual assignment changes
                for assignment in change[2]:
                    message += '\n{}: {}'.format(assignment[0], assignment[1])
           
            # overwrite log file with new file
            logfile = open('/etc/ppe/log', 'w')
            logfile.write(''.join(log) + "\n".join(new) + "\n")
            logfile.close()

            # add quarter to subject
            subject += ' in quarter ' + str(quarter)

            #send the email
            self.sendMail(message, subject)
   
    def updatePage(self):
        #get page
        req = self.session.get('https://portal.lcps.org/Login_Student_PXP.aspx?regenerateSessionId=True')
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

    def update(self, quarter=0):
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
                grade = cols[5].text
                 
                #remove parentheses from course title
                parenMinus = re.search('([\sA-Za-z0-9_&:{}",\-\ \. \/\[\]]+)',courseTitle)
                #if new class, add it to the list
                if count >= len(self.classes):                     
                    self.classes.append(PhoenixClass(self.session, parenMinus.group()))
                
                # update grade/url
                self.classes[count].setGrade(grade, quarter)
                self.classes[count].setURL('https://portal.lcps.org/'+cols[5].find('a')['href'], quarter)
                
                # if it's quarter 2/4, update S2 and final grade
                if quarter == 2:
                    self.classes[count].setGrade(cols[6].text, 5)   #s1
                elif quarter == 4:
                    self.classes[count].setGrade(cols[6].text, 6)   #s2
                    self.classes[count].setGrade(cols[7].text, 7)   #fg
                
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

            if len(self.deurl) < 4:
                self.deurl.append('https://portal.lcps.org/PXP_Gradebook.aspx?AGU=0')
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
        
        if len(self.urls) < 4:
            self.urls.append('https://portal.lcps.org/PXP_Gradebook.aspx?AGU=0')
        # increment current quarter for human readibility (over list index notation)
        self.currentQuarter += 1

    def printGrades(self, quarter=0, verbose=False):#prints summary of grades
        if quarter == 0:
            quarter = self.currentQuarter
        #print the current time
        print('\n' + str(datetime.datetime.now()))
        
        #print header
        print('*'*19 + self.username + ' Q' + str(quarter) + '*'*20)
        
        #per class, print name and vertically aligned grades/num/denom
        for cl in self.classes:
            print('{}:{}{} ({}/{})'.format(cl.getName(), '\t'*(3 - int((len(cl.getName())+2)/8)), cl.getGrade()[quarter-1], str(cl.getNumerator()[quarter-1]), str(cl.getDenominator()[quarter-1])))
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
