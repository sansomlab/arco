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
import logging
import sys

import arco.templates as templates
from arco.functions import *


def main():

    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

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

    logging.info("Initialising HUGO site")

    # create and configure a new HUGO site
    initialise_hugo_website(outdir,
                            args.theme, args.modifications,
                            recipe, templates.config)

    # ####################################################################### #
    # ######################## Compile the pages ############################ #
    # ####################################################################### #

    # write the top level _index.md
    page_vars = {"title": recipe["report"]["def"]["title"],
                 "contents": recipe["report"]["def"]["contents"],
                 "weight": 1,
                 }

    write_file(os.path.join(outdir, "content", "_index.md"),
               templates.index, page_vars)

    # write the sections and section pages
    logging.info("Linking in the contents")

    section_weight = 1

    sections = [x for x in recipe["report"].keys() if x != "def"]

    for section in sections:

        _section = recipe["report"][section]
        _section["def"]["weight"] = section_weight
        _section["def"]["id"] = section

        # Recursively parse the section.
        parse_section(_section, args.indir,
                      os.path.join(outdir,"content"))

        section_weight += 1



if __name__ == "__main__":
    main()
