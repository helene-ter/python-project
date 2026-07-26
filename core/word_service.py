import re
from pathlib import Path

"""
This class contains methods for extracting words in files and sort a list in alphabetic order.
"""
class WordService: 

    # This method reads all files in a given path and extracts words from lines that start with a number.
    def read_files(self, path):
        if path is None or not Path(path).exists():
            raise ValueError("Invalid path provided.")
        
        extractedWords = []

        for fichier in Path(path).iterdir():
            if fichier.is_file():
                with open(fichier, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        line = line.strip()
                        if re.match(r"^[0-9]", line):
                            piece = re.split(r"\s+", line)
                            word = piece[-1].strip()

                            if word:
                                extractedWords.append(word)

        return extractedWords
    
    def order_by_alphabetic(self, extractedWords):
        uniqueValuesList = set(extractedWords)
        orderedWords = sorted(uniqueValuesList)

        return orderedWords




