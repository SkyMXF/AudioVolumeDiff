import re
import os
from typing import Union
from P4 import P4, P4Exception


P4_SERVER = ""
P4_WORKSPACE_NAME = ""
TIME_STAMP_REGEX = re.compile(r"\d{1,4}/\d{1,2}/\d{1,2}:\d{1,2}:\d{1,2}:\d{1,2}")
P4_WORKSPACE_ROOT, curr_base = os.path.split(os.getcwd())
while curr_base != "Dev" and len(curr_base) > 0 and len(P4_WORKSPACE_ROOT) > 0:
    P4_WORKSPACE_ROOT, curr_base = os.path.split(P4_WORKSPACE_ROOT)
if curr_base != "Dev":
    P4_WORKSPACE_ROOT = ""


# file change info in change list of p4
class FileChangeInfo(object):

    def __init__(
        self,
        depot_path: str,
        action: str,
        file_type: str,
        rev: int,
    ):
        self.depot_path = depot_path
        self.action = action
        self.file_type = file_type
        self.rev = rev


# change list info of p4
class ChangeList(object):

    def __init__(self, p4_change_dict: dict):
        self.id: int = -1
        # self.status = ""
        self.file_change_list = list[FileChangeInfo]()

        self._parse_p4_change_dict(p4_change_dict)

    def __hash__(self):
        return hash(self.id)

    def _parse_p4_change_dict(self, p4_change_dict: dict):
        self.id = int(p4_change_dict["change"])
        # self.status = p4_change_dict["status"]
        for file_idx in range(len(p4_change_dict["depotFile"])):
            self.file_change_list.append(
                FileChangeInfo(
                    p4_change_dict["depotFile"][file_idx],
                    p4_change_dict["action"][file_idx],
                    p4_change_dict["type"][file_idx],
                    int(p4_change_dict["rev"][file_idx]),
                )
            )

    # remove file change info if out of dir
    def path_filter(self, dir_path: str):
        new_file_change_list = list[FileChangeInfo]()
        for file_change_info in self.file_change_list:
            if file_change_info.depot_path.startswith(dir_path):
                new_file_change_list.append(file_change_info)
        self.file_change_list = new_file_change_list

    # remove file with other ext
    def ext_filter(self, ext: str):
        new_file_change_list = list[FileChangeInfo]()
        for file_change_info in self.file_change_list:
            if file_change_info.depot_path.endswith(ext):
                new_file_change_list.append(file_change_info)
        self.file_change_list = new_file_change_list


