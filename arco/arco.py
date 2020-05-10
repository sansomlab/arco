'''
arco - automatic report compiler
=================================

Arco is a tool for automatically compiling a web report from
a given set of html documents (such as those produced from
rmarkdown or jupytr notebook files).

Arco builds the web report according to a recipe specified in a yaml file.

Arco recipies can include globs to match arbitrary sets of prexisting
documents.

Currently, arco is only tested with rmd html files and the HUGO theme "Learn".

* For knitr compiled rmd html files, arco will automatically link in "fig.dir"
  and page_file folders if they exist in the same directory as the html
  document.

'''


from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import yaml
import os
import shutil
import glob

import arco.templates as templates
from arco.functions import *


def main():

    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument("-i", "--indir", dest="indir", default=".",
                        help="the directory containing the source files")
    parser.add_argument("-r", "--recipe", dest="recipe", default="report.yml",
                        help="the recipe for the report (a yaml file)")
    parser.add_argument("-o", "--outdir", dest="outdir", default="report.dir",
                        help="the outdir for the report"),
    parser.add_argument("-t", "--theme", dest="theme",
                        help="gzipped file containing the hugo theme")
    parser.add_argument("-m", "--modifications", dest="modifications",
                        default=None,
                        help="directory containing theme modifications"),
    parser.add_argument("--overwrite", dest="overwrite", action="store_true",
                        help="if set, an existant outdir will be deleted")

    args = parser.parse_args()

    # ####################################################################### #
    # ##################### Initialise the HUGO report ###################### #
    # ####################################################################### #

    # read in the report recipe
    with open(args.recipe, "r") as stream:
        recipe = yaml.load(stream, Loader=yaml.FullLoader)

    # make the report folder if it doesn't exist
    outdir = args.outdir

    if os.path.exists(outdir):
        if args.overwrite:
            shutil.rmtree(outdir)
            os.mkdir(outdir)
        else:
            raise(ValueError("Report already exists and overwrite is False"))
    else:
        os.mkdir(outdir)

    # create and configure a new HUGO site
    initialise_hugo_website(outdir,
                            args.theme, args.modifications,
                            recipe, templates.config)

    # ####################################################################### #
    # ######################## Compile the pages ############################ #
    # ####################################################################### #

    # write the top level _index.md
    page_vars = {"title": recipe["report"]["title"],
                 "contents": recipe["report"]["contents"],
                 "weight": 1,
                 }

    write_file(os.path.join(outdir, "content", "_index.md"),
               templates.index, page_vars)

    # write the sections and section pages

    section_weight = 1

    for section, pages in recipe["report"]["sections"].items():

        _section = recipe["report"]["sections"][section]

        _section["weight"] = section_weight

        section_folder = _section["source_folder"]

        make_section(_section, templates.index, outdir)

        if section_folder.startswith("*"):

            folders = glob.glob(section_folder)
            _folder_section = _section.copy()

            folder_section_weight = 1

            for folder in folders:

                prefix = folder.replace(section_folder[1:], "")

                _folder_section["source_folder"] = folder
                _folder_section["target_folder"] = os.path.join(
                    _section["target_folder"], prefix)
                _folder_section["title"] = prefix
                _folder_section["contents"] = ""
                _folder_section["weight"] = folder_section_weight

                make_section(_folder_section, templates.index, outdir)
                make_section_pages(_folder_section, templates.page, outdir)

                folder_section_weight += 1
        else:
            _section["weight"] = 1

            make_section_pages(_section, templates.page, outdir)

        section_weight += 1


if __name__ == "__main__":
    main()
