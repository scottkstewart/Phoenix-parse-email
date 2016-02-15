import re
import requests
from bs4 import BeautifulSoup

class phoenixClass(object):
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
        self.grade = [0 for i in range(4)]
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

    def update(self, quarter):#update assignments/num/denom
        #instantiate session/get page
        page = self.session.get(self.url[quarter-1])
        req = BeautifulSoup(page.text, 'lxml')
        tempTable = req.findAll('table', {'class':'info_tbl'})
        
        if len(tempTable) == 3:#workaround for weight tables in weighted classes
            rows = tempTable[1].findAll('tr')
        else:
            rows = tempTable[0].findAll('tr')
        
        #set num/denom to 0
        self.numerator[quarter-1] = self.denominator[quarter-1] = 0

        ind = 0

        for tr in rows[2:-1]:#iterate through each assignment
            cols = tr.findAll('td')

            num = denom = 0

            score = cols[4].text
            if score[0].isnumeric():#interpret score as numerator/denominator
                if score[1] == ' ':
                    num = float(score[0])
                    denom = float(score[9:])
                elif score[2] == ' ':
                    num = float(score[0:2])
                    denom = float(score[10:])
                elif score[3] == ' ':
                    num = float(score[0:3])
                    denom = float(score[11:])
                else:
                    num = float(score[0:4])
                    denom = float(score[12:])
                

            #add numerator/denominator of assignment to overal num/denom
            self.numerator[quarter-1] += num
            self.denominator[quarter-1] += denom
            
            #instantiate assignment as list
            assignment = [cols[1].text, '(' + str(num) + '/' + str(denom) + ')']
            
            #if it's new, either add to or replace from assignment list1
            if ind >= len(self.assignments[quarter-1]):
                self.assignments[quarter-1].append(assignment)
            elif self.assignments[quarter-1][ind] != assignment:
                self.assignments[quarter-1][ind] = assignment

            ind += 1
