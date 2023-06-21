# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.4.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QMainWindow, QProgressBar,
    QPushButton, QSizePolicy, QSpacerItem, QTableView,
    QTextEdit, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1234, 749)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_2 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setPointSize(16)
        self.label.setFont(font)

        self.horizontalLayout.addWidget(self.label)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.checkBoxSelectAll = QCheckBox(self.centralwidget)
        self.checkBoxSelectAll.setObjectName(u"checkBoxSelectAll")
        font1 = QFont()
        font1.setPointSize(11)
        self.checkBoxSelectAll.setFont(font1)

        self.horizontalLayout_2.addWidget(self.checkBoxSelectAll)

        self.horizontalSpacer_2 = QSpacerItem(100, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.pushButtonAddPath = QPushButton(self.centralwidget)
        self.pushButtonAddPath.setObjectName(u"pushButtonAddPath")
        self.pushButtonAddPath.setMinimumSize(QSize(200, 0))
        self.pushButtonAddPath.setMaximumSize(QSize(180, 16777215))
        self.pushButtonAddPath.setFont(font1)

        self.horizontalLayout_2.addWidget(self.pushButtonAddPath)

        self.pushButtonRemoveSelected = QPushButton(self.centralwidget)
        self.pushButtonRemoveSelected.setObjectName(u"pushButtonRemoveSelected")
        self.pushButtonRemoveSelected.setMinimumSize(QSize(200, 0))
        self.pushButtonRemoveSelected.setMaximumSize(QSize(180, 16777215))
        self.pushButtonRemoveSelected.setFont(font1)

        self.horizontalLayout_2.addWidget(self.pushButtonRemoveSelected)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.tableView = QTableView(self.centralwidget)
        self.tableView.setObjectName(u"tableView")

        self.verticalLayout.addWidget(self.tableView)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setFont(font1)

        self.horizontalLayout_4.addWidget(self.label_2)

        self.lineEditOutputPath = QLineEdit(self.centralwidget)
        self.lineEditOutputPath.setObjectName(u"lineEditOutputPath")
        self.lineEditOutputPath.setMinimumSize(QSize(500, 0))
        self.lineEditOutputPath.setFont(font1)
        self.lineEditOutputPath.setDragEnabled(True)
        self.lineEditOutputPath.setReadOnly(True)

        self.horizontalLayout_4.addWidget(self.lineEditOutputPath)


        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.pushButtonOpenOutput = QPushButton(self.centralwidget)
        self.pushButtonOpenOutput.setObjectName(u"pushButtonOpenOutput")
        self.pushButtonOpenOutput.setMinimumSize(QSize(200, 0))
        self.pushButtonOpenOutput.setFont(font1)

        self.horizontalLayout_3.addWidget(self.pushButtonOpenOutput)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_3)

        self.progressBar = QProgressBar(self.centralwidget)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setMinimumSize(QSize(600, 0))
        self.progressBar.setFont(font1)
        self.progressBar.setValue(24)

        self.horizontalLayout_3.addWidget(self.progressBar)

        self.pushButtonCheck = QPushButton(self.centralwidget)
        self.pushButtonCheck.setObjectName(u"pushButtonCheck")
        self.pushButtonCheck.setMinimumSize(QSize(250, 0))
        self.pushButtonCheck.setFont(font1)

        self.horizontalLayout_3.addWidget(self.pushButtonCheck)


        self.verticalLayout.addLayout(self.horizontalLayout_3)


        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.textEdit = QTextEdit(self.centralwidget)
        self.textEdit.setObjectName(u"textEdit")
        self.textEdit.setMinimumSize(QSize(0, 200))
        self.textEdit.setMaximumSize(QSize(16777215, 200))
        self.textEdit.setFont(font1)
        self.textEdit.setTextInteractionFlags(Qt.TextSelectableByKeyboard|Qt.TextSelectableByMouse)

        self.verticalLayout_2.addWidget(self.textEdit)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"FFAudioResourcesChecker", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"FF Audio Resources Checker", None))
        self.checkBoxSelectAll.setText(QCoreApplication.translate("MainWindow", u"Select All", None))
        self.pushButtonAddPath.setText(QCoreApplication.translate("MainWindow", u"Add Path", None))
        self.pushButtonRemoveSelected.setText(QCoreApplication.translate("MainWindow", u"Remove Selected", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Output Folder", None))
        self.pushButtonOpenOutput.setText(QCoreApplication.translate("MainWindow", u"Open Output Folder", None))
        self.pushButtonCheck.setText(QCoreApplication.translate("MainWindow", u"Check Selected Path(s)", None))
    # retranslateUi

