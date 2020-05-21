import os
import shutil
from pathlib import Path
import tarfile
import textwrap
import pkg_resources
import glob
import copy
import logging

import arco.templates as templates

# ########################################################################### #
# ########################## Functions ###################################### #
# ########################################################################### #


def initialise_hugo_website(outdir,
                            theme_tar_file,
                            theme_modifications,
                            config,
                            config_template):
    '''create and configure a new hugo website'''

    # initiate the site
    os.system("hugo new site " + outdir)

    # copy the theme across
    theme_dir = os.path.join(outdir, "themes")

    if not os.path.exists(theme_dir):
        os.mkdir(theme_dir)

    with tarfile.open(theme_tar_file) as tar:
        tar.extractall(path=theme_dir)

    theme_name = os.path.basename(theme_tar_file)[:-len(".tar.gz")]

    os.system('echo theme = \\"' + theme_name + '\\" >>' +
              os.path.join(outdir, "config.toml"))

    if theme_modifications is not None:

        # copy over theme modifications
        mod_dirs = next(os.walk(theme_modifications))[1]

        for mod_dir in mod_dirs:

            target_dir = os.path.join(outdir, mod_dir)

            os.rmdir(target_dir)

            # add the custom layout files
            shutil.copytree(os.path.join(theme_modifications, mod_dir),
                            target_dir)

    # add the shortcodes
    shortcode_dir = os.path.join(outdir, "layouts", "shortcodes")

    if not os.path.exists(shortcode_dir):
        os.mkdir(shortcode_dir)

    pkg_shortcode_path = pkg_resources.resource_filename('arco', 'shortcodes')

    for shortcode_file in glob.glob(os.path.join(
            pkg_shortcode_path, "*.html")):
        shutil.copy(shortcode_file, shortcode_dir)

    # write the config.toml file
    config["theme_name"] = theme_name

    write_file(os.path.join(outdir, "config.toml"),
               config_template, config)


def write_file(file_name, template, vars_dict):
    '''fill and write a hugo page template'''

    contents = template % vars_dict

    with open(file_name, "w") as fh:
        fh.write(textwrap.dedent(contents))


def make_section(section_definition, index_template, outdir):
    '''make a section (content subfolder) of hugo website'''

    sec_def = section_definition

    target_dir =os.path.join(outdir, sec_def["target"])
    if not os.path.exists(target_dir):
        os.mkdir(target_dir)

    page_vars = {"title": os.path.basename(sec_def["target"]),
                 "contents": sec_def["contents"],
                 "weight": sec_def["weight"]}

    page_file = os.path.join(outdir,
                            sec_def["target"],
                             "_index.md")

    if not os.path.exists(page_file):

        write_file(page_file,
                   index_template, page_vars)

    else:
        raise ValueError("Page file already exists")


