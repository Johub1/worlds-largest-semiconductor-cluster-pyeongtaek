"""Compare generated and checked-in campus JSON without changing either input.

Compare the same language and intended revision. Exit 0: equal; 1: different;
2: invalid input or I/O error. A pass does not verify provenance, site accuracy,
the generator that was executed, CAD exports, documentation, or release archives.
"""
import argparse
from collections import Counter
from decimal import Decimal, InvalidOperation
import hashlib
import json
import math
from pathlib import Path
import sys


def unique_object(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError('duplicate JSON key: '+key)
        obj[key] = value
    return obj


def reject_constant(value):
    raise ValueError('non-finite JSON number: '+value)


def finite_float(value):
    # Keep every decimal digit: binary float rounding could falsely equate
    # 1.0000000000000001 and 1.0, or underflow a small nonzero value to zero.
    try:
        number=Decimal(value)
    except InvalidOperation as error:
        raise ValueError('unsupported JSON decimal: '+value) from error
    if not number.is_finite() or not math.isfinite(float(number)):
        raise ValueError('JSON number outside supported finite range: '+value)
    return number


def report_number(value):
    if isinstance(value,Decimal):
        return {'json_decimal':str(value)}
    raise TypeError('unsupported report value: '+type(value).__name__)


def load(path):
    raw = path.read_bytes()
    document = json.loads(raw.decode('utf-8-sig'), object_pairs_hook=unique_object,
                          parse_constant=reject_constant,parse_float=finite_float)
    return document, hashlib.sha256(raw).hexdigest()


def validate(document):
    if not isinstance(document, dict):
        raise ValueError('campus root must be an object')
    for key, kind in [('meta',dict),('sources',dict),('elems',list)]:
        if not isinstance(document.get(key), kind):
            raise ValueError('missing or invalid campus section: '+key)
    seen = set()
    for element in document['elems']:
        if not isinstance(element, dict):
            raise ValueError('element must be an object')
        eid = element.get('id')
        if not isinstance(eid, str) or not eid or eid in seen:
            raise ValueError('missing or duplicate element id: '+str(eid))
        seen.add(eid)
        box = element.get('box')
        if not isinstance(box,list) or len(box)!=6 or any(
            isinstance(v,bool) or not isinstance(v,(int,float,Decimal)) or not math.isfinite(v)
            for v in box
        ) or any(box[i]>=box[i+3] for i in range(3)):
            raise ValueError('invalid box: '+eid)
        source_keys = element.get('src')
        if not isinstance(source_keys,list) or any(
            not isinstance(k,str) or k not in document['sources'] for k in source_keys
        ):
            raise ValueError('invalid or unresolved element source: '+eid)


def numeric_equal(a, b):
    return (not isinstance(a,bool) and not isinstance(b,bool)
            and isinstance(a,(int,float,Decimal)) and isinstance(b,(int,float,Decimal)) and a==b)


class Comparison:
    def __init__(self, limit=100):
        self.limit = limit
        self.count = 0
        self.by_section = Counter()
        self.details = []

    def record(self, path, kind, **detail):
        self.count += 1
        section = path.split('.',2)[1].split('[',1)[0] if '.' in path else '$'
        self.by_section[section] += 1
        if len(self.details)<self.limit:
            self.details.append(dict(path=path,kind=kind,**detail))

    def walk(self, generated, reference, path='$'):
        if type(generated) is not type(reference):
            if numeric_equal(generated,reference):
                return
            self.record(path,'type',generated_type=type(generated).__name__,
                        reference_type=type(reference).__name__)
            return
        if isinstance(generated,dict):
            for key in sorted(generated.keys()|reference.keys()):
                child = path+'.'+key
                if key not in generated:
                    self.record(child,'missing_key')
                elif key not in reference:
                    self.record(child,'extra_key')
                else:
                    self.walk(generated[key],reference[key],child)
        elif isinstance(generated,list):
            if path=='$.elems':
                self.elements(generated,reference,path)
            else:
                if len(generated)!=len(reference):
                    self.record(path,'list_length',generated_length=len(generated),
                                reference_length=len(reference))
                for i in range(min(len(generated),len(reference))):
                    self.walk(generated[i],reference[i],f'{path}[{i}]')
        elif generated!=reference:
            self.record(path,'value',generated=generated,reference=reference)

    def elements(self, generated, reference, path):
        gm={e['id']:e for e in generated}
        rm={e['id']:e for e in reference}
        for eid in sorted(gm.keys()|rm.keys()):
            child=path+'['+json.dumps(eid,ensure_ascii=False)+']'
            if eid not in gm:
                self.record(child,'missing_element')
            elif eid not in rm:
                self.record(child,'extra_element')
            else:
                self.walk(gm[eid],rm[eid],child)
        go=[e['id'] for e in generated]
        ro=[e['id'] for e in reference]
        if go!=ro:
            self.record(path,'element_order_or_membership',generated_length=len(go),
                        reference_length=len(ro))


def compare(generated, reference, limit=100):
    validate(generated)
    validate(reference)
    result=Comparison(limit)
    result.walk(generated,reference)
    return {'equal':result.count==0,'difference_count':result.count,
            'differences_by_section':dict(sorted(result.by_section.items())),
            'details':result.details,'details_truncated':result.count>len(result.details)}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--generated',required=True,type=Path)
    parser.add_argument('--reference',required=True,type=Path)
    parser.add_argument('--report',type=Path)
    parser.add_argument('--max-details',type=int,default=100)
    args=parser.parse_args(argv)
    if args.max_details<0:
        parser.error('--max-details must be nonnegative')
    try:
        input_paths={args.generated.resolve(),args.reference.resolve()}
        if args.report and (args.report.resolve() in input_paths or (
            args.report.exists() and any(args.report.samefile(p) for p in input_paths)
        )):
            raise ValueError('report must not overwrite an input')
        generated,ghash=load(args.generated)
        reference,rhash=load(args.reference)
        report=compare(generated,reference,args.max_details)
        report.update(generated=str(args.generated),reference=str(args.reference),
                      generated_sha256=ghash,reference_sha256=rhash,
                      scope='Same-language JSON content comparison; generator execution and site accuracy are not verified')
        if args.report:
            args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2,default=report_number),encoding='utf-8')
        print(json.dumps({k:v for k,v in report.items() if k!='details'},ensure_ascii=False))
        return 0 if report['equal'] else 1
    except (OSError,ValueError,TypeError,OverflowError,RecursionError) as error:
        print('Verification error: '+str(error),file=sys.stderr)
        return 2


if __name__=='__main__':
    raise SystemExit(main())
