"""Đánh giá xếp hạng trên qrels đóng băng, độc lập với công thức chấm điểm.

Precision chia cho K cố định, kể cả hệ thống trả ít hơn K. NDCG dùng gain
2**grade-1 và ideal ranking từ toàn bộ nhãn liên quan của truy vấn. Truy vấn
không có việc phù hợp được đánh giá Empty_Accuracy riêng, không làm đẹp NDCG.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import argparse
import json
import math
import platform
import time
import numpy as np
import pandas as pd


def ranking_metrics(predicted: list[str], relevance: dict[str,int], k=5) -> dict[str,float]:
    if isinstance(k,bool) or not isinstance(k,int) or k<=0:
        raise ValueError('k must be a positive integer')
    if len(predicted)!=len(set(predicted)):
        raise ValueError('Repeated Job_ID would inflate ranking metrics')
    if any(isinstance(value,bool) or not isinstance(value,int) or value not in (0,1,2) for value in relevance.values()):
        raise ValueError('Relevance grades must be 0, 1 or 2')
    returned = predicted[:k]
    grades = [relevance.get(identifier,0) for identifier in returned]
    positives = sum(grade>=1 for grade in relevance.values())
    dcg = lambda values:sum((2**grade-1)/math.log2(rank+2) for rank,grade in enumerate(values))
    ideal = dcg(sorted(relevance.values(),reverse=True)[:k])
    return {
        f'Precision@{k}':sum(grade>=1 for grade in grades)/k,
        f'StrictPrecision@{k}':sum(grade==2 for grade in grades)/k,
        f'Recall@{k}':sum(grade>=1 for grade in grades)/positives if positives else 0.,
        f'NDCG@{k}':dcg(grades)/ideal if ideal else 0.,
        f'MRR@{k}':next((1./(rank+1) for rank,grade in enumerate(grades) if grade>=1),0.),
    }


@dataclass(frozen=True)
class EvaluationQuery:
    id: str
    profile_group: str
    split: str
    text: str
    region: str
    relevance: dict[str,int]


def load_benchmark(path: str | Path, catalog: pd.DataFrame):
    source = json.loads(Path(path).read_text(encoding='utf-8'))
    expected = source['catalog_sha256']
    catalog_path = Path(path).resolve().parents[1]/'jobs_catalog.csv'
    if catalog_path.is_file() and sha256(catalog_path.read_bytes()).hexdigest()!=expected:
        raise ValueError('Catalog changed: review qrels before using benchmark')
    queries = [EvaluationQuery(**entry) for entry in source['queries']]
    if len({query.id for query in queries}) != len(queries):
        raise ValueError('Query IDs must be unique')
    ids = set(catalog.Job_ID)
    groups = {}
    for query in queries:
        if query.split not in ('dev','test') or not query.text.strip() or not set(query.relevance).issubset(ids):
            raise ValueError('Invalid benchmark query')
        if query.profile_group in groups and groups[query.profile_group]!=query.split:
            raise ValueError('Profile group leaked across dev/test')
        groups[query.profile_group] = query.split
    return source,queries


class RankingEvaluator:
    def __init__(self, jobs: pd.DataFrame, queries: list[EvaluationQuery], *, k=5):
        from hybrid_recommender import JobDiversifier
        self.jobs, self.queries, self.k = jobs, queries, k
        self.regions = {str(row.Job_ID):str(row.get('Region_Codes','')).split(';') for _,row in jobs.iterrows()}
        self.companies = {str(row.Job_ID):str(row.get('Company','')) for _,row in jobs.iterrows()}
        self.duplicate_groups = JobDiversifier(jobs).group

    def evaluate(self, engine, name: str, split='test'):
        rows=[]; predictions=[]
        for query in self.queries:
            if query.split!=split:
                continue
            start=time.perf_counter()
            result=engine.match_cv_to_jobs(query.text,self.k,location=query.region)
            elapsed=(time.perf_counter()-start)*1000
            ids=list(result.Job_ID)
            positives=any(grade>0 for grade in query.relevance.values())
            metrics=ranking_metrics(ids,query.relevance,self.k)
            row={'model':name,'query_id':query.id,'split':split,'has_relevant':positives,**metrics,
                 'Empty_Correct':float(not ids) if not positives else None,
                 'Region_Violations':sum(query.region not in self.regions[identifier] for identifier in ids),
                 'Unique_Companies':len({self.companies[identifier] for identifier in ids}),
                 'Near_Duplicate_Extras':len(ids)-len({self.duplicate_groups[identifier] for identifier in ids}),
                 'Returned':len(ids),'Latency_ms':elapsed}
            row[f'JudgedCoverage@{self.k}']=sum(identifier in query.relevance for identifier in ids)/len(ids) if ids else 0.
            rows.append(row)
            predictions.append({'model':name,'query_id':query.id,'region':query.region,'ids':ids,
                                'grades':[query.relevance.get(identifier,0) for identifier in ids]})
        frame=pd.DataFrame(rows)
        positive=frame.loc[frame.has_relevant] if len(frame) else frame
        summary={'model':name,'split':split,'queries':len(frame),'positive_queries':len(positive)}
        for metric in ('Precision','StrictPrecision','Recall','NDCG','MRR'):
            key=f'{metric}@{self.k}'
            summary[key]=float(positive[key].mean()) if len(positive) else None
        negative=frame.loc[~frame.has_relevant] if len(frame) else frame
        summary['Empty_Accuracy']=float(negative.Empty_Correct.mean()) if len(negative) else None
        summary['Region_Violations']=int(frame.Region_Violations.sum()) if len(frame) else 0
        summary['Mean_Unique_Companies']=float(frame.Unique_Companies.mean()) if len(frame) else 0.
        summary['Mean_Near_Duplicate_Extras']=float(frame.Near_Duplicate_Extras.mean()) if len(frame) else 0.
        summary['Mean_Returned']=float(frame.Returned.mean()) if len(frame) else 0.
        summary[f'JudgedCoverage@{self.k}']=float(positive[f'JudgedCoverage@{self.k}'].mean()) if len(positive) else None
        summary['Median_Latency_ms']=float(frame.Latency_ms.median()) if len(frame) else 0.
        return summary,frame,predictions


def run_evaluation(output: str | Path='outputs/evaluation', *, split='test', semantic=True):
    from job_recommender import JobRecommenderSystem
    from hybrid_recommender import HybridJobRecommenderSystem, DEFAULT_WEIGHTS
    from semantic_index import MODEL_REVISION
    root=Path(__file__).resolve().parent
    jobs=pd.read_csv(root/'data/jobs_catalog.csv').fillna('')
    metadata,queries=load_benchmark(root/'data/evaluation/benchmark.json',jobs)
    destination=Path(output); destination.mkdir(parents=True,exist_ok=True)
    engines=[('A_tfidf',lambda:JobRecommenderSystem(jobs,backend='tfidf'))]
    if semantic:
        engines.append(('B_semantic',lambda:JobRecommenderSystem(jobs,backend='sentence-transformers')))
        engines.append(('C_hybrid',lambda:HybridJobRecommenderSystem(jobs)))
    else:
        engines.append(('C_hybrid_lexical',lambda:HybridJobRecommenderSystem(jobs,use_semantic=False)))
    evaluator=RankingEvaluator(jobs,queries)
    summaries=[]; frames=[]; predictions=[]
    for name,build in engines:
        print(f'Preparing {name}',flush=True)
        start=time.perf_counter(); engine=build()
        # Warm-up chỉ dùng văn bản tin công khai. Thời gian xây index/model
        # tách riêng, không trộn với độ trễ CV khi server đã hoạt động.
        if name=='C_hybrid':
            engine._semantic_scores('Public job catalog warm-up')
            if engine.semantic_status!='ready':
                raise RuntimeError('Semantic model unavailable; cannot report a full hybrid comparison')
        setup=time.perf_counter()-start
        summary,frame,pred=evaluator.evaluate(engine,name,split)
        summary['Setup_seconds']=setup
        summaries.append(summary);frames.append(frame);predictions.extend(pred)
        print(json.dumps(summary,ensure_ascii=False),flush=True)
        del engine
    pd.DataFrame(summaries).to_csv(destination/'summary.csv',index=False,encoding='utf-8-sig')
    pd.concat(frames,ignore_index=True).to_csv(destination/'per_query.csv',index=False,encoding='utf-8-sig')
    (destination/'predictions.json').write_text(json.dumps(predictions,ensure_ascii=False,indent=2),encoding='utf-8')
    run={'benchmark_sha256':sha256((root/'data/evaluation/benchmark.json').read_bytes()).hexdigest(),
         'catalog_sha256':metadata['catalog_sha256'],'label_provenance':metadata['label_provenance'],
         'split':split,'weights':DEFAULT_WEIGHTS,'model_revision':MODEL_REVISION,'python':platform.python_version(),
         'semantic':semantic,'summary':summaries}
    (destination/'run_metadata.json').write_text(json.dumps(run,ensure_ascii=False,indent=2),encoding='utf-8')
    return pd.DataFrame(summaries)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',default='outputs/evaluation')
    parser.add_argument('--split',choices=('dev','test'),default='test')
    parser.add_argument('--no-semantic',action='store_true')
    args=parser.parse_args()
    run_evaluation(args.output,split=args.split,semantic=not args.no_semantic)
