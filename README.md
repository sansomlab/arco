Arco is a tool for automatically compiling web reports from given sets
of html documents (such as those produced from rmarkdown or jupytr
notebook files).

Arco uses [HUGO](https://gohugo.io/) to build web reports according to
recipes specified in a yaml files.

Currently, arco is only tested with rmd html files and the [HUGO theme "Learn"](https://themes.gohugo.io/hugo-theme-learn/).

**Features:**

* Arco recipies can include globs to match arbitrary sets of prexisting
documents (currently only supported in section definitions).

* For knitr compiled rmd html files, arco will automatically link in "fig.dir"
  and page_file folders if they exist in the same directory as the html
  document.

**Installation**

To use arco clone this repository and install with pip:

```
pip install arco
```