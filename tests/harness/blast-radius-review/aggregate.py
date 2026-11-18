#!/usr/bin/env python3
"""Validate evidence-bearing grades and aggregate a completed eval iteration."""
import sys
sys.dont_write_bytecode = True
import argparse
import json
from pathlib import Path
from validate import validate, require, load_json

ROOT = Path(__file__).resolve().parent

def aggregate(run):
    suite = validate()
    metadata = load_json(run / 'metadata.json')
    rows = []
    summaries = {}
    for config in ('with_skill', 'without_skill'):
        compatibility = []
        passed = total = cases_passed = 0
        for case in suite['evals']:
            directory = run / f"eval-{case['id']}" / config
            output = (directory / 'output.md').read_text()
            grade = load_json(directory / 'grading.json')
            checks = grade['expectations']
            require(len(checks) == len(case['expectations']), 'grade count mismatch')
            for expected, check in zip(case['expectations'], checks):
                require(check['text'] == expected, 'grade expectation mismatch')
                require(type(check['passed']) is bool, 'grade verdict must be boolean')
                require(isinstance(check['evidence'], str) and check['evidence'].strip(), 'grade requires evidence')
            count = sum(c['passed'] for c in checks)
            n = len(checks)
            summary = {'passed': count, 'failed': n-count, 'total': n, 'pass_rate': count/n}
            require(grade['summary'] == summary, 'grader summary does not match verdicts')
            passed += count; total += n; cases_passed += count == n
            rows.append({'eval_id':case['id'], 'configuration':config, 'run_number':1, 'result':summary, 'expectations':checks})
            compatibility.append({'id':case['id'], 'output':output, 'expectation_results':[c['passed'] for c in checks]})
        summaries[config] = {'passed':passed, 'total':total, 'pass_rate':passed/total, 'cases_passed':cases_passed, 'cases_total':len(suite['evals'])}
        (run / f'{config}-results.json').write_text(json.dumps(compatibility, indent=2)+'\n')
    queries = load_json(ROOT/'trigger-evals.json')['cases']
    predictions = load_json(run/'trigger-output.json')
    require(len(predictions) == len(queries), 'trigger result count mismatch')
    trigger_checks=[]
    for i,(q,p) in enumerate(zip(queries,predictions),1):
        require(p['id']==i and type(p['selected']) is bool and p['reason'], 'invalid trigger prediction')
        trigger_checks.append({'id':i, **q, **p, 'passed':p['selected']==q['should_trigger']})
    benchmark={'metadata':metadata,'runs':rows,'run_summary':summaries,'trigger_probe':{'passed':sum(c['passed'] for c in trigger_checks),'total':len(queries),'results':trigger_checks},'notes':['One observation per case/configuration; no statistical or Claude-runtime claim.','Pass rates reflect predeclared criteria, not complete task quality.','Trigger probe measures description selection, not actual runtime skill loading.']}
    (run/'benchmark.json').write_text(json.dumps(benchmark,indent=2)+'\n')
    for config,summary in summaries.items(): print(config,summary)
    print('Trigger description probe:',benchmark['trigger_probe']['passed'],'/',len(queries))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run',type=Path)
    args=parser.parse_args()
    aggregate(args.run)
