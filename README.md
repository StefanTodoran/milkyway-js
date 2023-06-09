<h1>What is Milkway? <img width="30px" height="30px" src="assets/logo.svg"/></h1>

I have long found myself greatly frustrated by the shortcomings of vanilla HTML. One of the most basic concepts of computer science—modularity—is simply non-existant when working the the basic version of this language, a fact that is all the more painful when one recalls that HTML has existed longer than I have been alive.

It truly boggles the mind that in a bare HTML, CSS + JS project one cannot factor out the header into another file without incurring some kind of cost. While in the past I've solved this with a `<script>` tag which replaces itself, all existing solutions are simply unacceptable. One should be able to factor out snippets of HTML to their own files for use elsewhere without breaking the experience for non-JS users, without using an overkill library like React or Vue, and without needing to learn an entirely different preprocessor syntax like Pug.

The goal of MilkywayJS, simply put, is to offer a development experience where you can utilize the benefits of components in your HTML, without any computational overhead. At runtime, your HTML code should look no different than it would had you done things the manual way.

# How it Works

Everything in MilkywayJS is controlled via the `manage.py` administration script. This file handles the TypeScript compiler, CSS minification, `mhtml` + `mcomp` transpilation to `html`, and development vs production builds.

Here is an example of how HTML components work:

<details>
<summary>Sample Input</summary>

index.mhtml
```html
<div><!-- %MLKY FOO bar="baz" --></div>
```

foo.mcomp
```html
<p style="font-size: 16px;">{{ bar }}</p>
```

</details>

<details>
<summary>Sample Ouput</summary>

index.html
```html
<div><p style="font-size: 16px;">baz</p></div>
```

</details><br>

As you can see it is very barebones; this is not React. We are not looking to "be the next web paradigm". We just want to factor out our headers.

# Development Instructions

To get started, clone this repository or click "use this template".

## Project Overview

`assets`<br>
This directory contains the original CSS file and all other assets, such as image, svg, or video files.

`components`<br>
This directory contains all component files, marked by the `.mcomp` extension. These should contain HTML code, and can be inserted into the HTML by using the `<!-- %MLKY {NAME} -->` indicator, where {NAME} is replaced by the component's name, which should match the name of the component file.

`dist`<br>
There should be no reason to make changes to this directory, as it contains the minifed CSS and compiled JavaScript.

`lib`<br>
Do not modify this directory, it is a python package with utils for the various template functions of MilkywayJS.

`page`<br>
This folder contains the uncompiled HTML files of the project, marked by the `.mhtml` file extension. These files can contain component indicators, and will be "compiled" by having these indicators replaced with the appropriate component code.

`src`<br>
Last but not least, the src folder contains all TypeScript files for the project.

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

* Finish build script for manage.py
* Add configuration file, read by manage.py
  * Should include option to configure root directory
* Make components able to be inline with other tags
* Add more basic template HTML, CSS and TS
* Investiage ways of having basic component props?