from typing import ClassVar
import os
from binaryornot.check import is_binary
import pandas 
import openpyxl
import filetype
import uuid
import xml.dom.minidom as md
import xml.parsers

'''
Write a program to update/create a text file.

Program should be written using class in python.

Program should have exception handling.

Should develop the same program using minimum 2-3 different python modules.

--------------------------------------------------------------------------------

Write a program to create/update an Excel file.

Program should be written using class in python.

Program should have exception handling.

Should develop the same program using minimum 2-3 different python modules.

--------------------------------------------------------------------------------

Write a program to create/update a xml file.

Program should be written using class in python.

Program should have exception handling.

Should develop the same program using minimum 2-3 different python modules.
'''


# https://support.microsoft.com/en-au/office/file-formats-that-are-supported-in-excel-0943ff2c-6014-4e8d-aaea-b83d51d46247
# https://pypi.org/project/filetype/
# https://stackoverflow.com/questions/42778784/abstract-classes-with-varying-amounts-of-parameters

# https://pythonbasics.org/write-excel/

# with open closes file if an exception occurs

from abc import ABC, abstractmethod 

class FileEditor(ABC):

    file_signature: str
    file_extensions: list[str]

    @abstractmethod
    def create(self, path, name):
        pass

    @abstractmethod
    def update(self, filepath, content):
        pass

    @abstractmethod
    def verify_file_extension(self, filepath):
        pass

    @abstractmethod
    def verify_file_signature(self, filepath):
        pass


class TextFileEditor(FileEditor):

    file_signature = ""
    file_extensions = ["txt"]

    def create(self, path ,name):
        # check dir exists 

        if not os.path.isdir(path):
            raise FileNotFoundError("directory does not exist")

        # check legal file name (file ext not necessary but will do)
        
        file_name_split = name.split('.')

        if len(file_name_split) != 2 or file_name_split[1] not in TextFileEditor.file_extensions:
            raise ValueError("invalid filename, .txt extension required")

        file_path = os.path.join(path, name)

        # create file

        try:
            with open(file_path, 'x') as f:
                pass
        except FileExistsError:
            print("could not create file, already exists")


    def update(self, filepath, content):
        
        if not os.path.isfile(filepath):
            raise FileNotFoundError("file does not exists")

        if is_binary(filepath):
            raise ValueError("provided file is binary, text file required")

        content = content.strip() + " \n"

        with open(filepath, 'a') as f:
            f.write(content)


    def verify_file_extension(self, filepath):
        pass
        # move to main class as non abstract method for all ?

    def verify_file_signature(self, filepath):
        pass

# .xlsx
class ExcelFileEditor(FileEditor):

    file_signature = ""
    file_extensions = ["xlsx", "xlsm"]     # use list, more types ? TODO

    def create(self, path, name):
        if not os.path.isdir(path):
            raise FileNotFoundError("directory does not exist")
        
        file_name_split = name.split('.')

        if len(file_name_split) != 2 or file_name_split[1] not in ExcelFileEditor.file_extensions:      # limit to xlsx ? check reqs
            raise ValueError("invalid filename, .xlsx extension required")

        file_path = os.path.join(path, name)

        df = pandas.DataFrame()

        # todo: check what if file exists

        df.to_excel(file_path, index=False, header=False)


    # two sheets in excel can't have the same name
    def update(self, filepath, data, sheet_id):

        if not isinstance(data, pandas.DataFrame):
            raise TypeError("data is required to be a pandas DataFrame")

        if not os.path.isfile(filepath):
            raise FileNotFoundError("file does not exists")

        file_type = filetype.guess_extension(filepath)

        if file_type:
            if file_type not in ExcelFileEditor.file_extensions:
                raise ValueError("file type not accepted")
        else:
            raise ValueError("file type indeterminate")

        # https://openpyxl.readthedocs.io/en/stable/_modules/openpyxl/utils/exceptions.html#InvalidFileException

        with pandas.ExcelWriter(filepath) as w:
            try:
                w.book = openpyxl.load_workbook(filepath)
                data.to_excel(w, sheet_name=sheet_id)
            except (IllegalCharacterError, SheetTitleException, InvalidFileException, ReadOnlyWorkbookException) as error:
                print(error)

    def verify_file_extension(self, filepath):
        pass

    def verify_file_signature(self, filepath):
        pass


