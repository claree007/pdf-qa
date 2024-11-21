from pypdf import PdfReader
from utils.text_preprocessing import TextPreprocessing

class PyPDFReader:
    def __init__(self, text_preprocessor: TextPreprocessing):
        self.text_preprocessor = text_preprocessor

    def __read_pages(self, reader):
        pages = reader.pages
        full_text = ''
        for page_num in range(len(pages)):
            page = reader.pages[page_num]
            page_contents = page.extract_text()
            joining_part = self.text_preprocessor.remove_incorrect_newline_char(
                full_text[-5:] + page_contents
            )
            if joining_part[:6] == full_text[-5:] + page_contents[0]:
                joining_part = joining_part[:5] + "\n\n" + joining_part[5:]
            full_text = full_text[:-5] + joining_part

        full_text = full_text[:-2]
        return full_text

    def process_document(self, document_path):
        reader = PdfReader(document_path)
        full_text = self.__read_pages(reader)
        return full_text
