import re
import os
from abc import abstractmethod
from typing import Union

from PySide6 import QtGui
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QItemDelegate, QStyleOptionViewItem, \
    QWidget, QTableView, QPushButton, QHBoxLayout, QHeaderView, QMenu
from PySide6.QtCore import Qt, QAbstractTableModel, QSortFilterProxyModel, QModelIndex


class TableRowModel(object):

    def __init__(self):

        self.checked = True

        # if this line is enabled
        self.enable: bool = True

        # these col indexes will always be enabled
        self.always_enable_cols: list[int] = list[int]()

    # things to be show in table, len == table_cols
    @property
    @abstractmethod
    def display_data(self) -> list[any]:
        raise NotImplementedError()

    # data need to be connected
    @property
    @abstractmethod
    def hidden_data(self) -> any:
        raise NotImplementedError()

    def __getitem__(self, idx: int) -> any:
        return self.display_data[idx]

    def __setitem__(self, idx: int, value: any) -> None:
        self.display_data[idx] = value


class TableModel(QAbstractTableModel):

    def __init__(self, parent=None):
        super(TableModel, self).__init__(parent)

        self._rows: list[TableRowModel] = list[TableRowModel]()
        self._header: list[str] = list[str]()

    # return display raw data
    @property
    def raw_data(self) -> list[TableRowModel]:
        return self._rows

    @raw_data.setter
    def raw_data(self, rows: list[TableRowModel]) -> None:
        self._rows = rows

    # 清空数据
    def clear(self) -> None:
        self._rows.clear()

    # override super.data
    # get data by index (row, col)
    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> any:
        row = index.row()
        col = index.column()
        value = self._rows[row][col]
        if role == Qt.DisplayRole:
            if type(value) == bool:
                # bool value should be set as a checkbox
                return None
            elif type(value) == float and str(value)[::-1].find(".") > 2:
                # float type with given precision
                return "%.4f" % value
            else:
                # other type (int, str, ...) return raw value
                return value
        elif role == Qt.CheckStateRole and type(value) == bool:
            # bool value should be set as a checkbox
            return Qt.CheckState.Checked if self._rows[row][col] else Qt.CheckState.Unchecked

    # override super.setData
    # set value at index (row, col)
    # only for bool value
    def setData(self, index: QModelIndex, value: any, role: int = Qt.DisplayRole) -> bool:
        if not index.isValid():
            return False

        row = index.row()

        if role == Qt.CheckStateRole:
            # check state change
            self._rows[row].checked = not self._rows[row].checked
            # self.dataChanged.emit(index, index, [role])
            return True

        return False

    # override super.headerData
    # get header of every section
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> any:
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._header[section]
            elif orientation == Qt.Vertical:
                return "%d" % (section + 1)
        return super().headerData(section, orientation, role)

    # override super.rowCount
    # get row num
    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._rows)

    # override super.columnCount
    # get col num
    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._header)

    # TODO: sort will cause errors on cols with widgets
    # def sort(self, column: int, order: Qt.SortOrder = Qt.AscendingOrder) -> None:
    #     self.layoutAboutToBeChanged.emit()
    #     self.view_index_list.sort(
    #         key=lambda model_idx: self.raw_data[model_idx][column],
    #         reverse=(order != Qt.AscendingOrder)
    #     )
    #     self.layoutChanged.emit()
    #     self.dataChanged.emit(QModelIndex(), QModelIndex())

    # override super.flags
    # return flags of index (row, col)
    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return super().flags(index)

        row = index.row()
        col = index.column()

        # selectable & enable
        flags = Qt.ItemIsSelectable
        if self._rows[row].enable:
            flags |= Qt.ItemIsEnabled

        # cols that always enabled
        if self._rows[row].always_enable_cols is not None and col in self._rows[row].always_enable_cols:
            flags |= Qt.ItemIsEnabled

        # checkbox for bool cell
        if type(self._rows[row][col]) == bool:
            flags |= Qt.ItemIsUserCheckable

        return flags


