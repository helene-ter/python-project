import unittest
import tempfile
from pathlib import Path
from core import word_service
from core.word_service import WordService

class WordServiceTest(unittest.TestCase):
    def test_order_by_alphabetic_whenListisEmpty_thenReturnEmpty(self):
        # WHEN
        word_service = WordService()
        result = word_service.order_by_alphabetic([])

        #THEN
        self.assertEqual(result, [])
    
    def test_order_by_alphabetic_whenListIsValid_thenReturnOrderedList(self):
        # WHEN
        word_service = WordService()
        result = word_service.order_by_alphabetic(['azerty', 'azertya', 'azertyz', 'qwerty'])
        
        #THEN
        self.assertEqual(result, ['azerty', 'azertya', 'azertyz', 'qwerty'])
    
    def test_order_by_alphabetic_whenListContainsDoubledElements_thenRemoveDuplicates(self):
        # WHEN
        word_service = WordService()
        result = word_service.order_by_alphabetic(['azerty', 'azertya', 'azertyz', 'qwerty', 'azerty'])

        #THEN
        self.assertEqual(result, ['azerty', 'azertya', 'azertyz', 'qwerty'])

    def test_read_files_whenPathIsValidInvalid_thenReturnError(self):
        # THEN
        word_service = WordService()
        with self.assertRaises(ValueError):
            word_service.read_files("invalid_path")
        
    
    def test_read_files_whenPathIsValid_thenReturnExtractedWords(self):
        # GIVEN 
        with tempfile.TemporaryDirectory() as temp_path:
            file = Path(temp_path) / "test_file.txt"
            file.write_text("123 word1\n4 word2\n0000000000-0--33435 word3")

            # WHEN
            word_service = WordService()
            result = word_service.read_files(temp_path)

            # THEN
            self.assertEqual(result, ['word1', 'word2', 'word3'])


    def test_read_files_whenNoNumber_thenReturnEmptyList(self):
        # GIVEN 
        with tempfile.TemporaryDirectory() as temp_path:
            file = Path(temp_path) / "test_file.txt"
            file.write_text("----- word1\n???? word2\n !!!! word3")

            # WHEN
            word_service = WordService()
            result = word_service.read_files(temp_path)

            # THEN
            self.assertEqual(result, [])
