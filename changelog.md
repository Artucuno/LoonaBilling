![LoonaBilling](https://user-images.githubusercontent.com/28388670/172512382-81059cf6-c872-4a4c-a370-223f2d4d009c.png)

<img src="https://img.shields.io/discord/887501133902385202?logo=discord&style=social"> <img src="https://img.shields.io/github/last-commit/Loona-cc/LoonaBilling?logo=github&style=social"> <img src="https://img.shields.io/github/workflow/status/Loona-cc/LoonaBilling/CodeQL?logo=github-sponsors&style=social">

# Development Changelog
Sorry for the late update, I tried to make this update a little bigger.

## LoonaBilling
+ Renamed links in `templates/core/index.html`
+ Failed module loading is deleted from `app.mods` list

## Admin Dashboard
+ Added Admin Modules Tab
  + Enable/Disable Modules
  + Install Modules

+ Added Update Tab
  + Check for updates
  + Pull new updates (WIP)

+ Added File Manager Tab
  + Edit template files from the web browser

+ New Admin Sidebar
  + Branding Tab
  + Modules Tab
  + Update Tab
  + File manager tab
  + Theme Manager

## Customer Dashboard
+ Added new links
  + Help / Support
    + Support Page
    + Tickets
  + Services
    + Payments

## Config
+ Removed Branding Settings -> Moved to Branding Tab

## Accounts
+ Fixed dashboard being Accounts.wrapper
+ Added Manage Accounts Tab
+ Suspended accounts now redirect to `error.html` with message

# Auth Util
+ Updated login_is_required wrapper
  + Fixed routes becoming module.wrapper

# Files Util
+ Added `readJSON(file)` function
+ Added `readJSONVar(file, var)` function
+ Added `delVarJSON(file, var)` function
+ Added `getBranding()` function
+ Added `Filesize(file)` function
+ Added `endisModule(module)` function
+ Added `moduleEnabled(module)` function

# Mail Util
+ Added Threaded Mail Sending

# Network Util
+ Added Network Util to cut down on repeated code

## Divs
+ Added adminSide div

# Other
+ Join our [Discord](https://loona.cc)!
