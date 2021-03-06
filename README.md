Arco is an **a**utomatic **r**eport **co**mpiler for generating web reports
from given sets of html documents (such as those produced from rmarkdown or
jupyter notebook files).

Arco uses [HUGO](https://gohugo.io/) to build web reports according to
recipes specified in yaml files.

Currently, arco is only tested with rmd html files and the [HUGO theme "Learn"](https://themes.gohugo.io/hugo-theme-learn/).

**Features**

* Arco yaml recipies can include globs to match arbitrary sets of prexisting
pages and documents.

* Arbitrary levels of subsections are supported.

* For knitr compiled rmd html files, arco will automatically link in "fig.dir"
  and "*page*_file" folders if they exist in the same directory as the html
  document.

**Installation**

To use arco clone this repository and install with pip:

```
git clone git@github.com:sansomlab/arco.git
pip install arco
```
