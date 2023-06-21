# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'watch_item_dialog.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QFormLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_WatchItemEditDialog(object):
    def setupUi(self, WatchItemEditDialog):
        if not WatchItemEditDialog.objectName():
            WatchItemEditDialog.setObjectName(u"WatchItemEditDialog")
        WatchItemEditDialog.resize(768, 155)
        self.verticalLayout = QVBoxLayout(WatchItemEditDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.label = QLabel(WatchItemEditDialog)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setPointSize(11)
        self.label.setFont(font)

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label)

        self.lineEditName = QLineEdit(WatchItemEditDialog)
        self.lineEditName.setObjectName(u"lineEditName")
        self.lineEditName.setFont(font)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.lineEditName)

        self.label_2 = QLabel(WatchItemEditDialog)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setFont(font)

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_2)

        self.lineEditPath = QLineEdit(WatchItemEditDialog)
        self.lineEditPath.setObjectName(u"lineEditPath")
        self.lineEditPath.setFont(font)

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.lineEditPath)

        self.label_3 = QLabel(WatchItemEditDialog)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setFont(font)

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_3)

        self.lineEditPrevStamp = QLineEdit(WatchItemEditDialog)
        self.lineEditPrevStamp.setObjectName(u"lineEditPrevStamp")
        self.lineEditPrevStamp.setFont(font)

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.lineEditPrevStamp)

        self.label_4 = QLabel(WatchItemEditDialog)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setFont(font)

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.label_4)

        self.lineEditCurrStamp = QLineEdit(WatchItemEditDialog)
        self.lineEditCurrStamp.setObjectName(u"lineEditCurrStamp")
        self.lineEditCurrStamp.setFont(font)

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.lineEditCurrStamp)


        self.verticalLayout.addLayout(self.formLayout)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.pushButtonSave = QPushButton(WatchItemEditDialog)
        self.pushButtonSave.setObjectName(u"pushButtonSave")
        self.pushButtonSave.setMinimumSize(QSize(130, 0))
        self.pushButtonSave.setFont(font)

        self.horizontalLayout.addWidget(self.pushButtonSave)

        self.pushButtonCancel = QPushButton(WatchItemEditDialog)
        self.pushButtonCancel.setObjectName(u"pushButtonCancel")
        self.pushButtonCancel.setMinimumSize(QSize(80, 0))
        self.pushButtonCancel.setFont(font)

        self.horizontalLayout.addWidget(self.pushButtonCancel)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(WatchItemEditDialog)

        QMetaObject.connectSlotsByName(WatchItemEditDialog)
    # setupUi

    def retranslateUi(self, WatchItemEditDialog):
        WatchItemEditDialog.setWindowTitle(QCoreApplication.translate("WatchItemEditDialog", u"Watch Item Info", None))
        self.label.setText(QCoreApplication.translate("WatchItemEditDialog", u"Name", None))
        self.label_2.setText(QCoreApplication.translate("WatchItemEditDialog", u"Depot Path", None))
        self.label_3.setText(QCoreApplication.translate("WatchItemEditDialog", u"Previous Stamp", None))
        self.label_4.setText(QCoreApplication.translate("WatchItemEditDialog", u"Current Stamp", None))
        self.pushButtonSave.setText(QCoreApplication.translate("WatchItemEditDialog", u"Save", None))
        self.pushButtonCancel.setText(QCoreApplication.translate("WatchItemEditDialog", u"Cancel", None))
    # retranslateUi

