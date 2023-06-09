# Project Overview

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

# Making Changes

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

This isn't meant to be a web framework. It is merely a useful template for medium sized projects, where the goal is non-trivial but also not complex enough to warrant the large overhead of a JS framework.

## TODO

* Finish build script for manage.py
* Add configuration file, read by manage.py
  * Should include option to configure root directory
* Make components able to be inline with other tags
* Add more basic template HTML, CSS and TS
* Investiage ways of having basic component props?