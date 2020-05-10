Arco is a tool for automatically compiling web reports from given sets
of html documents (such as those produced from rmarkdown or jupytr
notebook files).

Arco builds the web report according to a recipe specified in a yaml file.

Currently, arco is only tested with rmd html files and the HUGO theme "Learn".

Features:

* Arco recipies can include globs to match arbitrary sets of prexisting
documents (currently only supported in section definitions).

* For knitr compiled rmd html files, arco will automatically link in "fig.dir"
  and page_file folders if they exist in the same directory as the html
  document.
