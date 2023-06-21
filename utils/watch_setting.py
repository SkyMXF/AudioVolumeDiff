import json
from collections import OrderedDict


class WatchItem(object):

    # name: name of the path (e.g. "Dev_Normal")
    # path: depot path
    # prev_stamp or curr_stamp:
    # P4 change ID (e.g. 2262400) or time (e.g. 2023/3/16:19:00:00) of previous/current version.
    def __init__(
        self,
        name: str = "",
        path: str = "",
        prev_stamp: str = "",
        curr_stamp: str = "",
    ):
        self.name: str = name
        self.path: str = path
        self.prev_stamp: str = prev_stamp
        self.curr_stamp: str = curr_stamp

    def to_dict(self) -> OrderedDict:
        od = OrderedDict()
        od["name"] = self.name
        od["path"] = self.path
        od["prev_stamp"] = self.prev_stamp
        od["curr_stamp"] = self.curr_stamp
        return od

    def from_dict(self, od: OrderedDict):
        if "name" in od:
            self.name = od["name"]
        if "path" in od:
            self.path = od["path"]
        if "prev_stamp" in od:
            self.prev_stamp = od["prev_stamp"]
        if "curr_stamp" in od:
            self.curr_stamp = od["curr_stamp"]

    def update_from(self, sample: "WatchItem"):
        self.name = sample.name
        self.path = sample.path
        self.prev_stamp = sample.prev_stamp
        self.curr_stamp = sample.curr_stamp


class WatchSetting(object):

    def __init__(self):
        self.watch_item_list: list[WatchItem] = list[WatchItem]()
        self.dbfs_diff_thres: float = 3.0
        self.max_dbfs_diff_thres: float = 3.0
        self.disable_clean_mode: bool = True
        self.p4_server: str = ""
        self.p4_workspace_name: str = ""
        self.output_dir = "results"

    def from_dict(self, od: OrderedDict):
        if "watch_item_list" in od:
            self.watch_item_list = [WatchItem(**item) for item in od["watch_item_list"]]
        if "dbfs_diff_thres" in od:
            self.dbfs_diff_thres = od["dbfs_diff_thres"]
        if "max_dbfs_diff_thres" in od:
            self.max_dbfs_diff_thres = od["max_dbfs_diff_thres"]
        if "disable_clean_mode" in od:
            self.disable_clean_mode = od["disable_clean_mode"]
        if "p4_server" in od:
            self.p4_server = od["p4_server"]
        if "p4_workspace_name" in od:
            self.p4_workspace_name = od["p4_workspace_name"]
        if "output_dir" in od:
            self.output_dir = od["output_dir"]

    def to_dict(self) -> OrderedDict:
        od = OrderedDict()
        od["watch_item_list"] = [item.to_dict() for item in self.watch_item_list]
        od["dbfs_diff_thres"] = self.dbfs_diff_thres
        od["max_dbfs_diff_thres"] = self.max_dbfs_diff_thres
        od["disable_clean_mode"] = self.disable_clean_mode
        od["p4_server"] = self.p4_server
        od["p4_workspace_name"] = self.p4_workspace_name
        od["output_dir"] = self.output_dir
        return od

    def from_json(self, path: str):
        with open(path, "r") as f:
            od = json.load(f, object_pairs_hook=OrderedDict)
            self.from_dict(od)

    def to_json(self, path: str):
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=4)
