import re
from langchain_text_splitters import RecursiveCharacterTextSplitter
from cfg import Cfg

class TextPreprocessing:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Cfg.chunk_size,
            chunk_overlap=Cfg.chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )

    def remove_extra_newlines(self, text):
        return re.sub(r'\n\n+', '\n\n', text)

    def remove_special_characters(self, text):
        return re.sub(r'[^a-zA-Z0-9\s!\-:;\'\"\[\]\(\)@$%&*,\.]', '', text)
    
    def separate_headings(self, text):
        return re.sub(r'\n([0-9A-Z].{2,80})\n+([0-9A-Z].{80,})\n', r'\n\n\1\n\2\n\n', text)
    
    def process_text(self, text):
        text = self.separate_headings(text)
        text = self.remove_special_characters(text)
        text = self.remove_extra_newlines(text)
        return text
    
    def remove_incorrect_newline_char(self, text):
        index = 0
        pointer = text.find('\n', index)
        while pointer > -1 and pointer + 1 <= len(text) - 1:
            if text[pointer - 1] != '.' and text[pointer + 1].islower():
                text = text[:pointer] + ' ' + text[pointer + 1:]
            pointer = text.find('\n', index + pointer + 1)
        return text
    
    def split_text(self, text):
        return self.text_splitter.split_text(text)

if __name__ == '__main__':
    text = """this is a sample text. It contains special characters like !@#$%^&*()_+{}|:"<>?[];',./\."""
    text_preprocessor = TextPreprocessing()
    processed_text = text_preprocessor.process_text(text)
    print(processed_text)