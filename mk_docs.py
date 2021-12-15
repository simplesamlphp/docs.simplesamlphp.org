#! /bin/python3

import markdown
import glob
import os
import urllib.request
import json 
from bs4 import BeautifulSoup

# Some functions

# Convert md file to html file
# - make sure links remain working
# - add header, navigation and footer to the converted file
def md2html(md_file, html_file, file_name):
    #print("Transforming " + md_file + " into " + html_file)
    
    
    with open(md_file, 'r') as f:
       text = f.read()

       html = markdown.markdown(text, tab_length=2)
       soup = BeautifulSoup(html, 'html.parser')
       for a in soup.findAll('a'):
         
         if not a['href'].startswith(('http://', 'https://')):
           if not a['href'].endswith(('html')):
              a['href'] = a['href']+".html"
       
           if (str(a['href']).find(":") > 0):
             a['href'] = a['href'].replace(":", "/")
       
       # TODO: At this point we could use title and description to auto generate a breadcrum or an index
       #title = soup.find('h1').string
       #if (len(title.split(":")) > 1):
       #  title = title.split(":")[1]
       
       #desc = ""
       #p = soup.find('p')
       #if not p is None:
       #   desc = " - " + str(p.string)

    with open(html_file, 'w+') as f:
       f.write(header + mkContentHeader(ssp_versions) + str(soup.prettify()) + footer)	

# search a filesystem directory for subdirs and retum these in a list
def getsubdirs(dir_path):
	return(glob.glob(dir_path + '*/'))

# search a filesystem directory for markdown (md) files and parse these into html using the md2html function
def parsefiles(docsdir, outputdir):
    #print("parsing files from '" + docsdir + "' into '" + outputdir + "'")

    if os.path.isdir(docsdir):

      if not os.path.isdir(outputdir):
        os.makedirs(outputdir)

      os.chdir(docsdir)

      for file in glob.glob('*.md'):
        md_file = docsdir + file
        html_file = outputdir + file[:-3] + '.html'

        md2html(md_file, html_file, file)

# get a list of all repositories in the ssp github project
def getmodulerepos():
    module_repos = []
    
    with urllib.request.urlopen("https://api.github.com/users/simplesamlphp/repos") as url:
       repos = json.loads(url.read().decode())
    
    for repo in repos:
      a_repo = {"name": [], "description": [], "html_url": []}
	
      # we assume all module will have a name that starts with 'simplesamlphp-module-' 
      if (repo['name'].find('simplesamlphp-module-') == 0):
        a_repo['name'] = str(repo['name'])
        a_repo['description'] = str(repo['description'])
        a_repo['html_url'] = str(repo['html_url'])

        module_repos.append(a_repo)       
    
    return module_repos

# clone a specific git repo to a given directory. Optionally fetch specific version
# Target directories will be autocreated
def getgitrepo(repo, repo_clone_dir, repo_root, version=None):
   os.makedirs(os.path.join(repo_clone_dir))
   os.chdir(repo_clone_dir)
   
   os.system('git clone --depth=1 ' + repo)
   os.chdir(repo_clone_dir + repo_root)
   
   print("Working in git repo from" + os.getcwd())
   
   if (version is not None):
      os.system('git checkout -b ' + version)
   os.system('git status')

# make the header and headerbad div contents for indjection into each documentation page
def mkContentHeader(versions):
    content = '<body>'

    content += '<!-- Red logo header -->'
    content += '<div id="header">'
    content += '	<div id="logo"><a href="https://simplesamlphp.org" style="color: #fff; text-decoration: none" target="_blank">SimpleSAMLphp</a></div>'
    content += '</div>'
    content += '<!-- Grey header bar below -->'
    content += '<div id="headerbar" style="clear: both">'
    content += mkNavigation(versions)
    content += '<br style="height: 0px; clear: both" />'
    content += '</div><!-- /#headerbar -->'
    content += '<div id="content">'
   
    return content

# make a navigation structure based on the versions we have doucmentation for    
def mkNavigation(versions):
    
    content = '<div id="langbar" style="clar: both"><div id="navigation">Documentation is available for the following versions: '
    for version in versions:
        content += '<a href="./../'+version+'/index.html">'+version+'</a> | '
    content += ' modules</div></div>'
    
    return content

# make sure some hard coded resources like css, js and some images are put in the right place for teh website
def mkResources(root_dir, web_root):
    # Copy over the website js and css resources
    #if not os.path.exists(os.path.join(site_root_dir + '/res/js/')):
    os.makedirs(os.path.join(web_root + '/res/js/'))
   
    #if not os.path.exists(os.path.join(site_root_dir + '/res/css/')):
    os.makedirs(os.path.join(web_root + '/res/css/'))
    os.system('cp -R ' +  root_dir + 'resources/js/ ' + web_root + 'res/')
    os.system('cp -R ' +  root_dir + 'resources/css/ ' + web_root + 'res/')

    # starter index.html (just a redirect to 'latest')    
    os.system('cp ' +  root_dir + 'resources/index.html ' + web_root + 'index.html ')

