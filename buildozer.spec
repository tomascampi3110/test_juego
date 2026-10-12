[app]
title = Football Career Test
package.name = footballcareer
package.domain = ar.tomas.footballcareer
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt,json
source.include_patterns = assets/,assets/escudos/,assets/copas/*
source.exclude_dirs = tests,pycache,.git,bin,.buildozer
version = 0.1.0
requirements = python3,kivy==2.3.1
p4a.branch = develop
orientation = portrait
fullscreen = 0
icon.filename = assets/icon.png
presplash.filename = assets/icon.png
android.api = 35
android.minapi = 24
android.ndk = 28c
android.ndk_api = 24
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