class TableWrapper(object):

    def __init__(self, table_view: QTableView):
        # set table view and model
        self.table_view = table_view
        self.source_model = TableModel(table_view.parent())

        # connect table_model to table_view
        self.table_view.setModel(self.source_model)

        # init table setting
        self.init_table_setting()

        # double click signal
        self.table_view.doubleClicked.connect(self.on_double_click)
        self.double_click_row_delegate = None       # receive a TableRowModel as param
        self.double_click_cell_delegate = None      # receive a TableRowModel and col idx as param

    # init table setting
    def init_table_setting(self):
        self.stretch_last_column()

    # hide vertical header
    def hide_vertical_header(self, hide=True):
        self.table_view.verticalHeader().setHidden(hide)

    # auto stretch last column
    def stretch_last_column(self, enable=True):
        self.table_view.horizontalHeader().setStretchLastSection(enable)

    # set width of col
    def set_column_width(self, width: int, col: int = -1):
        header = self.table_view.horizontalHeader()
        if col < 0:
            # set default col width
            header.setDefaultSectionSize(width)
        else:
            header.resizeSection(col, width)

    # set auto col width
    def set_auto_column_width(self, col: int):
        header = self.table_view.horizontalHeader()
        header.setSectionResizeMode(col, QHeaderView.ResizeToContents)

    # set header
    def set_header(self, header: list[str]):
        self.source_model.layoutAboutToBeChanged.emit()
        self.source_model._header = header
        self.source_model.layoutChanged.emit()

    # get table column number
    @property
    def column_num(self) -> int:
        return self.source_model.columnCount()

    # get raw data from model
    @property
    def model_rows(self) -> list[TableRowModel]:
        return self.source_model.raw_data

    # insert line data
    # update_view = False: the table will not be updated immediately, self.refresh_view should be called later
    def append_line(self, row_data: TableRowModel, update_view=True) -> None:
        if update_view:
            self.source_model.layoutAboutToBeChanged.emit()

        self.source_model.raw_data.append(row_data)

        # refresh view
        if update_view:
            row = self.source_model.rowCount()
            col = self.source_model.columnCount()
            self.source_model.layoutChanged.emit()
            self.source_model.dataChanged.emit(
                self.source_model.createIndex(row, 0),
                self.source_model.createIndex(row, col - 1)
            )

    # refresh view
    def refresh_view(self):
        self.source_model.layoutAboutToBeChanged.emit()
        self.source_model.layoutChanged.emit()
        self.source_model.dataChanged.emit(
            self.source_model.createIndex(0, 0),
            self.source_model.createIndex(
                self.source_model.rowCount() - 1, self.source_model.columnCount() - 1
            )
        )

    # clear table data
    def clear(self):
        self.source_model.clear()
        self.refresh_view()

    # check all rows
    def select_all_rows(self, checked: bool = True):
        for row in self.model_rows:
            row.checked = checked

        self.refresh_view()

    # get checked rows
    def get_checked_rows(self) -> list[TableRowModel]:
        checked_rows: list[TableRowModel] = list[TableRowModel]()
        for row in self.model_rows:
            if not row.checked:
                # bool or other values
                continue

            checked_rows.append(row)

        return checked_rows

    # remove checked rows
    # return removed rows
    def remove_checked_rows(self) -> list[TableRowModel]:
        unchecked_rows: list[TableRowModel] = list[TableRowModel]()
        checked_rows: list[TableRowModel] = list[TableRowModel]()
        for row in self.model_rows:
            if row.checked:
                # bool or other values
                checked_rows.append(row)
            else:
                unchecked_rows.append(row)

        self.source_model.raw_data = unchecked_rows
        self.refresh_view()

        return checked_rows

    # double click event
    def on_double_click(self, index: QModelIndex):
        row_model = self.model_rows[index.row()]

        if self.double_click_row_delegate is not None:
            self.double_click_row_delegate(row_model)

        if self.double_click_cell_delegate is not None:
            self.double_click_cell_delegate(row_model, index.column())
