import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from catalog import parse
from upstream import merge, compare

class UpstreamSyncTest(unittest.TestCase):
    def test_reorder_keeps_translation_by_key(self):
        old=b'One=\nTwo=\n'
        new=b'Two=\nOne=\n'
        target='One=一\nTwo=二\n'.encode()
        self.assertEqual(merge(old,new,target),'Two=二\nOne=一\n')

    def test_changed_help_keeps_translation_and_requests_review(self):
        old=b':sample_help:\nOld text\n:end\n'
        new=b':sample_help:\nChanged text\n:end\n'
        target=':sample_help:\n已有译文\n:end\n'.encode()
        result=merge(old,new,target)
        self.assertIn('; TODO review changed English source',result)
        self.assertIn('已有译文',result)

    def test_new_entries_are_left_untranslated_and_marked(self):
        result=merge(b'One=\n',b'One=\nTwo=\n','One=一\n'.encode())
        self.assertIn('; TODO translate new English source: Two\nTwo=\n',result)

    def test_removed_entries_are_reported(self):
        result=compare({'sample.txt':b'One=\nTwo=\n'},{'sample.txt':b'Two=\n'})
        self.assertEqual(result,[{'file':'sample.txt','type':'entry','key':'One','change':'removed'}])

    def test_orphan_source_line_is_repaired_consistently(self):
        line='Note that this module reviews all of your previously installed Docker Containers to determine which appdata folders are abandoned.'
        row=parse(line,True)[0]
        self.assertEqual(row['type'],'entry')
        self.assertNotIn('.',row['key'])

if __name__=='__main__': unittest.main()
