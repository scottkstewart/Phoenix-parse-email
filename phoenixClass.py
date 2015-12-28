import re
import requests
from bs4 import BeautifulSoup

class phoenixClass(object):
    def __init__(self, session, name, url, num, denom, grade, assignments):#instantiate data
        self.session = session
        
        self.name = name
        self.url = url
        
        self.numerator = num
        self.denominator = denom
        
        self.grade = grade
        self.assignments = assignments

    def setName(self, name):#set course title
        self.name = name

    def getName(self):#return course title
        return self.name

    def setURL(self, url):#set url to course page
        self.url = url

    def getURL(self):#return url to course page
        return self.url

    def setNumerator(self, num):#set numerator to grade
        self.numerator = num

    def getNumerator(self):#return numerator to grade
        return self.numerator

    def setDenominator(self, denom):#set denominator to grade
        self.denominator = denom

    def getDenominator(self):#return denominator to grade
        return self.denominator

    def setGrade(self, grade):#set overall grade
        self.grade = grade

    def getGrade(self):#return overall grade
        return self.grade

    def setAssignments(self, assignments):#set list of assignments
        self.assignments = assignments
    
    def getAssignments(self):#return list of assignments
        return self.assignments

    def update(self):#update assignments/num/denom
        #instantiate session/get page
        page = self.session.get(self.url)
        req = BeautifulSoup(page.text, 'lxml')
        tempTable = req.findAll('table', {'class':'info_tbl'})

        if len(tempTable) == 3:#workaround for weight tables in weighted classes
            rows = tempTable[1].findAll('tr')
        else:
            rows = tempTable[0].findAll('tr')
        
        #set num/denom to 0
        self.numerator = self.denominator = 0

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
                else:
                    num = float(score[0:3])
                    denom = float(score[11:])
            
            #add numerator/denominator of assignment to overal num/denom
            self.numerator += num
            self.denominator += denom
            
            #instantiate assignment as list
            assignment = [cols[1].text, '(' + str(num) + '/' + str(denom) + ')']
            
            #if it's new, either add to or replace from assignment list1
            if ind >= len(self.assignments):
                self.assignments.append(assignment)
            elif self.assignments[ind] != assignment:
                self.assignments[ind] = assignment

            ind += 1
