**Toy example**

To build a report for the following files:

```
wt.sample.dir/overview.html
wt.sample.dir/qc/qc_report.html
wt.sample.dir/method_A.analysis/report.html
wt.sample.dir/method_B.analysis/report.html

ko.sample.dir/overview.html
ko.sample.dir/qc/qc_report.html
ko.sample.dir/method_A.analysis/report.html
ko.sample.dir/method_B.analysis/report.html
```

The report.yml might look like this:

```
title: "My analysis report"

# the contents of the report goes here
report:
   # "def" is a special key which configures the
   # current level of the report (in this case the top level)
   def:
      title: "Report title"
      contents: >-
         Description of report goes here.

   # make a subsection for each sample
   samples:
      def:
         # The source defines the source folder(s) for the section(s)
         source: "*.sample.dir"

         # The destination folder
	 target: "."

	 title: "Per sample reports"
	 contents: >-
	    Per sample analysis reports
	 pages:
	    overview: "overview.html"
	    qc: "qc/qc.html"

      # make subsections for the different analysis reports
      methods:
         def:
	    source: "*.analysis"
	    target: "."
	    title: "method reports"
	    contents: ""
	    pages:
	       report: "report.html"

```

And arco run as follows:

```
arco --theme arco/themes/hugo-theme-learn-2.4.0.tar.gz            # the hugo theme to use
     --modifications archo/themes/hugo-theme-learn-modifications  # modifications to the theme
     --recipe=report.yml                                          # the yaml recipe defining the report
     --indir=.                                                    # the directory containing the input files
     --outdir=report.dir                                          # the directory for the output
     --overwrite                                                  # if set an existing outdirectory will be overwritten
```

When the report has been built, it can be viewed using hugo

```
hugo serve -p 1313           # -p is the port on which the report will be served
           -s report.dir     # -s is the source folder containing the hugo report
```


**Notes**

* Each section definition in the yaml must include a “def” key comprising of a dictionary defining its source, target, title, contents (and pages).

* title is ignored if globbing.

* Any key not called “def” is treated as a subsection.

* Source and target paths are relative to those of any parent section(s) which are automatically inherited.

* For globbing, folders/files must be picked up by a common suffix (ending). Arco uses globbed prefix as the title.

* All glob patterns must begin with a star as the first character, i.e. “*.common_suffix”

* You cannot include parent folders in the glob specification (i.e. “parent.dir/*.suffix” is not supported). In such situations you need to define the parent folder as a parent section.
