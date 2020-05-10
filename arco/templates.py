# ########################################################################### #
# ###################### HUGO page templates ################################ #
# ########################################################################### #

# templates
config = '''\
             baseURL = "%(baseurl)s"
             languageCode = "en-us"
             title = "%(title)s"
             theme = "%(theme_name)s"
             uglyURLs = true
             disablePathToLower = true

             [outputs]
             home = ["HTML", "RSS", "JSON"]

             [markup.goldmark.renderer]
             unsafe= true
         '''

index = '''\
            +++
            title = "%(title)s"
            weight = %(weight)s
            +++
            %(contents)s
            {{%% children %%}}
         '''

page = '''\
           +++
           title = "%(title)s"
           weight = %(weight)s
           +++
           {{%% include_html_in_iframe file="%(html_file_path)s" %%}}
        '''
