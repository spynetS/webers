class PyTml:

    def getDefines(self,text):
        depth = []
        code = ""
        text2 = ""
        first = False
        for c in text:
            if len(depth) == 0 and first: break
            if c == "}": depth.pop()
            if len(depth) > 0:
                code += c
            if c == "{": 
                first = True
                depth.append(c)
        return code

    def getReturn(self,text):
        text = text.replace("{"+self.getDefines(text)+"}","")
        return text

    def toPythonFile(self,text):
        return self.getDefines(text)+"out =(f'''"+self.getReturn(text)+"''')"
    

    def compiles(self,text):
        na = {}
        exec(self.toPythonFile(text),na)
        #exec("out = 1",na)
    #print(na["out"])
        return(na["out"])
#print(toPythonFile(open("index.html","r").read()))