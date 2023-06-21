import os
import numpy as np
from typing import Callable, Union

from utils.version import is_release
from utils.wav_parser import WavInfo
from utils.p4 import P4Client, ChangeList, FileChangeInfo


CLEAN_MODE = True
DBFS_DIFF_THRESHOLD = 3.0
LUFS_DIFF_THRESHOLD = 3.0
MAX_DBFS_DIFF_THRESHOLD = 3.0


# file diff among versions
class FileDiffRecord(object):

    def __init__(self, path: str):
        self.path = path
        self.prev_rev_id: int = -1
        self.curr_rev_id: int = -1

    def version_forward(self, file_change_info: FileChangeInfo):

        if self.prev_rev_id == -1 or file_change_info.rev <= self.prev_rev_id:
            self.prev_rev_id = self.get_prev_rev_id(file_change_info.rev)

        if file_change_info.rev > self.curr_rev_id:
            self.curr_rev_id = file_change_info.rev

    @staticmethod
    def get_prev_rev_id(rev_id: int) -> int:
        return rev_id - 1 if rev_id > 0 else 0


# given a check function to check prev and curr wav info
# if check function return a not None value, then log the info
class CheckRule(object):

    def __init__(self, check_func: Callable[[WavInfo, WavInfo], any], log_header: str):
        self.check_func = check_func
        self.log_header = log_header
        self.log_info = list[str]()

    def check(self, prev_wav_info: WavInfo, curr_wav_info: WavInfo):
        result = self.check_func(prev_wav_info, curr_wav_info)
        if result is not None:
            self.log_info.append(str(result))

    def get_log(self) -> str:
        if len(self.log_info) == 0:
            return ""
        return "\n".join([self.log_header] + self.log_info)


# run check rules with file diff records
class DiffChecker(object):

    def __init__(self, clean_mode: bool = CLEAN_MODE):
        self.file_diff_record_map = dict[str, FileDiffRecord]()
        self.check_rules = list[CheckRule]()
        self.clean_mode = clean_mode

    # add check rules
    def add_rules(self, check_rules: list[CheckRule]):
        self.check_rules.extend(check_rules)

    # forward with change list
    def version_forward(self, change_list: ChangeList):
        for file_change_info in change_list.file_change_list:
            if file_change_info.depot_path not in self.file_diff_record_map:
                # build new record
                self.file_diff_record_map[file_change_info.depot_path] = FileDiffRecord(file_change_info.depot_path)

            # forward record
            self.file_diff_record_map[file_change_info.depot_path].version_forward(file_change_info)

    # load wav info of given rev id
    def load_wav_of_rev(self, p4_client: P4Client, depot_path: str, rev_id: int) -> WavInfo:
        wav_info = None
        if rev_id <= 0:
            wav_info = WavInfo()

        local_path = p4_client.sync_file_of_rev(depot_path, rev_id)
        if len(local_path) == 0 or not os.path.exists(local_path):
            wav_info = WavInfo()

        # wav file exist, try to load wav
        if wav_info is None:
            try:
                wav_info = WavInfo(local_path)
            except Exception as e:
                print("\n[Load wav]Failed to load wav info of %s#%d" % (depot_path, rev_id))
                print(e)
                wav_info = WavInfo()
            finally:
                if self.clean_mode:
                    p4_client.sync_file_of_rev(depot_path, 0)   # version 0 will clean local file
                else:
                    p4_client.sync_file_of_rev(depot_path)

        # set version info
        wav_info.depot_path = depot_path
        wav_info.rev_id = rev_id

        return wav_info

    # run checker
    def check(self, p4_client: P4Client, yield_path_flag: bool = False) -> list:
        for file_idx, file_diff_record in enumerate(self.file_diff_record_map.values()):
            prev_wav_info = self.load_wav_of_rev(p4_client, file_diff_record.path, file_diff_record.prev_rev_id)
            curr_wav_info = self.load_wav_of_rev(p4_client, file_diff_record.path, file_diff_record.curr_rev_id)
            for check_rule in self.check_rules:
                check_rule.check(prev_wav_info, curr_wav_info)
            if yield_path_flag:
                yield [file_idx, file_diff_record.path]

    def __len__(self):
        return len(self.file_diff_record_map)

    # get log
    def get_log(self) -> str:
        log_str = ""
        for rule in self.check_rules:
            rule_log = rule.get_log()
            if len(rule_log) > 0:
                log_str += rule_log + "\n\n"

        if log_str.endswith("\n\n"):
            log_str = log_str[:-2]

        return log_str


# resource changed rule
def resource_changed_rule(prev_wav_info: WavInfo, curr_wav_info: WavInfo) -> Union[str, None]:
    if not prev_wav_info.available and curr_wav_info.available:
        return "Added,#%d,#%d,%s" % (prev_wav_info.rev_id, curr_wav_info.rev_id, curr_wav_info.depot_path)
    if prev_wav_info.available and not curr_wav_info.available:
        return "Removed,#%d,#%d,%s" % (prev_wav_info.rev_id, curr_wav_info.rev_id, prev_wav_info.depot_path)
    if not prev_wav_info.available and not curr_wav_info.available:
        return None
    return "Changed,#%d,#%d,%s" % (prev_wav_info.rev_id, curr_wav_info.rev_id, curr_wav_info.depot_path)


# resource dBFS diff too large rule
def resource_dBFS_diff_rule(prev_wav_info: WavInfo, curr_wav_info: WavInfo) -> Union[str, None]:
    if not prev_wav_info.available or not curr_wav_info.available:
        return None

    prev_dBFS = float(np.mean(prev_wav_info.dBFS))
    curr_dBFS = float(np.mean(curr_wav_info.dBFS))
    if np.abs(curr_dBFS - prev_dBFS) >= DBFS_DIFF_THRESHOLD:
        return "%.2f,%.2f,%s" % (prev_dBFS, curr_dBFS, curr_wav_info.depot_path)
    return None


# resource max dBFS diff too large rule
def resource_max_dBFS_diff_rule(prev_wav_info: WavInfo, curr_wav_info: WavInfo) -> Union[str, None]:
    if not prev_wav_info.available or not curr_wav_info.available:
        return None

    prev_max_dBFS = float(np.mean(prev_wav_info.max_dBFS))
    curr_max_dBFS = float(np.mean(curr_wav_info.max_dBFS))
    if np.abs(curr_max_dBFS - prev_max_dBFS) >= MAX_DBFS_DIFF_THRESHOLD:
        return "%.2f,%.2f,%s" % (prev_max_dBFS, curr_max_dBFS, curr_wav_info.depot_path)
    return None


# resource channel diff rule
def resource_channel_diff_rule(prev_wav_info: WavInfo, curr_wav_info: WavInfo) -> Union[str, None]:
    if not prev_wav_info.available or not curr_wav_info.available:
        return None

    prev_channel = prev_wav_info.channels
    curr_channel = curr_wav_info.channels
    if prev_channel != curr_channel:
        return "%d,%d,%s" % (prev_channel, curr_channel, curr_wav_info.depot_path)
    return None