def make_pages(section_definition,
               indir,
               page_template,
               target_folder):
    '''make a section (content subfolder) pages of hugo website'''

    sec_def = section_definition

    page_weight = 1

    for page_name, page_file in sec_def["pages"].items():

        ## support globbing for pages... (untested!)

        page_source_path = os.path.join(indir, sec_def["source"])



        if page_file.startswith("*."):

            glob_path = os.path.join(page_source_path, page_file)

            globbed_pages = glob.glob(glob_path)

            globbing = True

            source_path_len = len(Path(page_source_path).parts)

            pages = [ os.path.join(Path(x).parts[source_path_len:])
                      for x in globbed_paths ]

        else:
            globbing = False
            pages = [ page_file ]

        for page in pages:

            logging.info("Processing page: " + page)

            target_path = os.path.join(target_folder,
                                       page)

            # check that the parent directory exists.
            target_path_dir = os.path.dirname(target_path)

            if not os.path.exists(target_path_dir):
                os.mkdir(target_path_dir)

            page_abspath = os.path.abspath(
                os.path.join(page_source_path, page))

            if not os.path.exists(page_abspath):

                logging.warn(
                    "source page does not exist: " +\
                    page_abspath)

                continue

            os.symlink(page_abspath,
                           target_path)

            # Support for RMD files.

            # link in "fig.dir" if it exists.
            source_fig_dir = os.path.join(os.path.dirname(page_abspath),
                                          "fig.dir")

            target_fig_dir = os.path.join(target_path_dir, "fig.dir")

            if os.path.exists(source_fig_dir):

                if not os.path.exists(target_fig_dir):
                    os.symlink(os.path.abspath(source_fig_dir),
                           target_fig_dir)
                else:
                    logging.warn("not linking in fig dir "
                                  "because a link already exists")


            # link in associated files (i.e. javascript libraries)
            page_files = page_abspath.replace(".html", "_files")

            if os.path.exists(page_files):
                os.symlink(os.path.abspath(page_files),
                           os.path.join(target_folder,
                                        page.replace(".html", "_files")))

            if globbing:
                page_basename = os.path.basename(page)

            else:
                page_basename = page_name + ".html"

            markdown_file = os.path.join(target_folder,
                                         page_basename.replace(".html", "_x.md"))

            page_vars = {"title": page_name,
                         "html_file_path": page,
                         "weight": page_weight}

            write_file(markdown_file, page_template, page_vars)

            page_weight += 1

    return page_weight

def parse_section(section, indir, outdir):

    logging.info("Parsing report section: " +\
                 section["def"]["id"])


    # Check the section is defined
    if "def" not in section.keys():
        raise ValueError("Section definition missing")

    # Check the source folder is defined
    if "source" not in section["def"].keys():
        raise ValueError("Section source not defined")

    source = section["def"]["source"]

    # establish the full relative path to
    # the source files
    if indir == ".":
        source_path = source
    else:
        if source == ".":
            source_path = indir
        else:
            source_path = os.path.join(indir, source)

    if os.path.basename(source).startswith("*"):

        folders = [x for x in glob.glob(source_path)]
        globbing = True

    else:
        folders = [ source_path ]
        globbing = False

    if "target" not in section["def"].keys():
        raise ValueError("Section target folder not defined")

    else:
        target = section["def"]["target"]


    if not globbing:

        if "title" not in section["def"].keys():
            raise ValueError("Section title not defined")

        title = section["def"]["title"]

        if "content" in section["def"].keys():
            contents = section["def"]["contents"]

        else:
            contents = ""


    glob_weight = 1

    if len(folders) == 0:
        return

    for source_folder in folders:

        source_folder_name = os.path.basename(source_folder)

        _section = copy.deepcopy(section)
        _section["def"]["source"] = source_folder_name

        if globbing:
            prefix = source_folder_name.replace(source[1:], "")

            if _section["def"]["target"] == ".":
                _section["def"]["target"] = prefix

            else:
                _section["def"]["target"] = os.path.join(
                    target, prefix)

            _section["def"]["title"] = prefix

            _section["def"]["contents"] = ""

            _section["def"]["weight"] = glob_weight
            glob_weight += 1

        else:
            _section["def"]["target"] = target

        make_section(_section["def"], templates.index, outdir)

        if "pages" in _section["def"]:

            if _section["def"]["pages"] and _section["def"]["pages"] != "None":

                if _section["def"]["target"] == ".":
                    target_folder = outdir
                else:
                    target_folder = os.path.join(outdir,
                                                 _section["def"]["target"])

                child_weight = make_pages(_section["def"],
                                          indir,
                                          templates.page,
                                          target_folder)

            else:
                child_weight = 1

        else:
            child_weight = 1

        # make child sections
        items = section.keys()

        child_sections = [x for x in items if x != "def"]


        for child in child_sections:

            _child_section = copy.deepcopy(section[child])

            _child_section["def"]["id"] = child
            _child_section["def"]["weight"] = child_weight
            child_weight += 1

            _indir = source_folder

            if _section["def"]["target"] != ".":
                 _outdir = os.path.join(outdir,
                                        _section["def"]["target"])
            else:
                 _outdir = outdir

            parse_section(_child_section,
                          _indir, _outdir)
