# Webers

Webers is a small tool that lets you use components in html.
Webers also lets you script with python that will be run in compile time.
This lets you search files, create lists and so on which deletes lots of hard"coding".


## EXAMPLES

### Component system
Parent component
```html
<div class="flex w-screen h-screen bg-blue-200 flex-col items-center gap-2 justify-center" >
    <h>Search</h>
    <Searchbar placeholder="Search" mode="dark" ></Searchbar>
</div>
```

This is a new file named Searchbar.html
When the parent components is compiled webers is going to replac the
`<Searchbar placeholder="Search" mode="dark" ></Searchbar>` with the contents of the file named after the Component name (Searchbar).
```html
<div class="searchbar input1 $mode">
    <input  type="text" placeholder=$placeholder ></input>
</div>
```
Compiled parent
```html
<div class="flex w-screen h-screen bg-blue-200 flex-col items-center gap-2 justify-center" >
    <h>Search</h>
    <div class="searchbar input1 dark">
        <input  type="text" placeholder="Search"" ></input>
    </div>
</div>
```

### Python scripting
Webers also lets you script with python inside your html.
First you define the python script in the top of the file with the `${}$` as blocks.
you can under define the html and access python members. 
```html
${
list_of_hello = ""
for i in range(10):
    list_of_hello += f"<h1>Hello this is a test page ${i}$</h1>"


}$
<div>
    <h1>This is a example of the power of Webers</h1>
    ${list_of_hello}$
</div>
```
#### How it works
Everthing under the python block will become  this
```python
out = f"""
<div>
    <h1>This is a example of the power of Webers</h1>
    {list_of_hello}
</div>
"""
```
which becomes
```html
<div>
    <h1>This is a example of the power of Webers</h1>
    <h1>Hello this is a test page 0</h1>
    <h1>Hello this is a test page 1</h1>
    <h1>Hello this is a test page 2</h1>
    <h1>Hello this is a test page 3</h1>
    <h1>Hello this is a test page 4</h1>
    <h1>Hello this is a test page 5</h1>
    <h1>Hello this is a test page 6</h1>
    <h1>Hello this is a test page 7</h1>
    <h1>Hello this is a test page 8</h1>
    <h1>Hello this is a test page 9</h1>
</div>
and when we then excecute the python the out variable will have the value of asd.
We then go on and check for components and output.
