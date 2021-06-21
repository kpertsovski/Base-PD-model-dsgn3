
# Documentation Generation Guide

This README serves as a guide for using the **documentation** commands in mew-cli

___

## Overview
1. [Required tools](#required-tools)
2. [Installation](#installation)
    1. [Install anaconda](#install-anaconda)
    2. [Correct python and pip version](#correct-python-and-pip-version)
    3. [Install pandoc](#install-pandoc)
    4. [Install pandoc-crossref](#install-pandoc-crossref)
    5. [Install pandoc-xnos](#install-pandoc-xnos)
3. [Expected Folder Structure](#expected-folder-structure)
    1. [Overall Structure](#overall-folder-structure-&-config-file-locations)
    2. [About /docs](#about-/docs)
4. [Document Configuration Files](#document-configuration-files)
    1. [Top-Level Config](#top-level-config)
    2. [Low-Level Config](#low-level-config)
5. [Special Syntax](#special-syntax)
    1. [Tables](#tables)
    2. [Images](#images)
    3. [pandoc-crossref syntaxes](#pandoc-crossref-syntaxes)
6. [Troubleshooting](#troubleshooting)
    1. [Common Issues](#common-issues)

___

## Required tools
Your OS must install following tools to generate documentations
1. [pandoc v2.12](https://pandoc.org/installing.html)
2. [pandoc-crossref v0.3.10.0](https://github.com/lierdakil/pandoc-crossref)

## Installation
### Install anaconda

[Anaconda](https://docs.anaconda.com/anaconda/install/linux/) should already be installed on your Platform McKinsey instance, but in the case that it needs to be installed or updated, follow these instructions.

```
# note: this is Anaconda Installation instructions for Ubuntu v18.04 distribution only
# download the anaconda installation shell script
$ curl -O https://repo.anaconda.com/archive/Anaconda3-2020.02-Linux-x86_64.sh

# verify the Data Integrity of the Installer
$ sha256sum Anaconda3-2020.02-Linux-x86_64.sh

# run command install anaconda via the downloaded script, click YES or ENTER if any questions
$ bash Anaconda3-2020.02-Linux-x86_64.sh
```

### Correct python and pip version
After successfully installing Anaconda, python and pip should be available for usage.
Use `python 3.7.3` and `pip 21.1.2` for support installing `DVC v2.0.6`
Ensure you correct Python and Pip version to successfully install DVC v2.0.6

```
// check python and pip version to make sure installing true version
$ python --version
$ python -m pip --version
```

Running following command if you need to upgrade pip version
```
pip install --upgrade pip
```

### Install pandoc

```
$ conda install -c conda-forge pandoc==2.12
$ pandoc --version
```

### Install pandoc-crossref

```
$ conda install -c conda-forge pandoc-crossref==0.3.10.0
$ pandoc-crossref --version
```

Check [pandoc-crossref syntaxes](http://lierdakil.github.io/pandoc-crossref/)

### Install pandoc-xnos

We use pip to install pandoc-xnos. This plugin contains many different individual filters

```
$ pip install pandoc-fignos pandoc-eqnos pandoc-tablenos pandoc-secnos
```

Check [pandoc-xnos supports](https://github.com/tomduck/pandoc-xnos/)

## Expected Folder Structure

### Overall Folder Structure & Config File Locations
This is an example of what the folder structure should look like for a directory in order to generate documentation.

```
mew-cli-working-directory
  |
  +-- /documentation // When store the documentation outputs if in Top-Level Config does not provide "dir_output_path" value
  |
  +-- /models
  |   |
  |   +-- docs.config.yaml // Top-Level Config
  |   +-- /docs
  |   |   |
  |   |   +-- .md files for the Final Document
  |   |   +-- /assets
  |   |       |
  |   |       +-- /images
  |   |       +-- /css
  |   |       +-- /js
  |   |
  |   +-- /Test_Plan_Folder
  |       |
  |       +-- docs.config.yaml // Low-Level Config
  |       +-- /Statistical_Test_Folder
  |           |
  |           +-- /docs
  |               |
  |               +-- .md files for the Test
  |               +-- /assets
  |               |   |
  |               |   +-- Same structure as other assets folders
  |               |
  |               +-- ...other Statistical Test files (data, code, etc)
  |
  +-- /validations
  |   |
  |   +-- docs.config.yaml // Top-Level Config
  |   +-- /docs
  |   |   |
  |   |   +-- .md files for the Final Document
  |   |   +-- /assets
  |   |       |
  |   |       +-- /images
  |   |       +-- /css
  |   |       +-- /js
  |   |
  |   +-- /Test_Plan_Folder
  |       |
  |       +-- docs.config.yaml // Low-Level Config
  |       +-- /Statistical_Test_Folder
  |           |
  |           +-- /docs
  |               |
  |               +-- .md files for the Test
  |               +-- /assets
  |               |   |
  |               |   +-- Same structure as other assets folders
  |               |
  |               +-- ...other Statistical Test files (data, code, etc)
  |
  ...
```


### About /docs
Any `/docs` folder will use the following convention:
```
  |   +-- /docs
  |       |
  |       +-- .md files to be included in the generated document
  |       +-- /assets
  |           +-- /images
  |           +-- /css
  |           +-- /js

```

`/docs` is where the user should store their Markdown files and any corresponding supporting files
- Markdown files that require JSON to display data as a table will should have those JSON files stored here.
- Any files declared in `docs.config.yaml` will be read from the corresponding `/docs` folder.


`/docs/assets` contains folders to store additional files related to the documentation
- `/images` - Contains image files that will be displayed in the documentation
- `/css` - Contains CSS stylesheet files that can be applied to the generated HTML
- `/js` - Contains JavaScript files the user would like to execute within

---

## Document Configuration Files
The document configuration file is named `docs.config.yaml`. The `.yml` file extension is also supported.

There are two types of config files for documentation: `Top-Level` and `Low-Level`
- `Top-Level`:
    - Specifies details for building a single document for a directory (such as `/validations` or `/models`)
    - Collects the documents created by the `Low-Level` configs into a single document for a directory
- `Low-Level`:
    - Specifies details for an individual sub-directory
    - For example, a single Validation Test Plan, or a single Model

### Top-Level Config
```
# Example of /validations or /models that stores top-level config "docs.config.yaml"
toc_depth: 3
dir_output_path: path/to/name-of-documentations-directory
file_name: Validation_Test_Plans_doc
dir_order:
  - Test_Plan_A
  - Test_Plan_B
introduction:
  - header.md
  - table_of_contents.md
conclusion:
  - conclusion_file.md
  - appendix.md
template_metadata:
  title: Top-Level Title
  author: Dev
  date: 08-04-2021
  lang: en-US
  linkReferences: true
  abstract: |
    This is the abstract.

    It consists of two paragraphs.
```

`toc_depth`:
- Specify the number of section levels to include in the table of contents (ToC)
- If not provided, the ToC is not auto generate into exported files

`dir_output_path`:
- The folder path where documentation is created
- If not provided, the `dir_output_path` is `documentation` at root project

`file_name`:
- Name of the HTML / Markdown file which contains all documentation for specified directory
- The above example will create some files `Validation_Test_Plans_doc.md`, `Validation_Test_Plans_doc.html`, `Validation_Test_Plans_doc.docx`, and `Validation_Test_Plans_doc.tex` when running command `mew-cli documentation:create -p validations`
- If not provided, `file_name` defaults to `Validations_documentation` when running command `mew-cli documentation:create -p validations` or `Models_documentation` when running command `mew-cli documentation:create -p models`

`dir_order`:
- Order in which documentation for sub-directories will be displayed

`introduction`:
- List of markdown files to display at the start of the top-level document

`conclusion`:
- List of markdown files to display at the end of the top-level document

`template_metadata`:
- The metadata used for Pandoc Templates export feature
- It should provide in the Top-Level Config

The top-level document created with this config will display its contents in the following order:
1. Contents of `introduction`
2. Contents of `dir_order`
3. Contents of `conclusion`

### Low-Level Config
```
# Example /validations/Test_Plan docs.config.yaml
toc_depth: 3
dir_order:
  - Statistical_Test_1
  - Statistical_Test_2
dir_source: mysource
dir_details:
  Statistical_Test_1:
    file_order:
      - description.md
      - results.md
  Statistical_Test_2:
    ...
template_metadata:
  title: Low-Level Title
  author: Dev
  date: 08-04-2021
  lang: en-US
  linkReferences: true
  abstract: |
    This is the abstract.

    It consists of two paragraphs.
```

`toc_depth`:
- Specify the number of section levels to include in the table of contents (ToC)
- If not provided, the ToC is not auto generate into exported files

`dir_order`:
- Similar to top-level config field
- Order in which documentation for sub-directories will be displayed

`dir_source`:
- Declare the name of directory that stores all Document Files (.md, .json)
- E.g if you specify `dir_source: mysource`, then command will read all files (.md, .json) belong to directory `Statistical_Test_X/mysource`
- If not specified, it will take default name as `docs`

`dir_details`:
- Declares details how to collect documentation together for sub-directories
- `file_order`:
    - Order in which markdown files should be displayed

`template_metadata`:
- The metadata used for Pandoc Templates export feature
- It should provide in the Low-Level Config

---

## Special Syntax

### Tables
JSON files can be inserted into your markdown files using the following syntax:

```
{{table json_file_name.json}}
```

Ensure that the json file exists in the same `/docs` folder as the markdown file using it.

### Images

Image files can be inserted into your markdown files using the following syntax:

```
{{image assets/images/example_image.png}}
```

The image must be stored in the `/assets/images` folder associated with the `/docs` folder your markdown file exists in.

The following image file formats are supported: JPEG, PNG, SVG

### pandoc-crossref syntaxes

We could also refer [pandoc-crossref syntax documentation](http://lierdakil.github.io/pandoc-crossref/) to apply for our documentation

---

## Troubleshooting

### Common Issues
1. Check your `docs.config.yaml` files are located in the correct directory
2. Check that all fields in the `docs.config.yaml` are inserted correctly. For example: `dir-order` rather than `dir_order`
3. Ensure your filepath references are correct
4. Assets are in the correct `/docs/assets` folder
5. Files and directories referenced in `dir_order`, `dir_details` and `file_order` all exist
---

