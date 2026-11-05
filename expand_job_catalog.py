"""Mở rộng bằng nguồn thật theo batch pandas, giữ nguyên ID/nội dung tin đã bàn giao.

Chạy: python expand_job_catalog.py. File nguồn Parquet chỉ ở .cache.
Không sinh tin giả, không lấy số dòng CSV làm số tin thực, không nạp 607k JD vào RAM.
"""
from hashlib import sha256
from pathlib import Path
from datetime import datetime, timezone
import json
import re
import shutil
import pandas as pd
import pyarrow.parquet as pq
from build_job_catalog import PublicJobCatalogBuilder, SOURCE, REVISION, LICENSE
from locations import plain_text
from resume_profile import ROLES

ROOT=Path(__file__).resolve().parent


class ExpandedCatalogBuilder(PublicJobCatalogBuilder):
    all_regions=True

    def expand(self, source_path, output=ROOT/'data', batch_size=4096):
        output=Path(output); current=output/'jobs_catalog.csv'
        existing=pd.read_csv(current,encoding='utf-8-sig').fillna('')
        # Benchmark 500 tin là tập đóng băng riêng. Không đổi qrels để hợp thức
        # kết quả cũ khi phạm vi ứng viên của web đã lớn hơn.
        frozen=output/'evaluation/jobs_catalog_500.csv'
        if not frozen.exists(): shutil.copy2(current,frozen)
        seen=set(existing.Content_Fingerprint); source_ids=set(existing.Source_Row_ID.astype(str))
        records=[];scanned=0;prefiltered=0;duplicates=0
        aliases=[alias for role in ROLES for alias in role[5]]
        pattern=r'(?<!\w)(?:'+ '|'.join(re.escape(alias) for alias in aliases)+r')(?!\w)'
        for batch in pq.ParquetFile(source_path).iter_batches(batch_size=batch_size):
            frame=batch.to_pandas().fillna('')
            frame['_source_index']=range(scanned,scanned+len(frame));scanned+=len(frame)
            # Lab 3: chuẩn hóa chuỗi, mặt nạ vector hóa, bỏ thiếu/trùng trước
            # bước NLP đắt hơn. to_numeric dùng errors=coerce thay vì đoán giá trị.
            title=frame.job_title.astype('string').map(plain_text)
            industry=frame.job_industry.astype('string').map(plain_text)
            mask=title.str.contains(pattern,regex=True,na=False)|industry.str.contains('it phan mem|cong nghe thong tin',regex=True,na=False)
            frame=frame.loc[mask].drop_duplicates('id');prefiltered+=len(frame)
            for raw in frame.to_dict('records'):
                if str(raw['id']) in source_ids: continue
                row=self.normalize_row(raw,int(raw['_source_index']))
                if row is None:continue
                fingerprint=sha256(plain_text(row['Company']+' '+row['Title']+' '+row['Location']+' '+row['Job_Description']).encode()).hexdigest()
                if fingerprint in seen:duplicates+=1;continue
                seen.add(fingerprint);source_ids.add(str(row['Source_Row_ID']))
                row['Content_Fingerprint']=fingerprint;records.append(row)
            if scanned%32768<batch_size:print(json.dumps({'scanned':scanned,'new_valid':len(records)}),flush=True)
        first=max(int(str(identifier)[2:]) for identifier in existing.Job_ID)+1
        for i,row in enumerate(records,first):row['Job_ID']=f'VN{i:04d}'
        jobs=pd.concat([existing,pd.DataFrame(records)],ignore_index=True)
        # Nhóm cột phân loại tiết kiệm bộ nhớ; CSV xuất vẫn đọc được bằng pandas.
        for column in ('Domain','Role_Code','Primary_Region','Source_Dataset','Source_License'):
            jobs[column]=jobs[column].astype('category')
        temporary=current.with_suffix('.tmp.csv');jobs.to_csv(temporary,index=False,encoding='utf-8-sig');temporary.replace(current)
        manifest={'dataset':SOURCE,'revision':REVISION,'license':LICENSE,
                  'source_url':f'https://huggingface.co/datasets/{SOURCE}',
                  'pinned_source_url':f'https://huggingface.co/datasets/{SOURCE}/tree/{REVISION}',
                  'retrieved_at':datetime.now(timezone.utc).isoformat(),'source_rows_scanned':scanned,
                  'prefiltered_rows':prefiltered,'eligible_unique_rows':len(jobs),'selected_rows':len(jobs),
                  'preserved_rows':len(existing),'added_rows':len(records),'duplicates_removed':duplicates,
                  'batch_size':batch_size,'actual_region_counts':jobs.Primary_Region.value_counts().to_dict(),
                  'role_counts':jobs.Role_Code.value_counts().to_dict(),'company_count':int(jobs.Company.nunique()),
                  'unknown_experience_count':int((~jobs.Experience_Known.astype(bool)).sum()),
                  'csv_sha256':sha256(current.read_bytes()).hexdigest(),
                  'source_sha256':sha256(Path(source_path).read_bytes()).hexdigest(),
                  'vacancy_status':'Historical source snapshot; current availability not verified.',
                  'english_content':'Rule-based structured summaries unless original English is available; not full translations.',
                  'pipeline':'Parquet batches -> pandas masks/drop_duplicates -> normalization -> fingerprint dedup -> concat/category/value_counts'}
        (output/'catalog_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
        return manifest


if __name__=='__main__':
    builder=ExpandedCatalogBuilder();source=ROOT/'.cache/tinix-jobs.parquet';builder.download(source)
    print(json.dumps(builder.expand(source),ensure_ascii=True,indent=2))
