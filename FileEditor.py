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
limitations, features and interpretations of task:

- text files can only be updated by appending new lines text
- only xlsx excel format is targeted for simplicity, although readily extendable and likely functional with more
  extensions with minimal changes
- xml files can only be updated by adding new elements with text, one level deep, to the root element / XML is validated before
  updating new files
- no experience with XML, except very limited Java Spring videos, might not be implemeted according to best practices (creating 
  XML document without Document Type Definition, etc...)
- excel files can only be updated by writing pandas DataFrames to new sheets / sheets must have unique name, causing error
  otherwise, could be handled by adding "-{unique constant}" to name
- written to be operating system agnostic (functionality across multiple operating systems) - not tested / also no unit
  testing due to time issues / also no manual tests of excel due to Ubuntu operating system
- correct file extensions, although not technically required in all cases are made mandatory
- different file checking methods applied
- automatic closing, also on exceptions, of files via using "with ... open(...)"
- code was refactored in last hour to implement DRY principles

needed additions:
- unit testing
- consistent use of "_" in variable names
- better excel support
- adding type hints
- extending functionality

'''

class FileEditor(ABC):

    file_extensions: list[str]

    @abstractmethod
    def create(self):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def file_validation_function(self):
        pass

    def verify_file_extension(self, file_name, file_extensions):
        file_name_split = file_name.split('.')
        extension_str = ",".join(str(element) for element in file_extensions)

        if len(file_name_split) != 2 or file_name_split[1] not in file_extensions:
            raise ValueError("invalid filename, valid extensions: " + extension_str)
        else:
            return True
        
    def verify_file_signature(file_validation_function, file_path, file_extensions):
        file_name = os.path.split(file_path)[1]

        if FileEditor.verify_file_extension(FileEditor, file_name, file_extensions) and file_validation_function(file_path, file_extensions):
            return True


class TextFileEditor(FileEditor):

    file_extensions = ["txt"]

    def create(self, path, file_name):

        # check dir exists 

        if not os.path.isdir(path):
            raise FileNotFoundError("directory does not exist")

        # check file extension

        if FileEditor.verify_file_extension(self, file_name, TextFileEditor.file_extensions):
            
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

        if FileEditor.verify_file_signature(self.file_validation_function, filepath, TextFileEditor.file_extensions):

            # add content

            content = content.strip() + " \n"

            with open(filepath, 'a') as f:
                f.write(content)

    def file_validation_function(self, filepath, file_extensions):
        if is_binary(filepath):
            raise ValueError("provided file is binary, text file required")
        else:
            return True


class ExcelFileEditor(FileEditor):

    file_extensions = ["xlsx"]

    def create(self, path, file_name):
        
        # check that dir exists

        if not os.path.isdir(path):
            raise FileNotFoundError("directory does not exist")
        
        # validate file name

        if FileEditor.verify_file_extension(self, file_name, ExcelFileEditor.file_extensions):

            # create file

            file_path = os.path.join(path, file_name)

            df = pandas.DataFrame()

            # TODO: check what if file already exists

            df.to_excel(file_path, index=True, header=True)


    # TODO: two sheets in excel can't have the same name
    def update(self, filepath, data, sheet_id):

        # check that data is DataFrame object

        if not isinstance(data, pandas.DataFrame):
            raise TypeError("data is required to be a pandas DataFrame")

        # check that file exists and file signature is valid

        if FileEditor.verify_file_signature(self.file_validation_function, filepath, ExcelFileEditor.file_extensions):

            # update file

            with pandas.ExcelWriter(filepath, mode="a") as w:
                try:
                    w.book = openpyxl.load_workbook(filepath)
                    data.to_excel(w, sheet_name=sheet_id)
                except (IllegalCharacterError, SheetTitleException, InvalidFileException, ReadOnlyWorkbookException) as error:
                    print(error)


    def file_validation_function(self, filepath, file_extensions):
        file_type = filetype.guess_extension(filepath)

        if file_type:
            if file_type not in file_extensions:
                raise ValueError("file type not accepted")
            else:
                return True
        else:
            raise ValueError("file type indeterminate")



class XMLFileEditor(FileEditor):

    file_extensions = ["xml"]

    def create(self, path, file_name, xml_root):
        
        # check that dir exists

        if not os.path.isdir(path):
            raise FileNotFoundError("directory does not exist")
        
        # validate file extension

        if FileEditor.verify_file_extension(self, file_name, XMLFileEditor.file_extensions):

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

        # check that file exists

        if not os.path.isfile(filepath):
            raise FileNotFoundError("file does not exists")
        
        # check that file is not binary and that file extension is valid

        if FileEditor.verify_file_signature(self.file_validation_function, filepath, XMLFileEditor.file_extensions):

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


    def file_validation_function(self, filepath, file_extensions):
        if is_binary(filepath):
            raise ValueError("provided file is binary, text file required")
        else:
            return True


if __name__ == "__main__":
    '''
    t = TextFileEditor()
    t.create('<insert pwd>', 'test.txt')
    t.update('<insert pwd>/test.txt', 'Hello')
    '''

    '''
    data = {
        "calories": [420, 380, 390],
        "duration": [50, 40, 45]
    }
    df = pandas.DataFrame(data)
    x = ExcelFileEditor()
    x.create('<insert pwd>', 'test.xlsx')
    x.update('<insert pwd>/test.xlsx',df,'sheet2290')
    '''
    
    '''
    m = XMLFileEditor()
    m.create('<insert pwd>', 'test.xml', 'root')
    m.update('<insert pwd>/test.xml', 'apple', 'lemon')
    '''

'''
useful links:
https://products.aspose.app/cells/viewer
https://openpyxl.readthedocs.io/en/stable/_modules/openpyxl/utils/exceptions.html#InvalidFileException
https://support.microsoft.com/en-au/office/file-formats-that-are-supported-in-excel-0943ff2c-6014-4e8d-aaea-b83d51d46247
https://pypi.org/project/filetype/
https://stackoverflow.com/questions/42778784/abstract-classes-with-varying-amounts-of-parameters
https://pythonbasics.org/write-excel/
https://bspaans.github.io/python-mingus/_modules/xml/dom/minidom.html
https://github.com/python/cpython/blob/main/Lib/xml/dom/expatbuilder.pys

'''