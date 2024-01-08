from html.parser import HTMLParser
import os
import pathlib
from bs4 import BeautifulSoup as bs
from PyTml import *
from flagser import *

# TODO
# flags
# fix so you can use Button as name??

def log(content,end="\n"):
    global verbose
    if verbose: print(content,end=end)


def remove_front_spaces(html):
    return '\n'.join(line.lstrip() for line in html.split('\n'))

def get_content(file,no_change=False):
    with open(file, "r") as f:
        if no_change:
            return f.read()
        else:
            return remove_front_spaces(bs(f.read(), features="html.parser").prettify())
# read all files in the srcpath and if they conatins .html
# we add them to the componetns list
def fetch_project_components(srcpath):
    f = []
    for path, subdirs, files in os.walk(srcpath):
        for name in files:
            if ".html" in name:
                f.append(Component(name=name.replace(".html", ""),
                                    srcpath=os.path.join(path, name)))
    return f

class Component:
    def __init__(self, name="", srcpath="", definition="", end_definition=""):
        self.name = name #tag name
        self.srcpath = srcpath # its file path
        self.props = [] # all attributes of the components in the defintino
        self.definition = definition # the string defintion
        self.end_definition = end_definition # the string end defintino

    # if there is mutliple child props (preivies there were)
    # we returns them as one here
    def get_child(self):
        asd = ""
        for name, value in self.props:
            if name == "child":
                if value is not None:
                    asd += value
        return asd

    # returns the compoentns whole defintino
    def get_string(self):
        return self.definition + self.get_child() + self.end_definition

    def set_end_definition(self, definition):
        self.end_definition = "" if definition == self.definition else definition

    def add_child_data(self, content):
        for i, (name, value) in enumerate(self.props):
            if name == "child":
                self.props[i] = ("child", value + content)
                return
        self.props.append(("child", content))

    # first we replace all props with the value
    # then we compile the content to check for comnponents in
    # the compeonnts
    # Then return the result
    def compile(self,srcpath):
        log(f"Found {self.name} compiling {self.srcpath}")
        content = get_content(self.srcpath)
        for name, value in self.props:
            content = content.replace("$" + name, value)
        web = Webers(srcpath=srcpath)
        return web.compile(content=content)


class Webers(HTMLParser):
    def __init__(self, srcpath="./", output="./out"):
        self.srcpath = srcpath # path to search for components
        self.output = output # path to output to
        self.components = [] # list of the components found in the project
        self.current_compile = "" # content we are parsing now
        #
        # fetching the components in the project
        self.components = fetch_project_components(self.srcpath)

        # current_components are the ones we have read but not closed
        # and finished_componeonts are the components we have closed
        # (current_components goes to finsihed when they are closed)
        self.current_components = []
        self.finished_components = []

        super().__init__()

    # returns a string from the line number provided
    def get_string_from_file(self, content, x, y):
        lines = content.split("\n")
        count = 0
        for line in lines:
            count += 1
            if count == y:
                return line
        raise Exception(f"Definition not found {y}")

    def handle_starttag(self, tag, attrs):

        #retrive the line of the definition of the component
        (y, x) = self.getpos()
        definition = self.get_string_from_file(self.current_compile, x, y)

        #we add that definition to all previues read components' child property
        for comp in self.current_components:
            comp.add_child_data(definition)

        # we check if the tag is a component in th project
        # if so we set the properties and add it to the read components
        for project_comps in self.components:
            if project_comps.name.lower() == tag.lower():
                comp = Component()
                comp.name = tag
                comp.srcpath = project_comps.srcpath
                comp.props = attrs
                comp.definition = definition
                self.current_components.append(comp)

    def handle_endtag(self, tag):
        # retrive the end line defintion
        (y, x) = self.getpos()
        end_definition = self.get_string_from_file(self.current_compile, x, y)

        # we pop the last component in the current
        # and add it to the finished components
        if len(self.current_components) > 0:
            if self.current_components[-1].name == tag:
                comp = self.current_components.pop()
                comp.set_end_definition(end_definition)
                self.finished_components.append(comp)

        # we add the end defintion to the previues read compoennts
        for comp in self.current_components:
            comp.add_child_data(end_definition)

    def handle_data(self, data):
        # add the data to all rriviues read compoennts
        for comp in self.current_components:
            comp.add_child_data(data)


    # function to compule file
    def compile(self, file="", content=""):
        # we check if user has put in file name or file content
        if content == "":
            cont = get_content(file,no_change=True)
        else:
            cont = content

        #print(cont)
        p = PyTml()
        cont = p.compiles(cont)
        cont = remove_front_spaces(bs(cont,features="html.parser").prettify())
        self.current_compile = cont
        # start the compiler
        self.feed(cont)

        #remove all spaces before to easier replace compoinentsn
        html_without_spaces = remove_front_spaces(cont)

        # we go though all finsished components and replaces
        # the defintions (get_stirng) with the components compiled content
        for comp in reversed(self.finished_components):
            html_without_spaces = remove_front_spaces(
                html_without_spaces.replace(
                    remove_front_spaces(comp.get_string()),
                    remove_front_spaces(comp.compile(self.srcpath))
                )
            )

        return bs(html_without_spaces, features="html.parser").prettify()


# **** USER INTERACTINS **** #

srcpath = "./"
output = "./out/"
verbose = True

# *** SET OPTIONS *** #

def setPath(args):
    global srcpath
    srcpath = args[0]

def setOutput(args):
    global output
    output = args[0]

# *** PROGRAM FUNCTIONS *** #

def output_content(filename,content):
    global output
    if output == "stdout" or output == "STDOUT":
        print(f"--- output of {filename} ---\n",content)
    else:
        # create the path if it does not exist
        outputdir = os.path.dirname(output)
        if not os.path.exists(outputdir):
            pathlib.Path(outputdir).mkdir(parents=True, exist_ok=True)
        # if the output path is a file write to that file
        if os.path.basename(output) :
            name = output#os.path.basename(outpath)
        else:
            name = output+os.path.basename(filename)

        with open(name,"w") as f:
            print(f"compiled correctly. Wrote to {name}\n")
            f.write(bs(content, features="html.parser").prettify())

def compile(args):
    global srcpath
    log(f"srcpath {srcpath}")
    if "all" in args:
        for comp in fetch_project_components(srcpath):
            log(f"comp srcpath {comp.srcpath}")
            parser = Webers(srcpath=srcpath)
            output_content(comp.srcpath,parser.compile(comp.srcpath))
    else:
        for arg in args:
            parser = Webers(srcpath=srcpath)
            output_content(arg,parser.compile(arg))

def start():
    pass

def generate_example():
    pass

settings_manager = FlagManager([
    Flag("-p", "--path", "sets the src path from", setPath),
    Flag("-o", "--output", "sets the out path (if STDOUT/stdout it will print to stdout)", setOutput),
]);

manager = FlagManager([
    Flag("-c", "--compile", "compile a file or all with all keyword (-c all)", compile),
    Flag("start", "--start", "auto compiles", start),
    Flag("generate-example", "generate-example", "creates a exmaple", generate_example),

])
settings_manager.description = """Webers is a compiling tool that lets you use components inside html. With the use of PyTml we can script with python
inside the components aswell. To get a example run `webers generate-example`"""
settings_manager.check()
manager.check()

if len(sys.argv) == 1:
    print ("-h for help")
