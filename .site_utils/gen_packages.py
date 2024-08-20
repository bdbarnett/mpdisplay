#!/bin/python

import os
import json
from pprint import pprint  # noqa: F401

package_ver = "0.1"
repo_url = "github:bdbarnett/mpdisplay/"
repo_dir = "/home/brad/gh/mpdisplay/"
src_dir = "src/"
output_dir = repo_dir
packages_dir = "packages/"
toml_full_path = output_dir + "html/mpdisplay.toml"
master_package_name = "package"

displays_shared = ["_basedisplay.py", "_basedisplay_numpy.py", "_basedisplay_viper.py", "splash.py"]
# list of package directories and extra files in that package
packages = [
    ["configs", ["path.py"]],
    ["examples", []],
    ["extras", []],
    ["lib/area", []],
    ["lib/displays/busdisplay", displays_shared],
    ["lib/displays/dtdisplay", displays_shared],
    ["lib/displays/fbdisplay", displays_shared],
    ["lib/displays/jndisplay", displays_shared],
    ["lib/displays/psdisplay", displays_shared],
    ["lib/eventsys", []],
    ["lib/framebuf", []],
    ["lib/graphics", []],
    ["lib/palettes", []],
    ["lib/timer", []],
    ]

master_exclude = ["examples"]


package_dicts = dict()
master_package =  {"urls": [], "version": package_ver}
master_toml = ["[files]"]
extra_files_added_to_master = []

for package_path, extra_files in packages:
    package_name = package_path.split("/")[-1]
    if package_name == package_path:
        package_sub_dir = ""
    else:
        package_sub_dir = "/".join(package_path.split("/")[:-1])
    package_dicts[package_name] = {"urls": [], "version": package_ver}
    full_path = os.path.join(repo_dir, src_dir, package_path)

    for extra_file in extra_files:
        full_file_path = os.path.join(repo_dir, src_dir, package_sub_dir, extra_file)
        dest_file = os.path.relpath(full_file_path, repo_dir + src_dir)
        src_file = repo_url + src_dir + dest_file
        package_dicts[package_name]["urls"].append([dest_file, src_file])
        if package_name not in master_exclude:
            if full_file_path not in extra_files_added_to_master:
                # Add the file to both the master package and the TOML file
                master_package["urls"].append([dest_file, src_file])
                toml_dest = f'/{"/".join(dest_file.split("/")[:-1])}/'
                if toml_dest == "//":
                    toml_dest = "/"
                master_toml.append(f'"../{src_dir + dest_file}" = "{toml_dest}"')
                extra_files_added_to_master.append(full_file_path)

    for root, _, files in os.walk(full_path):
        for f in files:
            full_file_path = os.path.join(root, f)
            dest_file = os.path.relpath(full_file_path, repo_dir + src_dir)
            src_file = repo_url + src_dir  + dest_file
            package_dicts[package_name]["urls"].append([dest_file, src_file])
            if package_name not in master_exclude:
                master_package["urls"].append([dest_file, src_file])
                toml_dest = f'/{"/".join(dest_file.split("/")[:-1])}/'
                if toml_dest == "//":
                    toml_dest = "/"
                master_toml.append(f'"../{src_dir + dest_file}" = "{toml_dest}"')
    if package_name not in master_exclude:
        master_toml.append("")

# pprint(package_dicts)
# pprint(master_package)
# for line in master_toml: print(line) # noqa: E701

package_dicts[master_package_name] = master_package

for package_name, contents in package_dicts.items():
    if package_name == master_package_name:
        package_file = output_dir + package_name + ".json"
    else:
        package_file = output_dir + packages_dir + package_name + ".json"
    with open(package_file, "w") as f:
        json.dump(contents, f, indent=4)

with open(toml_full_path, "w") as f:
    for line in master_toml:
        f.write(line + "\n")

print(f"{__file__.split('/')[-1]} finished\n")
