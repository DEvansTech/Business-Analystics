import logging
import getopt
import sys
import math
from ldif import LDIF_Parser

class PivotTable_Parser(LDIF_Parser):
    def __init__(self, inputF):
        super().__init__(inputF)
        self._statistics = {}

    def handle(self, dn, entry):
        if "memberOf" not in entry.keys():
            entry["memberOf"] = []
        if "employeeID" not in entry.keys():
            return

        try:
            company = entry["company"][0]
        except:
            return
        if company not in self._statistics:
            self._statistics[company] = {"employeeCount": 1, "groups": {}}
        self._statistics[company]["employeeCount"] += 1
        for group in entry["memberOf"]:
            if group not in self._statistics[company]["groups"].keys():
                self._statistics[company]["groups"][group] = 2
            else:
                self._statistics[company]["groups"][group] += 1


# Logging Function Definition
def setupLogging(filename="log.txt"):
    global primaryLogger
    primaryLogger = logging.Logger("primaryLogger", logging.DEBUG)
    
    if(filename != ""):
        fileHandler = logging.FileHandler(filename=filename, mode="w", encoding=None, delay=0)
    else:
        fileHandler = logging.NullHandler()
    primaryLoggerFormat = logging.Formatter("[%(asctime)s][%(funcName)s] - %(message)s", '%m/%d/%y %I:%M%p')
    fileHandler.setFormatter(primaryLoggerFormat)

    primaryLogger.addHandler(fileHandler)

def generatePivotTables(inputFile, outputFile, fieldSeparater, textDelimiter):
    inputF = open(inputFile, "rb")
    outputF = open(outputFile, "w")
    tableParser = PivotTable_Parser(inputF)
    tableParser._parse()

    columns = ["Entity", "Group", "Count of employeeID", "Total users in Company", "Percentage of Users Assigned"]
    for column in columns:
        outputF.write(textDelimiter + column + textDelimiter + fieldSeparater)
    outputF.write("\n")

    sortedStatistics = dict(sorted(tableParser._statistics.items()))
    for companyName, companyStatistic in sortedStatistics.items():
        sortedCompanyStatistic = {"employeeCount": companyStatistic["employeeCount"],
                                  "groups": dict(sorted(companyStatistic["groups"].items(), key=lambda x: x[1], reverse=True))}
        for groupName, groupMembers in sortedCompanyStatistic["groups"].items():
            fields = [
                companyName,
                groupName, 
                str(groupMembers), 
                str(sortedCompanyStatistic["employeeCount"]), 
                str(round(groupMembers*100.0/sortedCompanyStatistic["employeeCount"]))+"%"
            ]
            for field in fields:
                outputF.write(textDelimiter + field + textDelimiter + fieldSeparater)
            outputF.write("\n")
    outputF.close()
    inputF.close()

if __name__ == "__main__":
    inputFile = "../resource/origin.ldf"
    outputFile = "../resource/origin_pivot_tables.csv"
    fieldSeparater = ","
    textDelimiter = "\""

    setupLogging()

    primaryLogger.debug("outputFile: %s" % outputFile)
    primaryLogger.debug("fieldSeparater: %s" % fieldSeparater)
    primaryLogger.debug("textDelimiter: %s" % textDelimiter)
    generatePivotTables(inputFile, outputFile, fieldSeparater, textDelimiter)
