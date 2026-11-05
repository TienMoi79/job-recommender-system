"""Rà soát phần hiển thị toàn catalog, không đổi đầu vào NLP hoặc benchmark.

python repair_job_presentation.py          # chỉ kiểm tra, xuất báo cáo
python repair_job_presentation.py --apply  # backup rồi áp dụng
Nguồn gốc lấy từ snapshot Parquet công khai đã cache, không lấy CV người dùng.
"""
from __future__ import annotations
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import argparse
import json
import shutil
import pandas as pd
import pyarrow.parquet as pq
from job_presentation import presentation_fields

ROOT=Path(__file__).resolve().parent


def source_rows(jobs,source):
    wanted=set(jobs.Source_Row_ID.astype(int));result={}
    for batch in pq.ParquetFile(source).iter_batches(batch_size=8192,columns=['id','job_description','requirements','salary','benefits']):
        frame=batch.to_pandas();frame=frame.loc[frame.id.isin(wanted)].fillna('')
        result.update({str(row['id']):row for row in frame.to_dict('records')})
    if len(result)!=len(wanted):raise ValueError('Thiếu bản ghi nguồn; không áp dụng bản sửa dở dang.')
    return result


def repair(*,apply=False):
    path=ROOT/'data/jobs_catalog.csv';manifest_path=ROOT/'data/catalog_manifest.json'
    jobs=pd.read_csv(path,encoding='utf-8-sig').fillna('')
    source=ROOT/'.cache/tinix-jobs.parquet'
    rows=source_rows(jobs,source)
    report=[];updated=jobs.copy()
    # Cột *_Display giữ layout phục hồi; Job_Description/Requirements gốc dùng
    # cho AI vẫn giữ nguyên, nên index và benchmark không bị đổi ngữ nghĩa.
    fields=[]
    for row in jobs.to_dict('records'):
        original=rows[str(row['Source_Row_ID'])]
        context='\n'.join(str(original.get(key) or '') for key in ('job_description','requirements','benefits'))
        data=presentation_fields(original['job_description'],original['requirements'],original['salary'],context)
        fields.append(data)
        report.append({'Job_ID':row['Job_ID'],'Salary_Original':data['Salary_Original'],'Salary_Before':data['Salary_Original'],
                       'Salary_Previous_Display':row['Salary'],
                       'Salary_After':data['Salary'],'Salary_Status':data['Salary_Status'],'Salary_Evidence':data['Salary_Evidence'],
                       'Description_Lines':len(data['Job_Description_Display'].splitlines()),
                       'Requirements_Lines':len(data['Requirements_Display'].splitlines()),'Source_URL':row['Source_URL']})
    additions=pd.DataFrame(fields)
    for column in additions:updated[column]=additions[column]
    audit=pd.DataFrame(report);destination=ROOT/'outputs/data_quality';destination.mkdir(parents=True,exist_ok=True)
    audit.to_csv(destination/'presentation_audit.csv',index=False,encoding='utf-8-sig')
    summary={'rule':'job-presentation-v1','rows_audited':len(jobs),
             'salary_changed':int((audit.Salary_Before!=audit.Salary_After).sum()),
             'salary_changed_since_last_run':int((audit.Salary_Previous_Display!=audit.Salary_After).sum()),
             'salary_status_counts':audit.Salary_Status.value_counts().to_dict(),
             'multiline_descriptions':int(audit.Description_Lines.gt(1).sum()),
             'multiline_requirements':int(audit.Requirements_Lines.gt(1).sum()),
             'nlp_source_columns_changed':False,'frozen_benchmark_changed':False,'applied':apply}
    if apply:
        stamp=datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S');backup=ROOT/'.cache'/('presentation-before-'+stamp)
        backup.mkdir(parents=True)
        for p in (path,manifest_path):shutil.copy2(p,backup/p.name)
        previous=sha256(path.read_bytes()).hexdigest()
        temp=path.with_suffix('.presentation.tmp.csv');updated.to_csv(temp,index=False,encoding='utf-8-sig');temp.replace(path)
        manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
        manifest['csv_sha256']=sha256(path.read_bytes()).hexdigest()
        manifest['presentation']={**summary,'previous_csv_sha256':previous,'source_text':'Original NLP columns unchanged; display layout restored heuristically.',
                                  'salary_policy':'VND amounts in millions, original pay period kept; currency-less/invalid amounts not guessed; explicit negotiable salary beats allowance contamination.'}
        manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
        summary['backup']=str(backup)
    (destination/'presentation_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--apply',action='store_true');args=parser.parse_args()
    print(json.dumps(repair(apply=args.apply),ensure_ascii=True,indent=2))
