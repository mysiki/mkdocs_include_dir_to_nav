import os
import logging
import json
import yaml
import re

from mkdocs.structure.files import File
from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options
import mkdocs.structure.nav as nav

log = logging.getLogger('mkdocs')

class IncludeDirToNav(BasePlugin):

    config_scheme = (
        ("flat", config_options.Type(bool, default=False)),
        ("file_pattern", config_options.Type(str, default='.*\.md$')),
        ("file_name_as_title", config_options.Type(bool, default=True)),
        ("recurse", config_options.Type(bool, default=True)),
        ("sort_file", config_options.Type(bool, default=True)),
        ("sort_directory", config_options.Type(bool, default=True)),
        ("reverse_sort_file", config_options.Type(bool, default=False)),
        ("reverse_sort_directory", config_options.Type(bool, default=False)),
        ("include_empty_dir", config_options.Type(bool, default=False)),
    )

    def on_files(self, files, config):

        if config["nav"]:
            log.debug(f"IncludeDirToNav : ## Original NAV : \n{yaml.dump(config['nav'], indent=2)}##")
            parse(
                ori_nav=config["nav"],
                config=config,
                pattern=self.config['file_pattern'],
                flat=self.config['flat'],
                file_name_as_title=self.config['file_name_as_title'],
                reverse_sort_directory=self.config['reverse_sort_directory'],
                reverse_sort_file=self.config['reverse_sort_file'],
                sort_file=self.config['sort_file'],
                sort_directory=self.config['sort_directory'],
                include_empty_dir=self.config['include_empty_dir']
            )
            log.debug(f"IncludeDirToNav : ## Final NAV : \n{yaml.dump(config['nav'], indent=2)}##")

### Loop over ori_nav in order to find PagePath
#### When found, check if pagePath is folder
#### If Yes, get direct files and direct directory, and insert it to nav
#### If direct directory was finding, recall parse with current index, in order to subCheck needsted folder
#### Take care of direct notation ( - myFolder ) and page title notation ( - my folder : myFolder)
def parse(ori_nav,config, pattern: str = '.*\.md$', flat: bool = False, previous=None, file_name_as_title: bool=False, recurse: bool=True, reverse_sort_file: bool=False, reverse_sort_directory: bool=False, sort_file: bool=True, sort_directory: bool=True, include_empty_dir: bool=False):
    log.debug("IncludeDirToNav : ##START Parse state###")
    log.debug(f"IncludeDirToNav : ori_nav = {ori_nav} | previous = {previous} | type of ori_nav {type(ori_nav)}")

    ## Loop over nav path
    if isinstance(ori_nav, dict) or isinstance(ori_nav, list):
        for index, item in enumerate(ori_nav):
            ## If dict, value like { - 'pageName' : 'pagePath' }
            if isinstance(item, dict):
                log.debug(f"  IncludeDirToNav : Item in loop is dict. Item = {item}")
                ## Item hav only 1 value by mkdocs design, how but loop over ...
                for k in item:
                    ## If item value is List, value like { - 'pageName' : ['pagePath01', 'pagePath02' ...] }
                    ### Need to nested loop
                    if isinstance(item[k], list):
                        log.debug(f"    IncludeDirToNav : Item is List, recall parse. Item = {item[k]}")
                        parse(
                            ori_nav=item[k],
                            config=config,
                            pattern=pattern,
                            flat=flat,
                            previous=item,
                            file_name_as_title=file_name_as_title,
                            recurse=recurse,
                            reverse_sort_directory=reverse_sort_directory,
                            reverse_sort_file=reverse_sort_file,
                            sort_file=sort_file,
                            sort_directory=sort_directory,
                            include_empty_dir=include_empty_dir
                        )

                    ## Else, item is simple dict, aka, value is string
                    else:
                        current_item = os.path.join(config["docs_dir"], item[k])
                        log.debug(f"    IncludeDirToNav : check current item : {current_item}")
                        to_add, directory_was_insered = _generate_nav(current_item, pattern, config, flat, file_name_as_title, recurse, reverse_sort_file, reverse_sort_directory, sort_file, sort_directory, include_empty_dir)
                        if to_add:
                            item.update({k: to_add})
                            if directory_was_insered:
                                parse(
                                    ori_nav=item[k],
                                    config=config,
                                    pattern=pattern,
                                    flat=flat,
                                    previous=item,
                                    file_name_as_title=file_name_as_title,
                                    recurse=recurse,
                                    reverse_sort_directory=reverse_sort_directory,
                                    reverse_sort_file=reverse_sort_file,
                                    sort_file=sort_file,
                                    sort_directory=sort_directory,
                                    include_empty_dir=include_empty_dir
                                )
            ## Else if item is no named, value like { - 'pagePath' }
            elif isinstance(item, str):
                log.debug(f"  IncludeDirToNav : Item in loop is string. Item = {item}")
                current_item = os.path.join(config["docs_dir"], item)
                to_add, directory_was_insered = _generate_nav(current_item, pattern, config, flat, file_name_as_title, recurse, reverse_sort_file, reverse_sort_directory, sort_file, sort_directory, include_empty_dir)
                if to_add:
                    # Replace current index by object in order to avoir infinite loop
                    ori_nav[index] = to_add.pop(-1)
                    ## Now, index position is an object, so insert new value
                    for insert_index, insert in enumerate(to_add):
                        ori_nav.insert(index + insert_index, insert)
                    if directory_was_insered:
                        parse(
                            # ori_nav=ori_nav[index],
                            ori_nav=ori_nav,
                            config=config,
                            pattern=pattern,
                            flat=flat,
                            previous=ori_nav[index],
                            file_name_as_title=file_name_as_title,
                            recurse=recurse,
                            reverse_sort_directory=reverse_sort_directory,
                            reverse_sort_file=reverse_sort_file,
                            sort_file=sort_file,
                            sort_directory=sort_directory,
                            include_empty_dir=include_empty_dir
                            )

