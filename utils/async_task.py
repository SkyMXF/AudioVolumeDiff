from PySide6.QtCore import QThread, Signal


class AsyncTaskThread(QThread):
    signal_load_progress = Signal(float)    # emit当前进度，0.0-1.0
    signal_task_single_result = Signal(list)       # emit一次task结果
    signal_load_finish = Signal()

    def __init__(
        self,
        task_worker,    # python generator, 每次yield一行数据
        task_args: list,    # task_worker参数
        task_length: int,   # 任务长度，用于emit进度信息
        on_progress=None,       # progress更新响应
        on_task_result=None,    # task单次结果响应
        on_finish=None,         # 完成响应
        parent=None
    ):
        super(AsyncTaskThread, self).__init__(parent)

        self.task_worker = task_worker
        self.task_args = task_args
        self.task_length = task_length

        # 信号connect
        self.progress_emit_flag = False
        self.task_result_emit_flag = False
        self.finish_emit_flag = False
        if on_progress:
            self.progress_emit_flag = True
            self.signal_load_progress.connect(on_progress)
        if on_task_result:
            self.task_result_emit_flag = True
            self.signal_task_single_result.connect(on_task_result)
        if on_finish:
            self.finish_emit_flag = True
            self.signal_load_finish.connect(on_finish)

    def run(self) -> None:
        # progress更新signal
        curr_progress = 0.0
        progress_step = 1.0 / (self.task_length + 1e-6)
        progress_update_step = 0.05
        prev_progress = curr_progress - progress_update_step

        for data in self.task_worker(*self.task_args):

            # progress更新
            if self.progress_emit_flag:
                curr_progress += progress_step
                if curr_progress - prev_progress > progress_update_step - 1e-6:
                    prev_progress = curr_progress
                    self.signal_load_progress.emit(curr_progress)

            # emit task result
            self.send_data(data)

        self.end_task()

    # signal_task_single_result emit一次data
    def send_data(self, data: list):
        if self.task_result_emit_flag:
            if data is not None:    # 返回单个None时不发送
                self.signal_task_single_result.emit(data)

    # emit signal_load_finish信号
    def end_task(self):
        if self.finish_emit_flag:
            self.signal_load_finish.emit()

