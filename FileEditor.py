from abc import ABC, abstractmethod 
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


# goals: cross operating system, extensibility, DRY

# strict file extension requirements

# notes

# functionality and limitations (only xlsx, only adding xml elements with text one level deep, only appending to text file)

# TODO: type hints
# TODO: consistent underscores


class FileEditor(ABC):

    file_extensions: list[str]

    @abstractmethod
    def create(self, path, name):
        pass

    @abstractmethod
    def update(self, filepath, content):
        pass

    @abstractmethod
    def file_validation_function():
        pass

    '''
    @abstractmethod
    def verify_file_signature(self, file_validation_function, filepath, file_extensions):
        if file_validation_function(file_path, file_extensions):
            return True
    '''

    def verify_file_extension(self, file_name, file_extensions):
        file_name_split = file_name.split('.')

        extension_str = ",".join(str(element) for element in file_extensions)

        if len(file_name_split) != 2 or file_name_split[1] not in file_extensions:
            raise ValueError("invalid filename, valid extensions: " + extension_str)

        else:
            return True
        
    def verify_file_signature(file_validation_function, file_path, file_extensions):



class TextFileEditor(FileEditor):

    file_extensions = ["txt"]

    def create(self, path, file_name):

        # check dir exists 

        if not os.path.isdir(path):
            raise FileNotFoundError("directory does not exist")

        # check file extension

        '''
        file_name_split = file_name.split('.')

        if len(file_name_split) != 2 or file_name_split[1] not in TextFileEditor.file_extensions:
            raise ValueError("invalid filename, .txt extension required")
        '''

        if verify_file_extension(file_name, TextFileEditor.file_extensions):
            
            # create file

            file_path = os.path.join(path, file_name)

            try:
                with open(file_path, 'x') as f:
                    pass
            except FileExistsError:
                print("could not create file, already exists")


    def update(self, filepath, content):
        
        # check file exists 

        if not os.path.isfile(filepath):
            raise FileNotFoundError("file does not exists")

        # check file extension and that file is not binary

        '''
        file_name_split = os.path.split(filepath)[1].split(".")

        if len(file_name_split) != 2 or file_name_split[1] not in TextFileEditor.file_extensions:
            raise ValueError("invalid filename, .txt extension required")

        if is_binary(filepath):
            raise ValueError("provided file is binary, text file required")
        '''

        if verify_file_signature(is_binary, filepath, TextFileEditor.file_extensions):

            # add content

            content = content.strip() + " \n"

            with open(filepath, 'a') as f:
                f.write(content)

    '''
    def file_validation_function2(filepath, file_extensions):
        file_name_split = os.path.split(filepath)[1].split(".")

        if len(file_name_split) != 2 or file_name_split[1] not in file_extensions:
            raise ValueError("invalid filename, .txt extension required")

        if is_binary(filepath):
            raise ValueError("provided file is binary, text file required")
        
        return True
    '''

    def file_validation_function(filepath, file_extensions):
        if is_binary(filepath):
            raise ValueError("provided file is binary, text file required")
        else:
            return True


class ExcelFileEditor(FileEditor):

    file_extensions = ["xlsx", "xlsm"]     # use list, more types ? TODO

    def create(self, path, file_name):
        
        # check that dir exists

        if not os.path.isdir(path):
            raise FileNotFoundError("directory does not exist")
        
        # validate file name
        
        '''
        file_name_split = file_name.split('.')

        if len(file_name_split) != 2 or file_name_split[1] not in ExcelFileEditor.file_extensions:      # TODO: limit to xlsx ? check reqs
            raise ValueError("invalid filename, .xlsx extension required")
        '''

        if verify_file_extension(file_name, TextFileEditor.file_extensions):

            # create file

            file_path = os.path.join(path, file_name)

            df = pandas.DataFrame()

            # TODO: check what if file exists

            df.to_excel(file_path, index=False, header=False)


    # TODO: two sheets in excel can't have the same name
    def update(self, filepath, data, sheet_id):

        # check that data is DataFrame object

        if not isinstance(data, pandas.DataFrame):
            raise TypeError("data is required to be a pandas DataFrame")

        # check that file exists and file signature is valid

        if not os.path.isfile(filepath):
            raise FileNotFoundError("file does not exists")

        file_type = filetype.guess_extension(filepath)

        if file_type:
            if file_type not in ExcelFileEditor.file_extensions:
                raise ValueError("file type not accepted")
        else:
            raise ValueError("file type indeterminate")

        # check that file extension is valid

        file_name_split = os.path.split(filepath)[1].split(".")

        if len(file_name_split) != 2 or file_name_split[1] not in ExcelFileEditor.file_extensions:
            raise ValueError("invalid filename, .xlsx extension required")


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

    file_extensions = ["xml"]

    def create(self, path, file_name, xml_root):
        
        # check that dir exists

        if not os.path.isdir(path):
            raise FileNotFoundError("directory does not exist")
        
        # validate file extension

        '''
        file_name_split = file_name.split('.')

        if len(file_name_split) != 2 or file_name_split[1] not in XMLFileEditor.file_extensions:   
            raise ValueError("invalid filename, .xml extension required")
        '''

        if verify_file_extension(file_name, TextFileEditor.file_extensions):

            # validate that file does not exists

            file_path = os.path.join(path, file_name)

            if os.path.isfile(file_path):
                raise FileExistsError("could not create file, already exists")

            # create file

            xml_document = md.Document()
            root_element = xml_document.createElement(xml_root)
            xml_document.appendChild(root_element)
            xml_content = xml_document.toprettyxml(indent='\t')

            with open(file_path, 'w') as f:
                f.write(xml_content)


    def update(self, filepath, element_name, element_text):

        # check that file exists and is not binary

        if not os.path.isfile(filepath):
            raise FileNotFoundError("file does not exists")
        
        if is_binary(filepath):
            raise ValueError("provided file is binary, text file required")

        # check that file extension is valid

        file_name_split = os.path.split(filepath)[1].split(".")

        if len(file_name_split) != 2 or file_name_split[1] not in XMLFileEditor.file_extensions:
            raise ValueError("invalid filename, .xml extension required")

        # read contents and verify that it is valid XML

        with open(filepath, 'r') as f:
            file_content = f.read()
        
        try:
            content_dom = md.parseString(file_content)
        except xml.parsers.expat.ExpatError as error:
            print(error)

        # update file contents

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