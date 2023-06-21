import os
import time
from queue import Queue
from typing import Optional

from PySide6.QtWidgets import QMainWindow
from PySide6.QtGui import QDesktopServices, QTextCursor
from PySide6.QtCore import QUrl, Qt

from utils.watch_setting import WatchSetting, WatchItem
from utils import p4
from utils import diff_checker
from utils.async_task import AsyncTaskThread
from .utils.table_view_utils import TableRowModel, TableWrapper
from .ui.main_window import Ui_MainWindow
from .watch_item_edit_dialog import WatchItemEditDialog


TABLE_HEADER = ["", "Name", "Depot Path", "Prev Stamp (Time or Change ID)", "Curr Stamp (Time or Change ID)"]
COLUMN_DEFAULT_WIDTH = 150


class WatchItemRowModel(TableRowModel):

    TABLE_HEADER = ["", "Name", "Depot Path", "Prev Stamp", "Curr Stamp"]

    def __init__(self, watch_item: WatchItem):
        super(WatchItemRowModel, self).__init__()

        self.watch_item: WatchItem = watch_item

    @property
    def display_data(self) -> list[any]:
        return [
            self.checked,
            self.watch_item.name,
            self.watch_item.path,
            self.watch_item.prev_stamp,
            self.watch_item.curr_stamp,
        ]

    @property
    def hidden_data(self) -> any:
        return self.watch_item


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(
        self,
        loaded_watch_setting: Optional[WatchSetting] = None,
        watch_setting_save_path: str = "",
        console_mode: bool = False,
    ):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        # console mode
        self.console_mode = console_mode

        # watch setting
        self.watch_setting = WatchSetting() if loaded_watch_setting is None else loaded_watch_setting
        self.watch_setting_save_path = watch_setting_save_path
        self.save_watch_setting()       # generate user config file

        # watch setting table
        self.table_wrapper = TableWrapper(self.tableView)
        self.init_table()
        self.checkBoxSelectAll.setChecked(True)
        self.checkBoxSelectAll.clicked.connect(self.table_wrapper.select_all_rows)
        self.pushButtonAddPath.clicked.connect(self.on_click_add_path)
        self.pushButtonRemoveSelected.clicked.connect(self.on_click_remove_selected_path)
        self.table_wrapper.double_click_row_delegate = self.on_double_click_table_item
        self.watch_item_edit_dialog = None

        # p4 utils
        self.p4_client = self.create_p4_client(self.watch_setting)

        # checker utils
        diff_checker.CLEAN_MODE = not self.watch_setting.disable_clean_mode

        # output folder
        self.refresh_output_folder_view()
        self.pushButtonOpenOutput.clicked.connect(self.on_click_open_output_folder)

        # run checker
        self.pushButtonCheck.clicked.connect(self.on_click_run_checking)
        self.on_async_update_progress_bar(1.0)
        self.checking_queue = Queue()
        self.current_checker: Optional[diff_checker.DiffChecker] = None
        self.current_watch_item: Optional[WatchItem] = None

        # console output
        self.text_edit_replace_last_flag: Optional[bool] = None        # if true, new line will replace last line

    def init_table(self):
        self.table_wrapper.set_header(TABLE_HEADER)
        self.table_wrapper.hide_vertical_header()
        self.table_wrapper.init_table_setting()
        self.table_wrapper.set_column_width(COLUMN_DEFAULT_WIDTH)
        self.table_wrapper.set_column_width(50, col=0)
        self.table_wrapper.set_column_width(500, col=2)
        self.table_wrapper.set_column_width(250, col=3)
        self.table_wrapper.set_column_width(250, col=4)

        # append data
        for watch_item in self.watch_setting.watch_item_list:
            self.table_wrapper.append_line(WatchItemRowModel(watch_item))

    @staticmethod
    def create_p4_client(watch_setting: WatchSetting) -> p4.P4Client:
        p4_client = p4.P4Client(
            port=p4.P4_SERVER if watch_setting.p4_server is None else watch_setting.p4_server,
            workspace_name=p4.P4_WORKSPACE_NAME
            if watch_setting.p4_workspace_name is None
            else watch_setting.p4_workspace_name,
        )
        return p4_client

    @staticmethod
    def get_check_rules() -> list[diff_checker.CheckRule]:
        return [
            diff_checker.CheckRule(
                diff_checker.resource_dBFS_diff_rule,
                "[Resource dBFS diff too large]\nPrev dBFS,Curr dBFS,Path"
            ),
            diff_checker.CheckRule(
                diff_checker.resource_max_dBFS_diff_rule,
                "[Resource max dBFS diff too large]\nPrev max dBFS,Curr max dBFS,Path"
            ),
            diff_checker.CheckRule(
                diff_checker.resource_channel_diff_rule,
                "[Resource channel num changed]\nPrev channel num,Curr channel num,Path"
            ),
            diff_checker.CheckRule(
                diff_checker.resource_changed_rule,
                "[Resource changed]\nAction,OldRev,NewRev,Path"
            ),
        ]

    @staticmethod
    def create_checker(
        watch_item: WatchItem,
        p4_client: p4.P4Client,
        check_rules: list[diff_checker.CheckRule],
        clean_mode: bool = False,
    ) -> diff_checker.DiffChecker:
        # get all change list
        change_lists = p4_client.get_changes_of_dir(
            base_dir=watch_item.path,
            begin_stamp=watch_item.prev_stamp,
            end_stamp=watch_item.curr_stamp,
            file_ext=".wav"
        )
        change_lists.sort(key=lambda c: c.id)

        # build checker
        checker = diff_checker.DiffChecker(clean_mode=clean_mode)
        checker.add_rules(check_rules)
        for change_list in change_lists:
            checker.version_forward(change_list)

        return checker

    @staticmethod
    def save_checker_result(
        checker: diff_checker.DiffChecker,
        watch_item: WatchItem,
        output_dir: str,
    ) -> str:
        # output result
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_path = os.path.join(output_dir, "%s_prev_%s_curr_%s.csv" % (
            watch_item.name,
            watch_item.prev_stamp.replace(":", "_").replace("/", "_"),
            watch_item.curr_stamp.replace(":", "_").replace("/", "_"),
        ))
        with open(output_path, "w") as f:
            print(checker.get_log(), file=f)

        return output_path

    # refresh line edit of output folder by self.watch_setting
    def refresh_output_folder_view(self):
        self.lineEditOutputPath.setText(os.path.abspath(self.watch_setting.output_dir))

    # update watch setting by table items
    def update_watch_setting_by_table(self):
        self.watch_setting.watch_item_list = [row.hidden_data for row in self.table_wrapper.model_rows]

    # save watch setting to user config json file
    def save_watch_setting(self):
        self.watch_setting.to_json(self.watch_setting_save_path)

    # add line to table
    def on_click_add_path(self):
        def add_watch_item(edited_item: WatchItem):
            watch_item = WatchItem()
            watch_item.update_from(edited_item)
            self.table_wrapper.append_line(WatchItemRowModel(watch_item))
            self.update_watch_setting_by_table()
            self.save_watch_setting()

        self.watch_item_edit_dialog = WatchItemEditDialog()
        self.watch_item_edit_dialog.save_post_delegate = add_watch_item
        self.watch_item_edit_dialog.setWindowModality(Qt.ApplicationModal)
        self.watch_item_edit_dialog.show()

    # edit watch item in table
    def on_double_click_table_item(self, watch_item_row_model: WatchItemRowModel):
        def update_watch_item(edited_item: WatchItem):
            watch_item_row_model.hidden_data.update_from(edited_item)
            self.table_wrapper.refresh_view()
            self.update_watch_setting_by_table()
            self.save_watch_setting()

        self.watch_item_edit_dialog = WatchItemEditDialog(watch_item_row_model.hidden_data)
        self.watch_item_edit_dialog.save_post_delegate = update_watch_item
        self.watch_item_edit_dialog.setWindowModality(Qt.ApplicationModal)
        self.watch_item_edit_dialog.show()

    # remove selected line in table
    def on_click_remove_selected_path(self):
        self.table_wrapper.remove_checked_rows()
        self.update_watch_setting_by_table()
        self.save_watch_setting()

    def on_click_open_output_folder(self):
        if not os.path.exists(self.watch_setting.output_dir):
            os.makedirs(self.watch_setting.output_dir)
        QDesktopServices.openUrl(QUrl.fromLocalFile(self.watch_setting.output_dir))

    # add item to checking queue, and start checking
    def on_click_run_checking(self):
        # clean checking queue
        while not self.checking_queue.empty():
            self.checking_queue.get()

        # add selected items to checking queue
        rows = self.table_wrapper.get_checked_rows()
        for row in rows:
            row: WatchItemRowModel
            self.checking_queue.put(row.hidden_data)

        # start checking
        self.on_async_update_progress_bar(0.0)
        self.setEnabled(False)      # disable ui
        self.start_next_checking_thread()

    # start a checking thread from checking queue
    def start_next_checking_thread(self):
        if self.checking_queue.empty():
            self.on_all_checking_thread_finished()
            return

        # create checker
        self.current_watch_item: WatchItem = self.checking_queue.get()
        self.current_checker: diff_checker.DiffChecker = self.create_checker(
            watch_item=self.current_watch_item,
            p4_client=self.p4_client,
            check_rules=self.get_check_rules(),
        )

        # start checking thread
        check_thread = AsyncTaskThread(
            task_worker=self.current_checker.check,
            task_args=[self.p4_client, True],
            task_length=len(self.current_checker),
            on_progress=self.on_async_update_progress_bar,
            on_task_result=self.on_async_file_checked,
            on_finish=self.on_curr_checking_thread_finished,
            parent=self
        )
        check_thread.start()
        self.print_running_log(
            "Start checking %s" % self.current_watch_item.path, header="Checking"
        )

    # update progress bar gui
    def on_async_update_progress_bar(self, progress: float):
        self.progressBar.setValue(int(progress * 100))

    # one file checked
    def on_async_file_checked(self, file_info: list):
        file_idx = file_info[0]
        file_path = file_info[1]
        self.print_running_log(
            "[%d/%d]%s" % (file_idx + 1, len(self.current_checker), file_path),
            header="Checking", need_replace=True
        )

    # one check thread finished
    def on_curr_checking_thread_finished(self):
        # output result
        output_path = self.save_checker_result(
            checker=self.current_checker,
            watch_item=self.current_watch_item,
            output_dir=self.watch_setting.output_dir,
        )

        self.print_running_log(
            "Check result saved to '%s'" % os.path.abspath(output_path),
            header="CheckFinshed"
        )

        # start next checking thread
        self.start_next_checking_thread()

    # all checking thread finished
    def on_all_checking_thread_finished(self):
        self.current_checker = None
        self.current_watch_item = None
        self.on_async_update_progress_bar(1.0)
        self.setEnabled(True)

    # print running log to ui
    def print_running_log(
        self,
        info: str,
        header: str = "",
        time_stamp: bool = True,
        need_replace: bool = False,
        to_stdout: bool = True
    ):
        line_str = "[%s][%s]%s" % (
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) if time_stamp else "",
            header, info
        )
        cursor = self.textEdit.textCursor()
        if need_replace:
            if self.text_edit_replace_last_flag:
                # last line need replace
                cursor.select(QTextCursor.LineUnderCursor)
                cursor.removeSelectedText()
            elif self.text_edit_replace_last_flag == False:
                self.textEdit.insertPlainText("\n")
        else:
            # if not empty, add a new line
            if self.text_edit_replace_last_flag is not None:
                self.textEdit.insertPlainText("\n")
        cursor.movePosition(QTextCursor.End)
        self.textEdit.insertPlainText(line_str)
        self.textEdit.ensureCursorVisible()

        if to_stdout:
            if need_replace:
                print("\r" + line_str, end="")
            else:
                if self.text_edit_replace_last_flag:
                    print("")
                print(line_str)

        self.text_edit_replace_last_flag = need_replace
