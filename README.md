# mkdocs schema reader plugin

This is a plugin that scans the specified directories and files for JSON Schema files, converts them to markdown and builds them into your documentation.

**Breaking Change**  This version can introduce some breaking change. Markdown output is now wrtie to documentation directory (`${docs_dir/schema}`)instead of `site/schema`. If your documentation was in `site` folder, this will change nothing. Use the new `output` options for control it if needed.

## Setup

Install the plugin using pip:

`pip install mkdocs-schema-reader`

Activate the plugin in `mkdocs.yml`:
```yaml
plugins:
  - search
  - include_dir_to_nav
```

Then, specify folders and files that you want to include in `mkdocs.yml` relative to it's location, like so:
```yaml
plugins:
  - search
  - include_dir_to_nav:
      include:
        - "../JSONSchema/"
        - "../example/directory/schema.json"
```

Specified directories will be scanned for schema json files, so consider specifying individual files for expansive directories.

> **Note:** If you have no `plugins` entry in your config file yet, you'll likely also want to add the `search` plugin. MkDocs enables it by default if there is no `plugins` entry set, but now you have to enable it explicitly.

More information about plugins in the [MkDocs documentation][mkdocs-plugins].

## Usage

Just activate the plugin, specify directories and files in the manner shown above, and it will operate when normal mkdocs commands are used like `mkdocs serve'

## Options

- `auto_nav` : If true, generated markdown from JSON will be add to navigation path. Using `nav` (default `Schema`) entry (bool, default=True)
- `output` : Set export directory for markdown file, directory relative to `docs_dir` (str, default="/schema")
- `nav` : Set the navigation path when JSON schema will be find in web IHM (str, default="Schema"). Can be a complexe path (like /home/json/schema), but, it will not merge if existing path already exist *see note*.
- `example_as_yaml` : Show example as yaml instead of json (bool, default=False)
- `show_example` : Select what example will be show  (str, default='all')
    - `all` : All examples
    - `any` : No example will be show
    - `object` : Only examples present in objects section
    - `propertie` : Only examples present in properties section

> **Notes** About `nav` : Nav path is adding to navigation without merge with existing path. If you want to show schema in existing section (referenced in classic nav), set `auto_nav` to false and refere it by yourself in classic nav.
> Example :
>
> ```yaml
> plugins:
>   - search
>   - include_dir_to_nav:
>       include: ## Relative to mkdocs.yaml file
>         - "documentations/configuration/schemas/my_schema01.json"
>         - "documentations/configuration/schemas/my_schema02.json"
>       auto_nav: false
>       output: "configuration/schemas/docs"
>       example_as_yaml: true
>       show_example: object
> nav:
>   - Home: index.md
>   - Config:
>     - About: configuration/about.md
>     - Schema 01: configuration/schemas/docs/my_schema01.md
>     - Schema 02: configuration/schemas/docs/my_schema02.md
> ```
