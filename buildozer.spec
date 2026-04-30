[app]

# (str) Title of your application
title = FaceFury

# (str) Package name
package.name = facefury

# (str) Package domain (needed for android/ios packaging)
package.domain = com.facefury

# (str) Source code where the main.py lives
source.dir = facefury

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,jpeg,gif,wav,mp3,ogg,xml

# (list) Source files to exclude
source.exclude_exts =

# (list) List of directory to exclude
source.exclude_dirs = tests, bin, __pycache__, .git

# (str) Application versioning
version = 1.0.0

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,pygame,opencv-python-headless,pillow,numpy

# (str) Presplash of the application (an image displayed while loading)
#presplash.filename = %(source.dir)s/assets/images/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/assets/images/icon.png

# (str) Supported orientation (one of landscape, sensorLandscape,
#   portrait, sensorPortrait, user, behind, sensor, fullSensor, nosensor,
#   reverseLandscape, reversePortrait, fullUser, all)
orientation = landscape

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# (list) Permissions
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,CAMERA

# (int) Target Android API, should be as high as possible
android.api = 33

# (int) Minimum API your APK / AAB will support
# Android 6.0 = API 23
android.minapi = 23

# (str) Android NDK version to use
android.ndk = 25b

# (int) Android NDK API to use. This is the minimum API your app will
#   support, it should usually match android.minapi
android.ndk_api = 23

# (bool) If True, then skip trying to update the Android sdk
# This can be useful to avoid excess Internet downloads or save time
# when an update is due and you just want to test/build your package
android.skip_update = False

# (bool) If True, then automatically accept SDK license
# agreements. This is intended for automation only. If set to False,
# the default, you will be shown the license when first running
# buildozer.
android.accept_sdk_license = True

# (str) Android entry point, default is ok for Pygame-based apps
#android.entrypoint = org.renpy.android.PythonActivity

# (str) Full name including package path of the Java class that implements Android Activity
# use that parameter together with android.entrypoint to set custom entry point
#android.activity_class_name = org.renpy.android.PythonActivity

# (list) Pattern to whitelist for the whole project
#android.whitelist =

# (str) Path to a custom whitelist file
#android.whitelist_src =

# (str) Path to a custom blacklist file
#android.blacklist_src =

# (list) List of Java .jar files to add to the libs so that pyjnius can
# access their classes. Don't add jars that you do not need, since extra jars
# can slow down the build process. Allows wildcards matching, for example:
# OUYA-ODK/libs/*.jar
#android.add_jars =

# (list) List of Java files to add to the android project (can be java or a
# temporary directory that contains the files)
#android.add_src =

# (list) Android AAR archives to add
#android.add_aars =

# (list) Put these files or directories in the apk assets directory.
# Either form may be used, and assets need not be in 'source.dir'.
# 1) An item of the list can be a three element tuple -- (src, &lt;relative_path_in_the_assets_dir&gt;, action)
# where action is one of "include", "exclude"
# 2) An item of the list can be just a string, which is a source file/dir
android.add_assets = facefury/assets/sounds/

# (list) Gradle dependencies to add
#android.gradle_dependencies =

# (bool) Enable AndroidX support. Enable when 'android.gradle_dependencies'
# contains an pointAndroidX library, or any library from the Jetpack family.
#android.enable_androidx = True

# (list) add java compile options
# this can for example be necessary when importing certain java libraries using the 'android.gradle_dependencies' option
# see https://developer.android.com/studio/write/java8-support for further information
# android.add_compile_options = "sourceCompatibility = 1.8", "targetCompatibility = 1.8"

# (list) Gradle repositories to add {can be necessary for some android.gradle_dependencies}
# please enclose in double quotes 
# e.g. android.gradle_repositories = "maven { url 'https://kotlin.bintray.com/ktor' }"
#android.gradle_repositories =

# (list) packaging options to add 
# see https://google.github.io/android-gradle-plugin/javadoc/com/android/build/api/dsl/PackagingOptions.html
# can be necessary to resolve conflicts in gradle_dependencies
# please enclose in double quotes 
# e.g. android.packaging_options = "exclude 'META-INF/common.kotlin_module'", "exclude 'META-INF/*.kotlin_module'"
#android.packaging_options =

# (list) Java classes to add as activities to the manifest.
#android.add_activities = com.example.ExampleActivity

# (str) OUYA Console category. Should be one of GAME or APP
# If you leave this blank, OUYA support will not be enabled
#android.ouya.category = GAME

# (str) Filename of OUYA Console icon. It must be a 732x412 png image.
#android.ouya.icon.filename = %(source.dir)s/data/ouya_icon.png

# (str) XML file to include as an intent filters in <activity> tag
#android.manifest.intent_filters =

# (str) launchMode to set for the main activity
#android.manifest.launch_mode = standard

# (list) Android additional libraries to copy into libs/armeabi
#android.add_libs_armeabi = libs/android/*.so
#android.add_libs_armeabi_v7a = libs/android-v7/*.so
#android.add_libs_arm64_v8a = libs/android-v8/*.so
#android.add_libs_x86 = libs/android-x86/*.so
#android.add_libs_mips = libs/android-mips/*.so

# (bool) Indicate whether the screen should stay on
# Don't forget to add the WAKE_LOCK permission if you set this to True
#android.wakelock = False

# (list) Android application meta-data to set (key=value format)
#android.meta_data =

# (list) Android library project to add (will be added in the
# project.properties automatically.)
#android.library_references =

# (list) Android shared libraries which will be added to AndroidManifest.xml using <uses-library> tag
#android.uses_library =

# (str) Android logcat filters to use
android.logcat_filters = *:S python:D

# (bool) Android logcat only display log for activity's pid
#android.logcat_pid_only = False

# (str) Android additional adb arguments
#android.adb_args = -H host.docker.internal

# (bool) Copy library instead of making a libpymodules.so
#android.copy_libs = 1

# (list) The Android archs to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
# In past, was `android.arch` as we now support builds for multiple archs.
android.archs = arm64-v8a, armeabi-v7a

# (int) overrides automatic versionCode computation (used in determine version info) with a
# temporary value during development in order to avoid value overflow
# android.numeric_version = 1

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

# (str) XML file for custom backup rules (see official auto backup documentation)
# android.backup_rules =

# (str) If you need to insert variables into your AndroidManifest.xml file,
# you can do so with the manifestPlaceholders property.
# This property takes a map of key-value pairs. (via a string)
# Usage example : android.manifest_placeholders = [myCustomUrl:\"org.kivy.customurl\"]
# android.manifest_placeholders = [:]

# (bool) disables the compilation of py to pyc/pyo files when packaging
# android.no-compile-pyo = True

# (str) The format used to package the app for release mode (aab or apk or aar).
android.release_artifact = apk

# (str) The format used to package the app for debug mode (apk or aar).
android.debug_artifact = apk

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .aab, .ipa) storage
bin_dir = ./bin
