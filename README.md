<h1>What is Milkway? <img width="30px" height="30px" src="assets/logo.svg"/></h1>

I have long found myself greatly frustrated by the shortcomings of vanilla HTML. One of the most basic concepts of computer science—modularity—is simply non-existant when working the the basic version of this language, a fact that is all the more painful when I recall that HTML has existed longer than I have been alive.

It truly boggles the mind that in a bare HTML, CSS + JS project one cannot factor out the header into another file without incurring some kind of cost. While in the past I've solved this with a `<script>` tag which replaces itself, all existing solutions are simply unacceptable. One should be able to factor out snippets of HTML to their own files for use elsewhere without breaking the experience for non-JS users, without using an overkill library like React or Vue, and without needing to learn an entirely different preprocessor syntax like Pug.

The goal of MilkywayJS, simply put, is to offer a development experience where you can utilize the benefits of components in your HTML, without any computational overhead. At runtime, the HTML code you ship to the browser should look no different than it would had you done things the manual way.

# How it Works

Everything in MilkywayJS is controlled via the `manage.py` administration script. This file handles the TypeScript compiler, CSS minification, `mhtml` + `mcomp` transpilation to `html`, and development vs production builds.

Here is an example of how HTML components work:

<details>
<summary>Sample Input</summary>

index.mhtml
```html
<div><!-- %MLKY FOO text="bar" size="16px" --></div>
```

foo.mcomp
```html
<p style="font-size: {{ size }};">{{ text }}</p>
```

</details>

<details>
<summary>Sample Ouput</summary>

index.html
```html
<div><p style="font-size: 16px;">bar</p></div>
```

</details><br>

As you can see it is very barebones; this is not React. We are not looking to "be the next web paradigm". We just want to factor out our headers. Here is a more complex example involving if clauses:

<details>
<summary>Sample Input</summary>

index.mhtml
```html
<h1>An Image Icon</h1>
<!-- %MLKY ICON src="image.png" caption="Hello World" size="25px" -->
```

icon.mcomp
```html
<img src="{{ src }}" style="width: {{ size }}; height: {{ size }};"/>
{[ %if caption ]}<p>{{ caption }}</p>{[ %endif ]}
```

</details>

<details>
<summary>Sample Ouput</summary>

index.html
```html
<h1>An Image Icon</h1>
<img src="image.png" style="width: 25px; height: 25px;"/>
<p>Hello World</p>
```

</details><br>

# Development Instructions

To get started, clone this repository or click "use this template". Then, run the following commands:

```shell
npm i
pip install git+https://github.com/StefanTodoran/web-minify.git@master
```

The web-minify package is a fork of the [css_html_js_minify](https://github.com/juancarlospaco/css-html-js-minify) package. Unfortunately as of the time of writing the css_html_js_minify package hasn't seen an update since 2018, over 5 years ago. It contains a number of bugs which the web-minify package addresses.

## Project Overview

`assets`<br>
This directory contains the all assets, such as image, svg, or video files.

`components`<br>
This directory contains all component files, marked by the `.mcomp` extension. These should contain HTML code, and can be inserted into the HTML by using the `<!-- %MLKY {NAME} -->` indicator, where {NAME} is replaced by the component's name, which should match the name of the some component file.

`dist`<br>
There should be no reason to make changes to this directory, as it contains the minifed CSS and compiled JavaScript.

`lib`<br>
Do not modify this directory, it is a python package with utils for the various template functions of MilkywayJS.

`page`<br>
This folder contains the uncompiled HTML files of the project, marked by the `.mhtml` file extension. These files can contain component indicators, and will be "compiled" by having these indicators replaced with the appropriate component code.

`src`<br>
Last but not least, the src folder contains all TypeScript files for the project and the CSS file.

## Making Changes

MilkywayJS is made with the separation of development and production versions in mind. Once changes are made, push changes to production by running the following command. If using Github Pages, make sure to serve from the `docs` directory.

```
manage.py build
```

## Running Locally

```
manage.py runserver --watch
```
```
manage.py runserver --docs
```

## Keep in Mind

This isn't meant to be a web framework. It is merely a useful template for medium sized projects, where the goal is non-trivial but also not complex enough to warrant the large overhead of a JS framework. It is also not supported by a team, it is merely a tool created for personal use that you may use if you so desire. Bug-free code is not guaranteed!

## TODO

* Factor out minification and typescript transpilation from server to compiler
* Add bare compile option to manage.py script 
* More settings in configuration file, finish implementing existing ones
* Improve the basic template HTML, CSS and TS
* Stress test compiler code for both components and if clauses
* Improve compiler by allowing boolean components to be written as `prop` rather than `prop=""` or `prop="true"`
* Add nested components inside components
