
# this script will retrive the definintions made in the begining of a file
# and et the return (the html)
# ---syntax---
# {
# def getButtons(amount):
#     buttons = ""
#     for i in range(amount):
#         buttons += f'<button>Button {i}</button>\n'
#     return buttons
# }

# <body>
#     {getButtons()}
# </body>



# Then it will create a python file with the definition and then
# the html as a string in the f'''[html]''' format
# This will do so the python in the html will execute in the string
# so we get the right output
# In the compule e return the output of that generated script

#def test(name):
#    tes=""
#    for i in range(1):
#        tes += f"""
#            <h2>Hello {name}  {i}</h2>
#        """
#    return tes
#out = f"""
# <body>
#     {getButtons()}
# </body>
#"""


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
    
    def replaceBrack(self,text):
        #replace the pytml brackets
        txt = text.replace("${","DOLLARBRACKET").replace("}$","BRACKETDOLLAR")
        #replace the code brackets (not for pytml)
        txt = txt.replace("{","OPENBRACKET").replace("}","CLOSINGBRACKET")
        return txt.replace("DOLLARBRACKET","{").replace("BRACKETDOLLAR","}")


    def getReturn(self,text):
        text = text.replace("{"+self.getDefines(text)+"}","")
        return text

    def toPythonFile(self,text):
        text = self.replaceBrack(text)
        text = self.getDefines(text)+"out =(f'''"+self.getReturn(text)+"''')"
        return text


    def compiles(self,text):
        # to topythonfile will set a out variable to the putput
        # here we return that value
        na = {}
        try:
            exec(self.toPythonFile(text),na)
        except Exception as e:
            print("Python error",e)
        return(na["out"].replace("OPENBRACKET","{").replace("CLOSINGBRACKET","}"))
