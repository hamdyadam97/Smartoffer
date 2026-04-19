#!/usr/bin/env python3
"""Build frontend and integrate with Django (cross-platform)"""
import os
import shutil
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

print("Building frontend...")
os.chdir(os.path.join(BASE_DIR, "frontend"))
result = subprocess.run(["npm", "run", "build"], capture_output=True, text=True)
if result.returncode != 0:
    print(result.stderr)
    sys.exit(1)
print(result.stdout)

source = os.path.join(BASE_DIR, "frontend", "dist")
dest = os.path.join(BASE_DIR, "smartoffer_django", "static")
templates_dir = os.path.join(BASE_DIR, "templates")

print("Copying dist assets to Django static...")
os.makedirs(dest, exist_ok=True)

# Remove old assets
assets_dir = os.path.join(dest, "assets")
if os.path.exists(assets_dir):
    shutil.rmtree(assets_dir)
for f in ["favicon.svg", "index.html"]:
    p = os.path.join(dest, f)
    if os.path.exists(p):
        os.remove(p)

# Copy new assets
shutil.copytree(os.path.join(source, "assets"), os.path.join(dest, "assets"))
if os.path.exists(os.path.join(source, "favicon.svg")):
    shutil.copy2(os.path.join(source, "favicon.svg"), os.path.join(dest, "favicon.svg"))

print("Generating Django template...")
with open(os.path.join(source, "index.html"), "r", encoding="utf-8") as f:
    html = f.read()

html = html.replace('href="/favicon.svg"', 'href="{% static \'favicon.svg\' %}"')
import re
html = re.sub(r'src="/assets/([^"]+)"', r'src="{% static \'assets/\1\' %}"', html)
html = re.sub(r'href="/assets/([^"]+)"', r'href="{% static \'assets/\1\' %}"', html)

if "{% load static %}" not in html:
    html = html.replace("<!doctype html>", "{% load static %}\n<!doctype html>")

os.makedirs(templates_dir, exist_ok=True)
with open(os.path.join(templates_dir, "index.html"), "w", encoding="utf-8") as f:
    f.write(html)

print("Done! Frontend integrated with Django.")
print("Run 'python manage.py collectstatic --noinput' next.")
