[app]

# (str) Title of your application
title = Steam Auth Manager

# (str) Package name
package.name = steamauth

# (str) Package domain (needed for android/ios packaging)
package.domain = org.steamauth

# (source.dir) Source code directory
source.dir = .

# (list) Source include patterns
source.include_exts = py,png,jpg,kv,atlas,ttf

# (list) Permissions
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

# (list) Features
android.features = 

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API for the application.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Use the new toolchain
android.accept_sdk_license = True

# (list) Pattern to whitelist for the whole project
android.whitelist = lib-dynload/termios.so

# (list) Python modules
android.modules = sqlite3

# (str) Android logcat filters to use
log_level = 2

# Requirements
requirements = python3,kivy,pycryptodomex,requests

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning on buildozer.spec
warn_on_root = 1
