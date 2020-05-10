import os
import shutil
from pathlib import Path
import tarfile
import textwrap
import pkg_resources
import glob

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


def make_section(_section, index_template, outdir):
    '''make a section (content subfolder) of hugo website'''

    os.mkdir(os.path.join(outdir, "content", _section["target_folder"]))

    page_vars = {"title": os.path.basename(_section["target_folder"]),
                 "contents": _section["contents"],
                 "weight": _section["weight"]}

    write_file(os.path.join(outdir, "content",
                            _section["target_folder"], "_index.md"),
               index_template, page_vars)


def make_section_pages(_section, page_template, outdir):
    '''make a section (content subfolder) pages of hugo website'''

    page_weight = 1

    for page_name, page_file in _section["pages"].items():

        page_path = os.path.join(_section["source_folder"], page_file)

        source_path_dir = os.path.dirname(page_path)

        target_folder = os.path.join(outdir, "content",
                                     _section["target_folder"])

        target_path = os.path.join(target_folder, page_file)

        # check that the parent directory exists.
        target_path_dir = os.path.dirname(target_path)

        if not os.path.exists(target_path_dir):
            os.mkdir(target_path_dir)

        os.symlink(os.path.abspath(page_path),
                   target_path)

        fig_dir = os.path.join(source_path_dir, "fig.dir")

        if os.path.exists(fig_dir):
            os.symlink(os.path.abspath(fig_dir),
                       os.path.join(target_path_dir, "fig.dir"))

        # link in associated files (i.e. javascript libraries)
        page_files = page_path.replace(".html", "_files")

        if os.path.exists(page_files):
            os.symlink(os.path.abspath(page_files),
                       os.path.join(target_folder,
                                    page_file.replace(".html", "_files")))

        markdown_file = os.path.join(target_folder,
                                     page_file.replace(".html", "_x.md"))

        page_basename = os.path.basename(page_file)

        page_vars = {"title": page_name,
                     "html_file_path": page_basename,
                     "weight": page_weight}

        write_file(markdown_file, page_template, page_vars)

        page_weight += 1
