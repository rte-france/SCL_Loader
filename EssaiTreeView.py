
from PyQt5.QtWidgets import QMainWindow,QApplication,QDesktopWidget,QVBoxLayout,QHBoxLayout, QTableWidget, QTreeWidgetItem
from PyQt5.QtWidgets import QFileDialog,QTableView,QWidget,QTreeWidget, QPushButton,QFrame,QCheckBox,QTreeView,QMessageBox
from PyQt5.Qt        import QStandardItemModel, QStandardItem, QThread, Qt
from PyQt5.QtGui import QFont, QColor

import sys

def MainWindow():
#    app     = QApplication(sys.argv)
    tree    = QTreeWidget()
    headerItem  = QTreeWidgetItem()
    item    = QTreeWidgetItem()

    for i in range(3):
        parent = QTreeWidgetItem(tree)
        parent.setText(0, "Parent {}".format(i))


        for x in range(5):
            child = QTreeWidgetItem(parent)
            child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
            child.setText(0, "Child {}".format(x))
            child.setCheckState(0, Qt.Unchecked)
    tree.show() 
    sys.exit(app.exec_())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    Win = MainWindow()
    demo = Win.AppDemo('SCL_files\SCD_SITE_20200928.scd')
    sys.exit(app.exec_())