def mkcontribmodsindex(contrib_mods, module_index_file):
    module_index = "---\n"
    module_index += "layout: default\n"
    module_index += "title: Documentation\n---\n"
    module_index += "---\n"
    module_index += "SimpleSAMLphp Contributed modules\n"
    module_index += "===========================\n\n"

    # now find all the contents taht 
    
    
    
    for module in contrib_mods:
      module_index += " * ["+ module["name"] + "](" + module["html_url"] + ") \n" + module["description"] + "\n"
      
    with open(module_index_file, 'w+') as f:
       f.write(module_index)
	
################################################
#
# MAIN
#
################################################

# Configuration of static variables
root_dir = os.path.expanduser('~') + "/"
tempdir = root_dir + "ssp_tmp/"

#Runner path eequals $GITHUB_WORKSPACE
runner_path = '/home/runner/work/docs.simplesamlphp.org/docs.simplesamlphp.org/'

repo_root_dir = "simplesamlphp/"
repo_docs_dir = "docs/"
repo_modules_dir = "modules/"

site_root_dir = runner_path + "_site/"
header = runner_path + "resources/header"
footer = runner_path + "resources/footer"

# for which versions should we generate documentation?
# ToDo: replace with dynamic assasment based on github tags
ssp_versions=["latest","1.19", "1.18", "1.17"]

# Make sure we have a working site subdir to put stuff in
os.system('mkdir ' +  site_root_dir)
os.system('mkdir ' +  tempdir)

# make the header and footer available as global vars
print("reading Header")
with open(header, 'r') as f:
  header = f.read()

print("reading Footer")
with open(footer, 'r') as f:
  footer = f.read()

# Copy over resources like js and css files and a the starter index.html that will always redirect to "latest"
mkResources(runner_path, site_root_dir)

# Now generate contents based documentation for core simplesamlphp repo
for ssp_version in ssp_versions:
   print("Working on: " + ssp_version)
   #print("Repo Root: " + repo_root_dir)
   
   version_dir = tempdir + ssp_version + "/"
   #print("Version dir: " + version_dir)
   getgitrepo('https://github.com/simplesamlphp/simplesamlphp.git', version_dir, repo_root_dir, ssp_version)
   versioned_site_root =  site_root_dir + ssp_version + "/"

   # Parse main docs for this version
   parsefiles(os.path.join(version_dir, repo_root_dir, repo_docs_dir), versioned_site_root)

   # get all the modules in this version
   mods = getsubdirs(os.path.join(os.path.join(version_dir, repo_root_dir, repo_modules_dir)))

   # parse 'core' modules docs (if available)
   for module in mods:
     module_name = os.path.basename(os.path.normpath(module))
     module_dir = os.path.join(module, "docs/")
     module_output_dir = os.path.join(versioned_site_root, module_name + "/" )
     parsefiles(module_dir, module_output_dir)

# Fetch and generate documentation for contributed modules as made availabe in various ssp repos
# Contributes modules are not version dependent on the main source and hence are generated seperately from versioned documentation
contrib_mods = getmodulerepos()
module_index_file = tempdir + "contributed_modules.md"

for module in contrib_mods:
    print("Working on: " + module["name"])
    contrib_mod_dir = tempdir + "contrib_modules/" + module["name"] + "/"
    contrib_mod_web_dir = site_root_dir + "contrib_modules" + "/"
    
    # We assume contributes modules live in te simplesampphph repo and are named 'simplesamlphp-module-*' 
    getgitrepo(module["html_url"], contrib_mod_dir, module["name"])
    
    module_dir = os.path.join(contrib_mod_dir, module["name"], "docs/")
    print(module_dir)
    
    if os.path.isdir(module_dir):
      module_output_dir = os.path.join(contrib_mod_web_dir, module["name"].split("-")[2] + "/" )
      #print(module_output_dir)
      parsefiles(module_dir, module_output_dir)
    
    else:
        print("No docs found for '" + module["name"] +"'")


f = []
for (dirpath, dirnames, filenames) in walk(site_root_dir + "contrib_modules" + "/"):
    f.extend(filenames)
    
print(f)


# Dump website tree so we can see in the runner if all went well
# os.system('tree ' +  site_root_dir)

#mkcontribmodsindex(contrib_mods, module_index_file)
#md2html(module_index_file, site_root_dir + 'contributed_modules.html', 'contributed_modules.html')
   



