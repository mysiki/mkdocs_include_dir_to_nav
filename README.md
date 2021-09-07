# mkdocs include directory to navigation #

How I can include all directory in mkdocs navigation ? Use this plugin 👍

This is a plugin that fetch navigation menu (in mkdocs.yaml) and replace directory by files. Mkdocs, do not expand folder, this do.

Modification are make 'on the fly' during Build ou Serve, your mkdocs.yaml file will not be modified.

Features :

- Scan navigation for replace folder to all sub file
- Recurcive scan into folder
- Accept all classic mkdocs file type (direct reference, reference with title ...)
- Convert sub folder to section
- Options :
    - `flat` : Disable sub folder as section
    - `file_name_as_title` : Usine file name as title instead of let mkdocs detect H1 balise in file
    - `recurse` : disabled nested search in folder
    - `file_pattern` : Regex for select markdown file (default `'.*\.md$'`)

If you need more features, look at [mkdocs-awesome-pages-plugin](https://github.com/lukasgeiter/mkdocs-awesome-pages-plugin>) than seem to make many more think.

## Setup ##

Install the plugin using pip:

`pip install mkdocs-include-dir-to-nav`

## Usage ##

Activate the plugin in `mkdocs.yml`:

```yaml
plugins:
  - search
  - include_dir_to_nav
```

> **Note:** If you have no `plugins` entry in your config file yet, you'll likely also want to add the `search` plugin. MkDocs enables it by default if there is no `plugins` entry set, but now you have to enable it explicitly.

Then, specify folders in your navigation (as always, folder from docs_site path):

```yaml
nav:
  - Home: README.md
  - dirDirectRef
  - SubDirDirectRef/SubDirDirectRefSub
  - emptyDir
  - dirNamed: dirNamed
  - SubDirNamed: SubDirNamed/SubDirNamedSub
  - dirDirectRefUnderMenu:
    - dirDirectRefUnderMenu
    - dirNamedUnderMenu: dirNamedUnderMenu
```

Each navigation path will be scan, if elements is directory, it will be expand and all sub file will be add.

### Options ###

- `flat` : Disable sub folder as section
- `file_name_as_title` : Usine file name as title instead of let mkdocs detect H1 balise in file
- `recurse` : disabled nested search in folder
- `file_pattern` : Regex for select markdown file (default `'.*\.md$'`)

Basic example, for folder :

```shell
docs/
├── README.md
├── dirDirectRef
│   ├── dirDirectRef-page01.md
│   ├── dirDirectRef-page02.md
│   └── dirDirectRefSub
│       ├── dirDirectRefSub-page01.md
│       └── dirDirectRefSub-page02.md
├── dirNamedUnderMenu
│   ├── dirNamedUnderMenu-page01.md
│   ├── dirNamedUnderMenu-page02.md
│   └── dirNamedUnderMenuSub
│       ├── dirNamedUnderMenuSub-page01.md
│       └── dirNamedUnderMenuSub-page02.md
└── emptyDir
```

with mkdocs.yaml base :

```yaml
docs_dir: './docs'

nav:
  - Home: README.md
  - dirDirectRef
  - dirNamed: dirNamed
```

### Without option ####

```yaml
plugins:
  - search
  - include_dir_to_nav:
 ```

Result :

```yaml
- Home: README.md
- dirDirectRef/dirDirectRef-page01.md
- dirDirectRef/dirDirectRef-page02.md
- dirDirectRefSub:
    - dirDirectRef/dirDirectRefSub/dirDirectRefSub-page02.md
    - dirDirectRef/dirDirectRefSub/dirDirectRefSub-page01.md
- dirNamed:
    - dirNamed/dirNamed-page01.md
    - dirNamed/dirNamed-page02.md
    - dirNamedSub:
        - dirNamed/dirNamedSub/dirNamedSub-page01.md
        - dirNamed/dirNamedSub/dirNamedSub-page02.md
```

### file_pattern option ####

```yaml
plugins:
  - search
  - include_dir_to_nav:
      file_pattern: '.*01\.md$'
 ```

Result :

```yaml
- Home: README.md
- dirDirectRef/dirDirectRef-page01.md
- dirDirectRefSub:
    - dirDirectRef/dirDirectRefSub/dirDirectRefSub-page01.md
- dirNamed:
    - dirNamed/dirNamed-page01.md
    - dirNamedSub:
        - dirNamed/dirNamedSub/dirNamedSub-page01.md
```

### recurse option ####

```yaml
plugins:
  - search
  - include_dir_to_nav:
      recurse: false
 ```

Result :

```yaml
- Home: README.md
- dirDirectRef/dirDirectRef-page01.md
- dirDirectRef/dirDirectRef-page02.md
- dirNamed:
    - dirNamed/dirNamed-page01.md
    - dirNamed/dirNamed-page02.md
```

### Flat option ####

```yaml
plugins:
  - search
  - include_dir_to_nav:
      flat: true
 ```

Result :

```yaml
- Home: README.md
- dirDirectRef/dirDirectRef-page01.md
- dirDirectRef/dirDirectRef-page02.md
- dirDirectRef/dirDirectRefSub/dirDirectRefSub-page02.md
- dirDirectRef/dirDirectRefSub/dirDirectRefSub-page01.md
- dirNamed:
    - dirNamed/dirNamed-page01.md
    - dirNamed/dirNamed-page02.md
    - dirNamed/dirNamedSub/dirNamedSub-page01.md
    - dirNamed/dirNamedSub/dirNamedSub-page02.md
```

### file_name_as_title option ####

```yaml
plugins:
  - search
  - include_dir_to_nav:
      file_name_as_title: true
 ```

Result :

```yaml
- Home: README.md
- dirDirectRef-page01: dirDirectRef/dirDirectRef-page01.md
- dirDirectRef-page02: dirDirectRef/dirDirectRef-page02.md
- dirDirectRefSub:
    - dirDirectRefSub-page02: dirDirectRef/dirDirectRefSub/dirDirectRefSub-page02.md
    - dirDirectRefSub-page01: dirDirectRef/dirDirectRefSub/dirDirectRefSub-page01.md
- dirNamed:
    - dirNamed-page01: dirNamed/dirNamed-page01.md
    - dirNamed-page02: dirNamed/dirNamed-page02.md
    - dirNamedSub:
        - dirNamedSub-page01: dirNamed/dirNamedSub/dirNamedSub-page01.md
        - dirNamedSub-page02: dirNamed/dirNamedSub/dirNamedSub-page02.md
```

More 'complexe' example in test folder.

## Contribution ##

Feel free to add issue, arange code and/or make PR

### Tests ###

Find into test folder a basic mkdocs.yaml and sub folder in order to test plugin.

Use `mkdocs build -v` in order to show debug message.

## Personal note ##

It's my first python code, so be indulgent and optimize it if needed ;)