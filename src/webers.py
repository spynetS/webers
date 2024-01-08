from html.parser import HTMLParser
import os
from bs4 import BeautifulSoup as bs

components = ["card"]

def remove_front_spaces(html):
    return '\n'.join(line.lstrip() for line in html.split('\n'))

class Component:
    def __init__(self, name="", srcpath="", definition="", end_definition=""):
        self.name = name
        self.srcpath = srcpath
        self.props = []
        self.definition = definition
        self.end_definition = end_definition
        self.start = 0
        self.end = 0

    def get_child(self):
        asd = ""
        for name, value in self.props:
            if name == "child":
                if value is not None:
                    asd += value
        return asd

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

    def compile(self):
        content = get_content(self.srcpath)
        for name, value in self.props:
            content = content.replace("$" + name, value)
        web = Webers()
        return web.compile(content=content)

def get_content(file):
    with open(file, "r") as f:
        return remove_front_spaces(bs(f.read(), features="html.parser").prettify())

class Webers(HTMLParser):
    def __init__(self, srcpath="./", output="./out"):
        self.srcpath = srcpath
        self.output = output
        self.components = []
        self.current_compile = ""

        self.fetch_project_components()  # all components in the project

        self.current_components = []
        self.finished_components = []

        super().__init__()

    def get_string_from_file(self, content, x, y):
        lines = content.split("\n")
        count = 0
        for line in lines:
            count += 1
            if count == y:
                return line
        raise Exception(f"Definition not found {y}")

    def handle_starttag(self, tag, attrs):
        (y, x) = self.getpos()

        definition = self.get_string_from_file(self.current_compile, x, y)
        start = y

        for comp in self.current_components:
            comp.add_child_data(definition)

        for project_comps in self.components:
            if project_comps.name.lower() == tag.lower():
                comp = Component()
                comp.name = tag
                comp.start = start
                comp.srcpath = project_comps.srcpath
                comp.props = attrs
                comp.definition = definition
                self.current_components.append(comp)

    def handle_endtag(self, tag):
        (y, x) = self.getpos()
        end_definition = self.get_string_from_file(self.current_compile, x, y)
        end = y

        if len(self.current_components) > 0:
            if self.current_components[-1].name == tag:
                comp = self.current_components.pop()
                comp.end = end
                comp.set_end_definition(end_definition)
                self.finished_components.append(comp)

        for comp in self.current_components:
            comp.add_child_data(end_definition)

    def handle_data(self, data):
        for comp in self.current_components:
            comp.add_child_data(data)

    def fetch_project_components(self):
        f = []
        for path, subdirs, files in os.walk(self.srcpath):
            for name in files:
                if ".html" in name and name not in self.current_compile:
                    f.append(Component(name=name.replace(".html", ""),
                                       srcpath=os.path.join(path, name)))
        self.components = f

    def compile(self, file="", content=""):
        if content == "":
            cont = get_content(file)
        else:
            cont = content

        self.current_compile = cont
        self.feed(cont)


        html_without_spaces = remove_front_spaces(cont)

        for comp in reversed(self.finished_components):
            html_without_spaces = remove_front_spaces(
                html_without_spaces.replace(
                    remove_front_spaces(comp.get_string()),
                    remove_front_spaces(comp.compile())
                )
            )

        return bs(html_without_spaces, features="html.parser").prettify()

parser = Webers()
print(parser.compile("./test/index.html"))
