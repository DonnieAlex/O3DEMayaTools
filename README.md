This is a repository intended to host a set of tools that I will use myself while learning O3DE (Open 3D Engine), 
and I want to contribute something to the community.

The first tool you'll find here is an FBX Exporter. It leverages Maya's native FBX implementation, but its goal
is tailored more towards making things easier when it comes to common engine settings (like smoothing groups, 
preserve references or tangents and bi-normals) as well as automating multiple exports in one operation, 
include animation and separating things into animation clips, etc.

The whole interface received a tooltip treatment with brief explanations of what does what.
You can also save the (and later load) the configuration to file, so that you can always resume your work from 
where you left off.

It's nothing too complicated or fancy, really. But I hope someone may find it useful :)

### Added on September 2026: 
A new tool, the <u>Skeleton Builder</u>, has been added to the repo, along with some refactoring of the utility modules (in order to access functions and methods more easily across the two tools).
Skeleton Builder Tool: This tool is guide based using locators in amodular way, and let you create simple archetype body parts, supporting the traditional Left and Right, plus all the sensible combinations with Up, Down, Front and Back. 

There are modules to create modules from scratch, defining the number of sections per joint (i.e.: the Spine and the fingers), as well as a quick preset section with base parts you will likely need already shaped and sized to an average character. This latter option also works well as an example
to understand the general guidelines and principles used to create limbs and body parts (like the orientation at the end of a bipedal leg, for example)

It's configuration based (`SkeletonBuilder/configuration/joints_names_configuration.json`), so the joints naming convention can be changed there, allowing the guides to keep their naming. This will need a configuration manager to ease the configuration setup, but I've not come around making it yet.

There is support for managing multiple bind poses, recreating a T-Pose (more suitable for retargeting) with automatic HumanIK characterization, and a simple system to make sure that only one bind pose is active at any time. The active bind pose here is also recognized by the FBX Exporter and used for export of skinned meshes when animation is not included.

Like the FBXExporter, also this tool comes with tooltips on every piece of interface. 


# Installation instructions:
It's pretty easy: git clone somewhere on your computer. Open a terminal and cd into the main folder where this repo folder 
will live
```
cd /path/to/target/directory
git clone https://github.com/DonnieAlex/O3DEMayaTools.git
```
at this point, we go to our Maya user folder and we want to edit the current installation's .env file. 
Typical locations would be (depending on OS):

Linux:
home/<user_name>/maya/<version_number>/

Windows:
C:\Users\user_name\Documents\maya\version_number

MacOS:
Library/Preferences/Autodesk/maya/<version_number>

In this path, find (or create, if it's not there) the file ```Maya.env``` Be careful with the capitalization if you need to
create it from scratch.
Open that file to edit its contents.
add the following line:
```
PYTHONPATH = /path/to/target/directory/O3DEMayaTools
```
if PYTHONPATH already is being set there for some other tool of yours, make sure to append the path to this package.
To do this, you need to separate the paths in a list by using platform dependent separators.
Linux and MacOS use the : (colon)
Windows uses the ; (semicolon)

So, for example:
```
PYTHONPATH = other/path/to/another/tool:/path/to/target/directory/O3DEMayaTools
                                       ^ <- separator : is here on Linux and MacOS
```
and 
```
PYTHONPATH = other/path/to/another/tool;/path/to/target/directory/O3DEMayaTools
                                       ^ <- separator ; is here on Windows
```
~~If you had Maya running, it's time to restart it for these changes to be read and used.~~
~~Now, open the script editor, go to a Python tab and type~~

~~```~~
~~import FBX_Exporter.ExporterUI as ui~~
~~ui.FbxExportUI.load_window()~~
~~```~~
~~You can either highlight these two lines and run (play button on the top bar of the script editor OR right click-hold and choose 
"execute" from the context menu), or you can save this to a shelf as a button. Choose the shelf you want to use to house this new
button, then go back to the script editor (where the two lines above should still be highlighted, highlight them again if they're not)
and middle-click+drag over to the shelf, and drop on it to create the new button. Once the button is there, you can edit it and give it
a meaningful name, label and description by right-clicking on it and "edit"~~
The above has been replaced with a userSetup.py script within the package that creates a menu to access the available tools.

Enjoy!
