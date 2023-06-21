import os
import shutil

import PyInstaller.__main__


BASE_DIR = os.path.dirname(__file__)
SOURCE_PATH = os.path.join(BASE_DIR, "..", "check_wav_diff_gui.py")
BUILD_DIR = os.path.join(BASE_DIR, "build")
OUTPUT_PATH = os.path.join(BASE_DIR, "..", "release", "check_wav_diff_gui.exe")


if __name__ == '__main__':

    print("Compiling '%s'..." % SOURCE_PATH)

    # build output dir
    if not os.path.exists(BUILD_DIR):
        os.makedirs(BUILD_DIR)

    # create building dirs
    spec_dir = os.path.join(BUILD_DIR, "spec")
    dist_dir = os.path.join(BUILD_DIR, "dist")
    work_dir = os.path.join(BUILD_DIR, "../build")
    for dir_path in [spec_dir, dist_dir, work_dir]:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

    # run pyinstaller
    PyInstaller.__main__.run([
        "-F", SOURCE_PATH,
        "-n", os.path.splitext(os.path.basename(OUTPUT_PATH))[0],
        "--specpath", spec_dir,
        "--distpath", dist_dir,
        "--workpath", work_dir,
    ])

    # copy exe to output dir
    exe_src_path = os.path.join(dist_dir, os.path.basename(OUTPUT_PATH))
    shutil.copy(exe_src_path, OUTPUT_PATH)
