import os.path
import sys
import argparse

# import QCoreApplication
from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication
from qt_material import build_stylesheet

from view.main import MainWindow
from utils import p4
from utils import diff_checker
from utils.watch_setting import WatchSetting


BASE_CONFIG_PATH = "config.json"
USER_CONFIG_PATH = "user_config.json"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prev", type=str, required=False)
    parser.add_argument("--curr", type=str, required=False)
    parser.add_argument("--clean_mode", action="store_true")
    parser.add_argument("--no_gui", action="store_true")

    return parser.parse_args()


def start_gui_app(ws: WatchSetting, watch_setting_save_path: str):
    # init
    app = QApplication([])
    main_window = MainWindow(
        loaded_watch_setting=ws,
        watch_setting_save_path=watch_setting_save_path,
    )

    # style setting
    stylesheet = build_stylesheet(theme="dark_teal.xml", template="material.css")
    app.setStyleSheet(stylesheet)

    # start app
    main_window.show()
    app_thread = app.exec()

    # end
    sys.exit(app_thread)


def start_console_app(ws: WatchSetting):

    p4_client = MainWindow.create_p4_client(ws)
    for watch_item in ws.watch_item_list:
        print("[Start]Start checking '%s'" % watch_item.name)
        checker = MainWindow.create_checker(
            watch_item=watch_item,
            p4_client=p4_client,
            check_rules=MainWindow.get_check_rules(),
            clean_mode=not ws.disable_clean_mode,
        )
        for file_idx, file_path in checker.check(p4_client, yield_path_flag=True):
            print("\r[Checking][%d/%d]%s" % (file_idx + 1, len(checker), file_path), end="")
        output_path = MainWindow.save_checker_result(
            checker=checker,
            watch_item=watch_item,
            output_dir=ws.output_dir,
        )
        print("\n[End]Finish checking. Result saved to '%s'" % os.path.abspath(output_path))


if __name__ == '__main__':

    # load watch setting
    watch_setting = WatchSetting()
    if os.path.exists(BASE_CONFIG_PATH):
        watch_setting.from_json(BASE_CONFIG_PATH)
    if os.path.exists(USER_CONFIG_PATH):
        watch_setting.from_json(USER_CONFIG_PATH)

    # parse args
    args = parse_args()
    for item in watch_setting.watch_item_list:
        if args.prev is not None:
            item.prev_stamp = args.prev
        if args.curr is not None:
            item.curr_stamp = args.curr
    watch_setting.disable_clean_mode = not args.clean_mode

    if args.no_gui:
        start_console_app(watch_setting)
    else:
        start_gui_app(watch_setting, USER_CONFIG_PATH)

