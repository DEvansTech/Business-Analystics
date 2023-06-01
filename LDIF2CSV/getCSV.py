import logging
import getopt
import sys

from ldif import LDIF_Parser

class LDIF_Attribute_Parser(LDIF_Parser):
    def __init__(self, inputF):
        super().__init__(inputF)
        self._attrs = []

    def handle(self, dn, entry):
        if "dn" not in self._attrs:
            self._attrs.append("dn")

        for attr in entry.keys():
            if attr not in self._attrs:
                self._attrs.append(attr)

class LDIF_CSV_Parser(LDIF_Parser):
    def __init__(self, inputF, attrs, output, fieldSeparater, textDelimiter):
        super().__init__(inputF)
        self._attrs = attrs
        self._output = output
        self._fieldSeparater = fieldSeparater
        self._textDelimiter = textDelimiter

    def handle(self, dn, entry):
        if "memberOf" not in entry:
            entry["memberOf"] = [""]
        for group in entry["memberOf"]:
            for attr in self._attrs:
                if attr in entry:
                    if attr == "memberOf":
                        val = group
                    else:
                        val = entry[attr][0].encode("ascii", "replace").decode()
                elif attr == "dn":
                    val = dn.encode("ascii", "replace").decode()
                else:
                    val = ""
                self._output.write(self._textDelimiter + val + self._textDelimiter + self._fieldSeparater)
            self._output.write("\n")


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

def parseAttrs(filename):
    ldifFile = open(filename, "rb")
    primaryLogger.debug("Opened <%s> for reading" % filename)

    attrParser = LDIF_Attribute_Parser(ldifFile)

    primaryLogger.debug("Parsing <%s> for attributes" % filename)
    attrParser._parse()

    ldifFile.close()
    primaryLogger.debug("Closed file <%s>" % filename)

    return attrParser._attrs

def generateCSV(attrs, inputFileName, output, fieldSeparater, textDelimiter):
    ldifFile = open(inputFileName, "rb")

    primaryLogger.debug("Opened <%s> for reading" % inputFileName)

    for attr in attrs:
        output.write((textDelimiter + attr + textDelimiter + fieldSeparater))
    output.write("\n")

    primaryLogger.debug("Write headers")

    csvParser = LDIF_CSV_Parser(ldifFile, attrs, output, fieldSeparater, textDelimiter)
    primaryLogger.debug("Paring values")
    csvParser._parse()
    primaryLogger.debug("Paring done")

    ldifFile.close()
    primaryLogger.debug("Closed file <%s>" % inputFileName)

    output.write("\n")


if __name__ == "__main__":
    inputFile = "../resource/origin.ldf"
    outputFile = "../resource/origin.csv"
    fieldSeparater = ","
    textDelimiter = "\""

    setupLogging()

    primaryLogger.debug("outputFile: %s" % outputFile)
    primaryLogger.debug("fieldSeparater: %s" % fieldSeparater)
    primaryLogger.debug("textDelimiter: %s" % textDelimiter)

    attrs = parseAttrs(inputFile)
    
    primaryLogger.debug("Attributes: " + repr(attrs))

    try:
        output = open(outputFile, "w")
    except:
        raise "Can't open <%s> file" % (outputFile)
    else:
        generateCSV(attrs, inputFile, output, fieldSeparater, textDelimiter)
