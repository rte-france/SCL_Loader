from PyQt5.QtWidgets import QMainWindow, QApplication, QTreeWidgetItem
from PyQt5 import QtCore
import sys
import treewidgetwindow as treewidget


class widgetwindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = treewidget.Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.pushButton_edit.clicked.connect(self.add_items)

    def add_items(self):
        rowcount = self.ui.treeWidget.topLevelItemCount()
        self.ui.treeWidget.addTopLevelItem(QTreeWidgetItem(rowcount))
        self.ui.treeWidget.topLevelItem(rowcount).setText(0, 'Lincoln a good boy')
        self.ui.treeWidget.topLevelItem(rowcount).setCheckState(0, QtCore.Qt.Unchecked)
        self.ui.treeWidget.topLevelItem(rowcount).setFlags(
            self.ui.treeWidget.topLevelItem(rowcount).flags() | QtCore.Qt.ItemIsUserCheckable)
        self.ui.treeWidget.topLevelItem(rowcount).setText(1, 'He added a second column')
        self.ui.treeWidget.topLevelItem(rowcount).setTextAlignment(0, QtCore.Qt.AlignHCenter)
        self.ui.treeWidget.topLevelItem(rowcount).setTextAlignment(1, QtCore.Qt.AlignHCenter)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = widgetwindow()
    w.show()
    sys.exit(app.exec_())