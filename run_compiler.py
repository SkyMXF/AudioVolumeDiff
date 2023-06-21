import os
import venv
import shutil
import subprocess


CURRENT_DIR = os.path.abspath(".")
COMPILE_DIR = os.path.join("compile")
ENV_DIR = os.path.join(COMPILE_DIR, "env")
PYTHON_PATH = os.path.join("env", "Scripts", "python.exe")
COMPILER_NAME = "compile.py"
RELEASE_DIR = os.path.abspath("release")
POST_RELEASE_FILE_LIST = [
    os.path.abspath("material.css"),
    os.path.abspath("config.json"),
]


if __name__ == '__main__':

    # clean release dir
    shutil.rmtree(RELEASE_DIR, ignore_errors=True)
    os.makedirs(RELEASE_DIR)

    # create venv
    shutil.rmtree(ENV_DIR, ignore_errors=True)
    venv.create(env_dir=ENV_DIR, with_pip=True)

    # build subprocess cmds
    commands = list[str]()

    # activate env cmd
    # commands.append(os.path.join(ENV_DIR, "Scripts", "activate.bat"))

    # install requirements cmd
    commands.append("cd %s" % COMPILE_DIR)
    commands.append("%s -m pip install -r requirements.txt" % PYTHON_PATH)

    # run compiler cmd
    commands.append("%s %s" % (PYTHON_PATH, COMPILER_NAME))
    print("Running\n%s" % "\n".join(commands))

    # run subprocess
    subprocess.Popen(" && ".join(commands), shell=True).wait()

    # copy css and config to release
    for file_path in POST_RELEASE_FILE_LIST:
        shutil.copy(file_path, RELEASE_DIR)
