"""Regression cases for a content comparison used at a model publication boundary."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

PATH=Path(__file__).with_name('verify_generated_data.py')
spec=importlib.util.spec_from_file_location('verification_under_test',PATH)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def campus():
    return {'meta':{'scope':'concept','nested':{'status':'unverified'}},
            'sources':{'A':['Official source','https://example.org/원문']},
            'elems':[{'id':'E1','box':[0,0,0,1,2,3],'src':['A'],'conf':'D'},
                     {'id':'E2','box':[1,0,0,2,2,3],'src':['A'],'conf':'C'}],
            'equip':[[0,0,0,1,1,1,0,'P1','3F']], 'util':[[1,2,3]],
            'types':[{'key':'concept','name':'name'}]}


class VerificationTests(unittest.TestCase):
    def test_equal_same_model(self):
        a=campus()
        self.assertTrue(mod.compare(copy.deepcopy(a),a)['equal'])

    def test_unchanged_counts_do_not_hide_drift(self):
        changes=[lambda d:d['meta']['nested'].update(status='verified'),
                 lambda d:d['elems'][0]['box'].__setitem__(5,4),
                 lambda d:d['elems'][0].update(conf='A'),
                 lambda d:d['equip'][0].__setitem__(3,2),
                 lambda d:d['util'][0].__setitem__(2,4),
                 lambda d:d['sources']['A'].__setitem__(1,'https://example.org/other'),
                 lambda d:d['types'][0].update(name='different')]
        for change in changes:
            a=campus(); b=copy.deepcopy(a); change(b)
            with self.subTest(change=change):
                self.assertFalse(mod.compare(b,a)['equal'])

    def test_full_detail_limit_does_not_hide_failure(self):
        a=campus(); b=copy.deepcopy(a)
        b['meta']['nested']['status']='changed'; b['types'][0]['name']='changed'
        r=mod.compare(b,a,0)
        self.assertEqual(r['difference_count'],2)
        self.assertEqual(r['details'],[])
        self.assertTrue(r['details_truncated'])

    def test_list_length_difference_also_checks_common_entries(self):
        a=campus(); b=copy.deepcopy(a)
        b['util']=[[9,2,3],[4,5,6]]
        r=mod.compare(b,a)
        self.assertEqual(r['difference_count'],2)

    def test_element_reordering_is_reported(self):
        a=campus(); b=copy.deepcopy(a); b['elems'].reverse()
        r=mod.compare(b,a)
        self.assertEqual(r['difference_count'],1)
        self.assertEqual(r['details'][0]['kind'],'element_order_or_membership')

    def test_numeric_notation_is_equal_but_boolean_is_not_number(self):
        a=campus(); b=copy.deepcopy(a); b['equip'][0][0]=0.0
        self.assertTrue(mod.compare(b,a)['equal'])
        b['equip'][0][0]=False
        self.assertFalse(mod.compare(b,a)['equal'])

    def test_invalid_sources_duplicate_ids_and_boxes_are_rejected(self):
        for kind in ['source','id','box']:
            a=campus()
            if kind=='source': a['elems'][0]['src']=['MISSING']
            elif kind=='id': a['elems'][1]['id']='E1'
            else: a['elems'][0]['box'][3]=0
            with self.subTest(kind=kind),self.assertRaises(ValueError):
                mod.compare(a,campus())

    def test_json_duplicate_keys_and_nonfinite_numbers_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'bad.json'
            for value in ['{"key":1,"key":2}','{"key":NaN}','{"key":1e999}']:
                p.write_text(value,encoding='utf-8')
                with self.subTest(value=value),self.assertRaises(ValueError):
                    mod.load(p)

    def test_exact_decimal_values_do_not_round_into_false_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'number.json'
            def parsed(number):
                d=campus(); d['meta']['number']='TOKEN'
                p.write_text(json.dumps(d).replace('"TOKEN"',number),encoding='utf-8')
                return mod.load(p)[0]
            for left,right in [('1.0000000000000001','1.0'),('1e-999','0.0'),
                               ('9007199254740992.0','9007199254740993.0')]:
                with self.subTest(left=left,right=right):
                    report=mod.compare(parsed(left),parsed(right))
                    self.assertFalse(report['equal'])
                    encoded=json.dumps(report,default=mod.report_number)
                    self.assertIn('json_decimal',encoded)
            self.assertTrue(mod.compare(parsed('1'),parsed('1.0'))['equal'])
            self.assertFalse(mod.compare(parsed('false'),parsed('0'))['equal'])

    def test_report_hardlink_to_input_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            a=Path(directory)/'a.json'; alias=Path(directory)/'alias.json'
            a.write_text(json.dumps(campus()),encoding='utf-8')
            alias.hardlink_to(a)
            original=a.read_bytes()
            result=subprocess.run([sys.executable,str(PATH),'--generated',str(a),
                '--reference',str(a),'--report',str(alias)],capture_output=True,text=True)
            self.assertEqual(result.returncode,2)
            self.assertEqual(a.read_bytes(),original)

    def test_cli_equal_difference_and_input_preservation(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory); a=folder/'a.json'; b=folder/'b.json'
            a.write_text(json.dumps(campus()),encoding='utf-8')
            b.write_bytes(a.read_bytes())
            run=lambda *extra:subprocess.run([sys.executable,str(PATH),'--generated',str(a),
                '--reference',str(b),*extra],capture_output=True,text=True)
            self.assertEqual(run().returncode,0)
            data=campus(); data['meta']['scope']='changed'
            b.write_text(json.dumps(data),encoding='utf-8')
            self.assertEqual(run().returncode,1)
            original=a.read_bytes()
            self.assertEqual(run('--report',str(a)).returncode,2)
            self.assertEqual(a.read_bytes(),original)


if __name__=='__main__':
    unittest.main()