# creating XML document without Document Type Definition
# https://bspaans.github.io/python-mingus/_modules/xml/dom/minidom.html
# https://github.com/python/cpython/blob/main/Lib/xml/dom/expatbuilder.pys
class XMLFileEditor(FileEditor):

    file_signature = ""
    file_extensions = ["xml"]

    def create(self, path, name, xml_root):
        if not os.path.isdir(path):
            raise FileNotFoundError("directory does not exist")
        
        file_name_split = name.split('.')

        if len(file_name_split) != 2 or file_name_split[1] not in XMLFileEditor.file_extensions:   
            raise ValueError("invalid filename, .xml extension required")

        file_path = os.path.join(path, name)

        if os.path.isfile(file_path):
            raise FileExistsError("could not create file, already exists")

        #xml_document = md.getDOMImplementation().createDocument(None, 'root', None)

        xml_document = md.Document()

        #root = xml_document.createElement("User")
        #root.setAttribute( "id", 'myIdvalue' )
        #root.setAttribute( "email", 'blabla@bblabla.com' )
 
        #xml_document.appendChild(root)

        
        root_element = xml_document.createElement(xml_root)

        xml_document.appendChild(root_element)
        #text = xml_document.createTextNode("")
        #root_element.appendChild(text)


        #productChild = xml_document.createElement('connection')
        #productChild.setAttribute('formatted-name', 'Federated') 
        #productChild.setAttribute('inline', 'true') 
        #root_element.appendChild(productChild)

        '''
        root_element = xml_document.createElement("tree")

        xml_document.appendChild(root_element)

        
        productChild = xml_document.createElement('connection')
        productChild.setAttribute('formatted-name', 'Federated') 
        productChild.setAttribute('inline', 'true') 
        root_element.appendChild(productChild)

        text = xml_document.createTextNode("boo")
        productChild.appendChild(text)
        '''

        xml_content = xml_document.toprettyxml(indent='\t')

        with open(file_path, 'w') as f:
            f.write(xml_content)


    def update(self, filepath, element_name, element_text):

        # updating restricted to adding elements that contain to the root element
        # due to time reasons

        if not os.path.isfile(filepath):
            raise FileNotFoundError("file does not exists")
        
        if is_binary(filepath):
            raise ValueError("provided file is binary, text file required")

        with open(filepath, 'r') as f:
            file_content = f.read()
        
        try:
            content_dom = md.parseString(file_content)
        except xml.parsers.expat.ExpatError as error:
            print(error)


        root_element = content_dom.documentElement
        new_element = content_dom.createElement(element_name)
        new_element_text = content_dom.createTextNode(element_text)
        root_element.appendChild(new_element)
        new_element.appendChild(new_element_text)

        xml_content = content_dom.toprettyxml(indent='\t')

        with open(filepath, 'w') as f:
            f.write(xml_content)


    def verify_file_extension(self, filepath):
        pass

    def verify_file_signature(self, filepath):
        pass


if __name__ == "__main__":
    '''
    d = ExcelFileEditor()
    d.create("/home/patrick/Desktop/KPIT", "file.xlsx")

    d.update("/home/patrick/Desktop/KPIT/file.xlsx", "Hi")
    '''

    d = XMLFileEditor()
    d.create("/home/patrick/Desktop/KPIT", "file.xml", "Tree")  
    d.update("/home/patrick/Desktop/KPIT/file.xml", "fruit", "grape")

    # TODO:

    '''
    def createTextNode(self, data):
        if not isinstance(data, StringTypes):
            raise TypeError, "node contents must be a string"
    '''