def _generate_nav(current_item: str, pattern: str, config, flat, file_name_as_title, recurse, reverse_sort_file, reverse_sort_directory, sort_file, sort_directory, include_empty_dir: bool):
    ## Init var
    directory_was_insered = False
    to_add = []

    ## Check if value is directory
    if os.path.isdir(current_item):
        log.debug(f"IncludeDirToNav_generate_nav : Current item is dir ({current_item})")

        ## Get all direct files and direct folder
        ## r=root, d=directories, f = files
        for r, d, f in os.walk(current_item):
            ## For each file, check if pattern is respected
            for file in (sorted(f, reverse=reverse_sort_file) if sort_file else f):
                if re.match(pattern, file):
                    ## Add it to temp var
                    rpath = os.path.relpath(os.path.os.path.join(r, file), config["docs_dir"] )
                    if file_name_as_title:
                        to_add.append(rpath)
                    else:
                        to_add.append({ os.path.splitext(os.path.basename(file))[0] : rpath })

            ## If flat, add direct reference to directory, and recall parse for make the job (creation full path)
            ## Else, continue loop to all level
            ## Work because first walk loop return all direct file and direct directory
            if not flat and d and recurse:
                for sd in (sorted(d, reverse=reverse_sort_directory) if sort_directory else d):
                    ## Check if subdir have file to add in order to not add empty dir
                    rpath = os.path.relpath(os.path.os.path.join(r, sd), config["docs_dir"] )
                    if include_empty_dir or _check_subitem(os.path.join(config["docs_dir"], rpath), pattern):
                        directory_was_insered = True
                        to_add.append({sd : rpath })
                        log.debug(f"IncludeDirToNav_generate_nav : adding dir (sd : {sd}, rpath: {rpath})")
                break
            elif not recurse:
                break

    return to_add, directory_was_insered

def _check_subitem(item_to_check: str, pattern: str):
    log.debug(f"IncludeDirToNav_generate_nav : _check_subitem ({item_to_check})")
    for filename in os.listdir(item_to_check):
        f = os.path.join(item_to_check,filename)
        if os.path.isfile(f) and re.match(pattern, filename):
            log.debug(f"IncludeDirToNav_generate_nav : Dir have concerned subfile ({item_to_check})")
            return True
    log.debug(f"IncludeDirToNav_generate_nav : Dir not have subfile, do not add it ({item_to_check})")
    return False