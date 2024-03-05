#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time     : 2024/3/5 19:35
# @Author   : Chao Zhu
# @FileName : create_rpm.py
# @Software : PyCharm

import shlex
import shutil
import subprocess
import os
import glob


def copy_file(src, dest):
    try:
        shutil.copy(src, dest)
        print(f"File copied: {src} -> {dest}")
    except Exception as e:
        raise RuntimeError(f"Error copying file {src} to {dest}: {e}")


def create_rpm_package(source_dir, output_dir, name, version, release, arch):
    # 创建RPM工作目录结构
    rpmbuild_dir = os.path.join(output_dir, "rpmbuild")
    os.makedirs(os.path.join(rpmbuild_dir, "SOURCES"), exist_ok=True)
    os.makedirs(os.path.join(rpmbuild_dir, "SPECS"), exist_ok=True)

    # 将文件拷贝到SOURCES目录下
    for file_name in os.listdir(source_dir):
        src_file = os.path.join(source_dir, file_name)
        dest_file = os.path.join(rpmbuild_dir, "SOURCES", file_name)
        copy_file(src_file, dest_file)

    # 编写.spec文件内容
    spec_content = f"""
%define name {name}
%define version {version}
%define release {release}
%define buildroot %{{_tmppath}}/%{{name}}-%{{version}}-root

Summary: {name} RPM package
Name: %{{name}}
Version: %{{version}}
Release: %{{release}}
License: MIT
BuildArch: {arch}

%description
This is a {name} RPM package.

%prep
%setup -q

%build
# Add build commands here

%install
rm -rf %{{buildroot}}
# Add install commands here

%files
# Add file list here

%changelog
# Add changelog entries here
"""

    # 将.spec文件写入SPECS目录
    spec_file_path = os.path.join(rpmbuild_dir, "SPECS", f"{name}.spec")
    with open(spec_file_path, "w") as spec_file:
        spec_file.write(spec_content)

    # 使用rpmbuild命令构建RPM包
    rpmbuild_cmd = f"rpmbuild -ba {spec_file_path}"
    try:
        subprocess.run(shlex.split(rpmbuild_cmd), check=True)
        print("RPM package created successfully")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error running rpmbuild: {e}")

    # 移动生成的RPM包到输出目录
    rpm_files = glob.glob(os.path.join(rpmbuild_dir, "RPMS", arch, f"{name}*.rpm"))
    for rpm_file in rpm_files:
        dest_file = os.path.join(output_dir, os.path.basename(rpm_file))
        copy_file(rpm_file, dest_file)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create RPM package.")
    parser.add_argument("--source-dir", required=True, help="Path to source directory")
    parser.add_argument("--output-dir", required=True, help="Path to output directory")
    parser.add_argument("--name", required=True, help="Package name")
    parser.add_argument("--version", required=True, help="Package version")
    parser.add_argument("--release", required=True, help="Package release")
    parser.add_argument("--arch", required=True, help="Package architecture")

    args = parser.parse_args()

    try:
        create_rpm_package(
            args.source_dir,
            args.output_dir,
            args.name,
            args.version,
            args.release,
            args.arch
        )
    except Exception as e:
        print(f"Error: {e}")
