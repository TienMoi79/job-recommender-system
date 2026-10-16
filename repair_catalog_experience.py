"""Sửa trường kinh nghiệm của đúng 500 tin hiện có, không lấy mẫu lại nguồn.

Mặc định chỉ xem trước. --apply lưu bản CSV cũ vào .cache, cập nhật phần tóm
tắt Anh, manifest và liên kết checksum benchmark. Nội dung tin/ID/nhãn không đổi.
"""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import argparse
import json
import re
import shutil
import pandas as pd
from job_experience import resolve_job_experience

ROOT=Path(__file__).resolve().parent


def repair(*,apply=False):
    path=ROOT/'data/jobs_catalog.csv'
    previous_hash=sha256(path.read_bytes()).hexdigest()
    jobs=pd.read_csv(path,encoding='utf-8-sig').fillna('')
    manifest_path=ROOT/'data/catalog_manifest.json'
    benchmark_path=ROOT/'data/evaluation/benchmark.json'
    manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
    benchmark=json.loads(benchmark_path.read_text(encoding='utf-8'))
    if previous_hash!=manifest['csv_sha256'] or previous_hash!=benchmark['catalog_sha256']:
        raise ValueError('Catalog/checksums changed unexpectedly. Review the source before repairing.')
    qrels_hash=sha256(json.dumps(benchmark['queries'],ensure_ascii=False,sort_keys=True).encode()).hexdigest()
    changes=[]
    for index,row in jobs.iterrows():
        parsed=resolve_job_experience(row.Experience_Text,row.Requirements,row.Job_Description)
        if row.Experience_Known:
            continue  # Không thay các số năm có cấu trúc đã biết trong bản sửa này.
        if not parsed.known:
            continue
        changes.append({'Job_ID':row.Job_ID,'Title':row.Title,'Old_Experience_Text':row.Experience_Text,
                        'Old_Experience_Years':row.Experience_Years,'Experience_Years':parsed.years,
                        'Experience_Source':parsed.source,'Experience_Evidence':parsed.evidence})
        jobs.loc[index,'Experience_Years']=parsed.years
        jobs.loc[index,'Experience_Known']=True
        # Giữ nguyên Experience_Text thô; nguồn suy ra ghi ở cột riêng.
        jobs.loc[index,'Experience_Source']=parsed.source
        jobs.loc[index,'Experience_Evidence']=parsed.evidence
        english=f'{parsed.years:g} years (parsed lower bound)'
        jobs.loc[index,'Requirements_EN']=re.sub(r'Experience: .*?\.$',f'Experience: {english}.',str(row.Requirements_EN))
        jobs.loc[index,'Job_Description_EN']=re.sub(
            r'(?<=Experience requirement: ).*?(?=\. This is a structured English summary)',
            english,str(row.Job_Description_EN))
    audit=pd.DataFrame(changes)
    print(json.dumps({'apply':apply,'recovered':len(changes),'remaining_unknown':int((~jobs.Experience_Known).sum())}))
    if not apply or not changes:
        return audit
    now=datetime.now(timezone.utc).isoformat()
    backup=ROOT/'.cache'/('experience-before-'+datetime.now().strftime('%Y%m%d_%H%M%S'))
    backup.mkdir(parents=True,exist_ok=False)
    for item in (path,manifest_path,benchmark_path):
        shutil.copy2(item,backup/item.name)
    jobs['Experience_Source']=jobs['Experience_Source'].fillna('').replace('', 'experience_level')
    jobs.loc[~jobs.Experience_Known,'Experience_Source']='unknown'
    jobs['Experience_Evidence']=jobs['Experience_Evidence'].fillna('')
    temporary=path.with_suffix('.tmp.csv')
    jobs.to_csv(temporary,index=False,encoding='utf-8-sig')
    temporary.replace(path)
    new_hash=sha256(path.read_bytes()).hexdigest()
    manifest['csv_sha256']=new_hash
    manifest['unknown_experience_count']=int((~jobs.Experience_Known).sum())
    manifest.setdefault('normalization_updates',[]).append({
        'at':now,'rule':'job-experience-fallback-v1','recovered':len(changes),
        'previous_csv_sha256':previous_hash,'csv_sha256':new_hash,
        'note':'Only missing numeric experience and derived English summaries repaired; original source text, Job_ID and qrels unchanged.'})
    benchmark['catalog_sha256']=new_hash
    benchmark['catalog_normalization_note']={
        'at':now,'previous_catalog_sha256':previous_hash,'queries_sha256_unchanged':qrels_hash,
        'reason':'Experience recovered from existing source requirements/JD; posting text, query texts and relevance grades unchanged. Rerun metrics.'}
    manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    benchmark_path.write_text(json.dumps(benchmark,ensure_ascii=False,indent=2),encoding='utf-8')
    output=ROOT/'outputs/data_quality';output.mkdir(parents=True,exist_ok=True)
    audit.to_csv(output/'experience_repairs.csv',index=False,encoding='utf-8-sig')
    print('Backup:',backup)
    return audit


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--apply',action='store_true')
    args=parser.parse_args()
    result=repair(apply=args.apply)
    if len(result):
        print(result[['Job_ID','Experience_Years','Experience_Source']].to_string(index=False))
