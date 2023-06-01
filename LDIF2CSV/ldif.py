
validChangetypes = ["add", "delete", "modify"]
ignoredAttrs = []

class LDIF_Parser:
    def __init__(self, inputF):
        self._input = inputF
        self._recordCount = 0

    def handle(self, dn, entry):
        pass

    def _stripLineSep(self, s):
        if s[-1:] == "\n" or s[-1:] == b"\n":
            s=s[:-1]
        if s[-1:] == "\r" or s[-1:] == b"\r":
            s=s[:-1]
        while s[:1] == " " or s[:1] == b" ":
            s=s[1:]
        return s

    def _unfoldLDIFLine(self):
        foldedLines = [self._stripLineSep(self._line)]
        self._line = self._input.readline()
        while self._line and (self._line[:1] == b" " or self._line[:1] == " "):
            foldedLines.append(self._stripLineSep(self._line))
            self._line = self._input.readline()

        unfoldedLine = "".join([line.decode("ascii", "replace") for line in foldedLines])
        return unfoldedLine

    def _parseAttrAndVal(self):
        unfoldedLine = self._unfoldLDIFLine()
        while unfoldedLine and unfoldedLine[:1] == "#":
            unfoldedLine = self._unfoldLDIFLine()
        
        if not unfoldedLine or unfoldedLine == "\n" or unfoldedLine == "\r\n":
            return None, None
        try:
            colonPos = unfoldedLine.index(":")
        except ValueError:
            return None, None
        attr = unfoldedLine[:colonPos]
        sepLen = 1
        while colonPos + sepLen < len(unfoldedLine) and \
              (unfoldedLine[colonPos+sepLen] == ":" or \
              unfoldedLine[colonPos+sepLen] == b":" or \
              unfoldedLine[colonPos+sepLen] == " " or \
              unfoldedLine[colonPos+sepLen] == b" "):
            sepLen += 1
        val = unfoldedLine[colonPos+sepLen:].lstrip()
        return attr, val

    def _parse(self):
        self._line = self._input.readline()
        while self._line:
            dn = None
            changetype = None
            entry = {}

            attr, val = self._parseAttrAndVal()
            while attr != None and val != None:
                if attr == "dn":
                    if dn:
                        raise "Two lines starting with dn in one record"
                    dn = val
                elif attr == "version" and dn is None:
                    version = val
                elif attr == "changetype":
                    if not dn:
                        raise "Read changetype before getting valid dn"
                    if changetype:
                        raise "Two lines starting with changetype in one record"
                    if val not in validChangetypes:
                        raise "changetype value %s is invalid" % (repr(val))
                    changetype = val
                elif val != None and attr not in ignoredAttrs:
                    if attr in entry:
                        if val not in entry[attr]:
                            entry[attr].append(val)
                    else:
                        entry[attr] = [val]

                attr, val = self._parseAttrAndVal()
            if entry:
                self.handle(dn, entry)
                self._recordCount += 1
        return
