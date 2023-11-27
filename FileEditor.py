from typing import ClassVar
import os
from binaryornot.check import is_binary
import pandas 
import openpyxl
import filetype
import uuid

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
    file_extensions = ["xlsx", "xlsm"]     # use list, more types ?

    def create(self, path, name):
        if not os.path.isdir(path):
            raise FileNotFoundError("directory does not exist")
        
        file_name_split = name.split('.')

        if len(file_name_split) != 2 or file_name_split[1] not in ExcelFileEditor.file_extensions:      # limit to xlsx ? check reqs
            raise ValueError("invalid filename, .txt extension required")

        file_path = os.path.join(path, name)

        df = pandas.DataFrame()

        # todo: check what if file exists

        df.to_excel(file_path, index=False, header=False)


    # two sheets in excel can't have the same name
    def update(self, filepath, data):

        # TODO: check data is DF
        # TODO: openpyxl errors catch
        # TODO: unique sheet name

        if not isinstance(data, pandas.DataFrame):
            raise TypeError("data is required to be a pandas DataFrame")

        if not os.path.isfile(filepath):
            raise FileNotFoundError("file does not exists")

        file_type = filetype.guess_extension(filepath)

        print(file_type)

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

# .xml
class XMLFileEditor(FileEditor):

    file_signature = ""
    file_extensions = ".txt"

    def create(self, path, name):
        pass 

    def update(self, filepath, XXXX):
        pass
    
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