from typing import Callable, Optional

from PySide6.QtWidgets import QWidget

from .ui.watch_item_dialog import Ui_WatchItemEditDialog
from utils.watch_setting import WatchItem


SAMPLE_WATCH_ITEM = WatchItem(
    name="Sample Watch Item",
    path="//depot/...",
    prev_stamp="2023/4/6:19:00:00",
    curr_stamp="2023/5/25:17:00:00",
)


class WatchItemEditDialog(QWidget, Ui_WatchItemEditDialog):

    # edit given WatchItem or create an empty WatchItem
    def __init__(self, watch_item: Optional[WatchItem] = None):
        super(WatchItemEditDialog, self).__init__()
        self.setupUi(self)

        # set or create WatchItem
        self.editing_item = WatchItem()
        if watch_item is not None:
            self.editing_item.update_from(watch_item)
        else:
            self.editing_item.update_from(SAMPLE_WATCH_ITEM)
        self.init_dialog_by_watch_item()

        # save button delegate, receive an WatchItem param
        self.save_post_delegate: Optional[Callable] = None
        self.pushButtonSave.clicked.connect(self.on_click_save)
        self.pushButtonCancel.clicked.connect(self.on_click_cancel)

    def init_dialog_by_watch_item(self):
        self.lineEditName.setText(self.editing_item.name)
        self.lineEditPath.setText(self.editing_item.path)
        self.lineEditPrevStamp.setText(self.editing_item.prev_stamp)
        self.lineEditCurrStamp.setText(self.editing_item.curr_stamp)

    def on_click_save(self):
        self.editing_item.name = self.lineEditName.text()
        self.editing_item.path = self.lineEditPath.text()
        self.editing_item.prev_stamp = self.lineEditPrevStamp.text()
        self.editing_item.curr_stamp = self.lineEditCurrStamp.text()
        if self.save_post_delegate is not None:
            self.save_post_delegate(self.editing_item)
        self.close()

    def on_click_cancel(self):
        self.close()
