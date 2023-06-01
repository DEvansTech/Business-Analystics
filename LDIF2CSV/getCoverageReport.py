import logging
import getopt
import sys
import math
from tokenize import group
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

def generateCoverageReport(inputFile, outputFile, fieldSeparater, textDelimiter):
    inputF = open(inputFile, "rb")
    outputF = open(outputFile, "w")
    tableParser = PivotTable_Parser(inputF)
    tableParser._parse()

    columns = ["ID", "Entity", "Count", "Total number of Assignments", "Total number of Entitlements",
               "Number of Entitlements granted by entity role", "Number of Assignments included in Entity Role",
               "Percent of Access Granted by Entity Role"]
    for column in columns:
        outputF.write(textDelimiter + column + textDelimiter + fieldSeparater)
    outputF.write("\n")

    sortedStatistics = dict(sorted(tableParser._statistics.items()))
    index = 0
    for companyName, companyStatistic in sortedStatistics.items():
        index += 1
        fields = {}
        fields["ID"] = index
        fields["Entity"] = companyName
        fields["Count"] = companyStatistic["employeeCount"]
        fields["Total number of Assignments"] = 0
        fields["Total number of Entitlements"] = len(companyStatistic["groups"])
        fields["Number of Entitlements granted by entity role"] = 0
        fields["Number of Assignments included in Entity Role"] = 0
        fields["Percent of Access Granted by Entity Role"] = 0
        for groupName, groupMembers in companyStatistic["groups"].items():
            fields["Total number of Assignments"] += groupMembers
            if round(groupMembers*100.0/companyStatistic["employeeCount"]) >= 70:
                fields["Number of Entitlements granted by entity role"] += 1
                fields["Number of Assignments included in Entity Role"] += groupMembers
        fields["Percent of Access Granted by Entity Role"] = str(round(fields["Number of Assignments included in Entity Role"] * 100.0/fields["Total number of Assignments"])) + "%"
        for fieldName, fieldValue in fields.items():
            outputF.write(textDelimiter + str(fieldValue) + textDelimiter + fieldSeparater)
        outputF.write("\n")
    outputF.close()
    inputF.close()

if __name__ == "__main__":
    inputFile = "../resource/origin.ldf"
    outputFile = "../resource/origin_coverage_report.csv"
    fieldSeparater = ","
    textDelimiter = "\""

    setupLogging()

    primaryLogger.debug("outputFile: %s" % outputFile)
    primaryLogger.debug("fieldSeparater: %s" % fieldSeparater)
    primaryLogger.debug("textDelimiter: %s" % textDelimiter)
    generateCoverageReport(inputFile, outputFile, fieldSeparater, textDelimiter)
