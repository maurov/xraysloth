# coding: utf-8
# /*##########################################################################
# MIT License
#
# Copyright (c) 2018 DAXS developers.
# All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/
from __future__ import absolute_import, division

__authors__ = ['Marius Retegan']
__license__ = 'MIT'


from silx.gui import qt


class ComboBoxDelegate(qt.QStyledItemDelegate):

    def __init__(self, parent=None):
        super(ComboBoxDelegate, self).__init__(parent=parent)

    def createEditor(self, parent, option, index):
        editor = qt.QComboBox(parent)
        editor.setMinimumHeight(25)
        editor.currentIndexChanged.connect(self.commitDataAndClose)
        return editor

    def setEditorData(self, editor, index):
        model = index.model()
        values = model.data(index, qt.Qt.EditRole)
        currentText = model.data(index, qt.Qt.DisplayRole)
        editor.blockSignals(True)
        editor.addItems(values)
        editor.setCurrentText(currentText)
        editor.blockSignals(False)

    def setModelData(self, editor, model, index):
        value = editor.currentText()
        model.setData(index, value, qt.Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def commitDataAndClose(self):
        editor = self.sender()
        self.commitData.emit(editor)
        self.closeEditor.emit(editor)
