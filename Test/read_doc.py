# -*- coding: utf-8 -*-
# @Date    : 2022-08-26 09:45
# @Author  : chenxuepeng
import docx
import os.path
from win32com.client import Dispatch, DispatchEx

def doc_to_docx(path):
    docPath = path
    # wordApp = DispatchEx('Word.Application')
    wordApp = Dispatch('Word.Application')
    # 设置word不显示
    wordApp.Visible = 0
    wordApp.DisplayAlerts = 0
    docxPath = os.path.splitext(docPath)[0] + '.docx'
    doc = wordApp.Documents.Open(docPath)
    doc.SaveAs(docxPath, 12, False, '', True, '', False, False, False, False)
    print('success:doc to docx')
    doc.Close()
    wordApp.Quit()

def read_doc(path):
    text = ''
    file = docx.Document(path)
    for para in file.paragraphs:
        text += para.text
    return text

# doc_to_docx('C:\Pythonproject\work_file\Test\\20150901171427591.doc')
print(read_doc('20150901171427591.docx'))