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
    )

    def on_files(self, files, config):

        if config["nav"]:
            log.debug(f"IncludeDirToNav : ## Original NAV : \n{yaml.dump(config['nav'], indent=2)}##")
            parse(
                ori_nav=config["nav"],
                config=config,
                pattern=self.config['file_pattern'],
                flat=self.config['flat'],
                file_name_as_title=self.config['file_name_as_title']
            )
            log.debug(f"IncludeDirToNav : ## Final NAV : \n{yaml.dump(config['nav'], indent=2)}##")

### Loop over ori_nav in order to find PagePath
#### When found, check if pagePath is folder
#### If Yes, get direct files and direct directory, and insert it to nav
#### If direct directory was finding, recall parse with current index, in order to subCheck needsted folder
#### Take care of direct notation ( - myFolder ) and page title notation ( - my folder : myFolder)
def parse(ori_nav,config, pattern: str = '.*\.md$', flat: bool = False, previous=None, file_name_as_title=False):
    log.debug("IncludeDirToNav : ##State in parse###")
    log.debug(f"IncludeDirToNav : ori_nav = {ori_nav} | previous = {previous}")
    log.debug("IncludeDirToNav : ##State end###")

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
                            file_name_as_title=file_name_as_title
                        )

                    ## Else, item is simple dict, aka, value is string
                    else:
                        current_item = os.path.join(config["docs_dir"], item[k])
                        log.debug(f"    IncludeDirToNav : check current item : {current_item}")
                        to_add, directory_was_insered = _generate_nav(current_item, pattern, config, flat, file_name_as_title)
                        if to_add:
                            item.update({k: to_add})
                            if directory_was_insered:
                                parse(
                                    ori_nav=item[k],
                                    config=config,
                                    pattern=pattern,
                                    flat=flat,
                                    previous=item,
                                    file_name_as_title=file_name_as_title
                                )
            ## Else if item is no named, value like { - 'pagePath' }
            elif isinstance(item, str):
                log.debug(f"  IncludeDirToNav : Item in loop is string. Item = {item}")
                current_item = os.path.join(config["docs_dir"], item)
                to_add, directory_was_insered = _generate_nav(current_item, pattern, config, flat, file_name_as_title)
                if to_add:
                    ## Item is string, so need to replace it by object (and canno't use append or update)
                    ### Previous permit to keep parent reference in order to replace item string by new object at the same index
                    ### If no previous, item is in root of Nav.
                    log.debug(f"    IncludeDirToNav : Previous when adding new page : {previous}")
                    if previous:
                        ## Item hav only 1 value by mkdocs design, how but loop over ...
                        for k in previous:
                            previous.update({k: to_add})
                            if directory_was_insered:
                                parse(
                                    ori_nav==previous[k],
                                    config=config,
                                    pattern=pattern,
                                    flat=flat,
                                    previous=previous[k],
                                    file_name_as_title=file_name_as_title
                                )
                    else:
                        # Replace current index by object in order to avoir infinite loop
                        ori_nav[index] = to_add.pop(-1)
                        ## Now, index position is an object, so insert new value
                        for insert_index, insert in enumerate(to_add):
                            ori_nav.insert(index + insert_index, insert)

                        if directory_was_insered:
                            parse(
                                ori_nav==ori_nav[index],
                                config=config,
                                pattern=pattern,
                                flat=flat,
                                previous=ori_nav[index],
                                file_name_as_title=file_name_as_title
                                )


    ## Else if item is no named, value like { - 'pagePath' }
    elif isinstance(ori_nav, str):
        log.debug(f"IncludeDirToNav : Item is string. Item = {item}")
        current_item = os.path.join(config["docs_dir"], item)
        to_add, directory_was_insered = _generate_nav(current_item, pattern, config, flat, file_name_as_title)
        if to_add:
            ## Item is string, so need to replace it by object (and canno't use append or update)
            ### Previous permit to keep parent reference in order to replace item string by new object at the same index
            ### If no previous, item is in root of Nav.
            log.debug(f"IncludeDirToNav : Previous when adding new page : {previous}")
            # if previous:
            #     ## Item hav only 1 value by mkdocs design, how but loop over ...
            #     for k in previous:
            #         previous.update({k: to_add})
            #         if directory_was_insered:
            #             parse(
            #                 ori_nav=previous[k],
            #                 config=config,
            #                 pattern=pattern,
            #                 flat=flat,
            #                 previous=previous[k],
            #                 file_name_as_title=file_name_as_title
            #             )
            # else:
                ## Replace current index by object in order to avoir infinite loop
            ori_nav[previous] = to_add.pop(-1)
            ## Now, index position is an object, so insert new value
            for insert_index, insert in enumerate(to_add):
                ori_nav.insert(previous + insert_index, insert)

            if directory_was_insered:
                parse(
                    ori_nav=ori_nav[previous],
                    config=config,
                    pattern=pattern,
                    flat=flat,
                    previous=previous,
                    file_name_as_title=file_name_as_title
                    )

def _generate_nav(current_item: str, pattern: str, config, flat, file_name_as_title):
    ## Init var
    directory_was_insered = False
    to_add = []

    ## Check if value is directory
    if os.path.isdir(current_item):
        log.debug(f"IncludeDirToNav_generate_nav : Current item is dir")

        ## Get all direct files and direct folder
        ## r=root, d=directories, f = files
        for r, d, f in os.walk(current_item):
            ## For each file, check if pattern is respected
            for file in f:
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
            if not flat and d:
                directory_was_insered = True
                for sd in d:
                    rpath = os.path.relpath(os.path.os.path.join(r, sd), config["docs_dir"] )
                    to_add.append({sd : rpath })
                break

    return to_add, directory_was_insered