class P4Client(object):

    def __init__(
        self,
        port: str = P4_SERVER,
        user: str = "",
        password: str = "",
        workspace_name: str = P4_WORKSPACE_NAME,
        charset: str = "utf8",
        workspace_root: str = P4_WORKSPACE_ROOT,
    ):
        self.p4 = P4()
        self.p4.port = port
        self.p4.user = user
        self.p4.password = password
        self.p4.client = workspace_name
        self.p4.charset = charset
        self.p4.connect()
        if len(workspace_name) == 0 and len(workspace_root) > 0:
            # workspace name is empty, get workspace name by workspace root
            self._set_workspace_info(workspace_root)

    # set self._client.client info
    # get workspace name by workspace root
    def _set_workspace_info(self, workspace_root: str) -> None:
        # get current(default) client info
        curr_client_info = self.p4.run("info")[0]
        curr_host = curr_client_info["clientHost"]  # current computer name

        # get info of all user clients
        user_client_infos = self.p4.run("clients", "--me")
        for client_info in user_client_infos:
            if client_info["Host"] == curr_host:
                # is client on current computer
                if os.path.abspath(client_info["Root"]) == os.path.abspath(workspace_root):
                    # is client of given workspace_root
                    self.p4.client = client_info["client"]
                    return

        print("[WARNING]Cannot found workspace matched with root '%s'." % workspace_root)

    def get_changes_of_dir(
        self,
        base_dir: str,
        begin_stamp: str = "",
        end_stamp: str = "",
        file_ext: str = ""
    ) -> list[ChangeList]:
        # turn stamp to id or time
        begin_id, end_id, begin_time, end_time = "", "", "", ""
        if len(begin_stamp) > 0:
            if begin_stamp.isdigit():
                begin_id = begin_stamp
            elif TIME_STAMP_REGEX.match(begin_stamp) is not None:
                begin_time = begin_stamp
            else:
                raise ValueError("Invalid begin stamp: '%s'" % begin_stamp)
        if len(end_stamp) > 0:
            if end_stamp.isdigit():
                end_id = end_stamp
            elif TIME_STAMP_REGEX.match(end_stamp) is not None:
                end_time = end_stamp
            else:
                raise ValueError("Invalid end stamp: '%s'" % end_stamp)

        # get change list
        return self._get_changes_of_dir(
            base_dir=base_dir,
            begin_id=begin_id,
            end_id=end_id,
            begin_time=begin_time,
            end_time=end_time,
            file_ext=file_ext
        )

    def _get_changes_of_dir(
        self,
        base_dir: str,
        begin_id: str = "",
        end_id: str = "",
        begin_time: str = "",
        end_time: str = "",
        file_ext: str = ""
    ) -> list[ChangeList]:

        # change id condition cmd string
        begin_id_cmd = begin_id if len(begin_id) > 0 else ""
        end_id = int(end_id) if len(end_id) > 0 else int('0x7fffffff', 16)

        # time condition cmd string
        if len(begin_time) > 0 and TIME_STAMP_REGEX.match(begin_time) is None:
            raise ValueError("Invalid begin time: '%s'" % begin_time)
        if len(end_time) > 0 and TIME_STAMP_REGEX.match(end_time) is None:
            raise ValueError("Invalid end time: '%s'" % end_time)
        if len(begin_time) > 0 and len(end_time) > 0:
            time_condition_cmd = "@%s,%s" % (begin_time, end_time)
        elif len(begin_time) > 0:
            time_condition_cmd = "@%s,@now" % begin_time
        elif len(end_time) > 0:
            time_condition_cmd = "@%s" % end_time
        else:
            time_condition_cmd = ""

        change_lists = list[ChangeList]()

        # base_dir -> base_dir/...
        p4_check_path = os.path.join(base_dir, "...").replace("\\", "/")

        # run p4 command
        if len(begin_id_cmd) > 0:
            results = self.p4.run("changes", "-e", begin_id_cmd, "%s%s" % (p4_check_path, time_condition_cmd))
        else:
            results = self.p4.run("changes", "%s%s" % (p4_check_path, time_condition_cmd))

        # parse results
        for p4_change_info in results:
            change_id = int(p4_change_info["change"])
            if change_id >= end_id:
                continue
            change_list = self.get_change_info_by_id(change_id)
            change_list.path_filter(base_dir)
            if len(file_ext) > 0:
                change_list.ext_filter(file_ext)
            if change_list is not None and len(change_list.file_change_list) > 0:
                change_lists.append(change_list)

        return change_lists

    def get_change_info_by_id(self, change_id: int) -> Union[ChangeList, None]:
        change_list = None
        try:
            p4_change_dict = self.p4.run("describe", change_id)
            if type(p4_change_dict) != list or len(p4_change_dict) != 1:
                raise P4Exception("Invalid p4 change dict for change id: %d" % change_id)
            change_list = ChangeList(p4_change_dict[0])
        except P4Exception as e:
            print("=========Capture an error from P4=========")
            print(e)

        return change_list

    def sync_file_of_rev(self, path: str, rev_id: int = -1) -> str:
        try:
            with self.p4.at_exception_level(P4.RAISE_ERRORS):
                if rev_id == -1:
                    self.p4.run("sync", path)
                else:
                    self.p4.run("sync", "%s#%d" % (path, rev_id))
                # get local path
                local_path = self.p4.run("where", path)[0]["path"]
            return local_path
        except P4Exception as e:
            print("=========Capture an error from P4=========")
            print(e)
            return ""
