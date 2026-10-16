"""Bộ gợi ý kết hợp có thể giải thích, giữ baseline ở job_recommender.py.

Lọc địa điểm -> đối chiếu từ khóa/ngữ nghĩa -> chấm kỹ năng, vị trí, lĩnh vực,
kinh nghiệm -> loại tin gần trùng -> chọn danh sách đa dạng công ty.
Các trọng số là cấu hình thử nghiệm, không phải xác suất được tuyển dụng.
"""
from __future__ import annotations
from dataclasses import dataclass
from difflib import SequenceMatcher
from collections import Counter
import json
import math
import re
import threading

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from experience_matching import experience_fit
from job_recommender import DEFAULT_MODEL, JobRecommenderSystem, TextPreprocessor
from locations import plain_text
from resume_profile import ROLES, ResumeAnalyzer, ResumeProfile, extract_skills, identify_roles

DEFAULT_WEIGHTS = {"Lexical":.15,"Semantic":.25,"Skills":.30,"Title":.15,"Domain":.05,"Experience":.10}
ROLE_DOMAINS = {role[0]: role[3] for role in ROLES}
STACK_LANGUAGES = {"Python","Java","JavaScript","TypeScript","C#","C++","PHP","Go","Ruby","Kotlin","Swift","Dart"}
ROLE_NEIGHBORS = {
    "backend":{"software":.7,"fullstack":.65}, "frontend":{"fullstack":.65,"software":.4},
    "fullstack":{"backend":.7,"frontend":.7,"software":.65},
    "software":{"backend":.7,"frontend":.55,"fullstack":.7,"mobile":.45,"embedded":.35},
    "data_analyst":{"bi_analyst":1.,"data_scientist":.5,"data_engineer":.25},
    "bi_analyst":{"data_analyst":1.,"data_scientist":.4,"data_engineer":.25},
    "data_scientist":{"ai_engineer":.7,"data_analyst":.5,"bi_analyst":.4,"data_engineer":.4},
    "ai_engineer":{"data_scientist":.75,"data_engineer":.3},
    "data_engineer":{"data_scientist":.4,"dba":.4,"backend":.3},
    "cloud":{"devops":.85,"support":.3}, "devops":{"cloud":.85,"support":.3},
    "mobile":{"software":.5}, "security":{"support":.25,"cloud":.25},
}


def role_fit(candidate: tuple[str, ...], job: tuple[str, ...]) -> float:
    if set(candidate) & set(job):
        return 1.0
    return max((ROLE_NEIGHBORS.get(left, {}).get(right, 0.) for left in candidate for right in job), default=0.)


@dataclass(frozen=True)
class SkillEvidence:
    mentioned: frozenset[str]
    required: frozenset[str]
    preferred: frozenset[str]


def skill_evidence(row) -> SkillEvidence:
    """Chỉ gán nhãn bắt buộc/ưu tiên khi câu nguồn nêu rõ; còn lại là mentioned.

    'Chưa thấy trong CV' không có nghĩa ứng viên không có kỹ năng đó. Không
    suy diễn tất cả kỹ năng trong metadata đều là điều kiện bắt buộc.
    """
    mentioned = set(extract_skills(str(row['Skills'])))
    required, preferred = set(), set()
    text = str(row.get('Original_Requirements', row.get('Requirements','')))
    for sentence in re.split(r"\n+|(?<=[.;])\s+", text):
        normalized = plain_text(sentence)
        found = set(extract_skills(sentence)) & mentioned
        if re.search(r"\b(uu tien|loi the|nice[- ]to[- ]have|preferred|optional)\b", normalized):
            preferred.update(found)
        elif re.search(r"\b(bat buoc|must[- ]have|mandatory)\b|required(?: skills| technologies)?\s*[:：]", normalized):
            required.update(found)
    preferred.difference_update(required)
    return SkillEvidence(frozenset(mentioned), frozenset(required), frozenset(preferred))


def skill_fit(candidate: tuple[str, ...], evidence: SkillEvidence) -> tuple[float, list[str], list[str]]:
    weights = {skill:2. if skill in evidence.required else .5 if skill in evidence.preferred else 1.
               for skill in evidence.mentioned}
    covered = set(candidate) & evidence.mentioned
    score = sum(weights[skill] for skill in covered) / sum(weights.values()) if weights else 0.
    return score, sorted(covered), sorted(evidence.mentioned - set(candidate))


def company_key(row) -> str:
    # Ưu tiên tên gốc để việc Việt/Anh không làm đổi nhóm công ty.
    value = plain_text(row.get('Original_Company', row.get('Company','')))
    return re.sub(r'\W+', ' ', value).strip()


class JobDiversifier:
    """Nhóm tin gần trùng cùng công ty/cùng vùng; không sửa hoặc xóa catalog.

    Hai tin khác kỹ năng hoặc khác cấp bậc không được coi là trùng chỉ vì cùng
    Role_Code. Ngưỡng được cố định trước khi đánh giá tập test.
    """
    def __init__(self, jobs: pd.DataFrame):
        self.company = {str(row.Job_ID): company_key(row) for _,row in jobs.iterrows()}
        self.group = {str(job_id):str(job_id) for job_id in jobs.Job_ID}
        records = [row for _,row in jobs.iterrows()]
        for index, left in enumerate(records):
            company = self.company[str(left.Job_ID)]
            if not company:
                continue
            left_title = self._title(left)
            left_text = self._description(left)
            for right in records[:index]:
                if self.company[str(right.Job_ID)] != company:
                    continue
                if str(left.get('Region_Codes','')) != str(right.get('Region_Codes','')):
                    continue
                right_title = self._title(right)
                # Giữ sự khác biệt Junior/Senior/Lead, kể cả JD dùng chung.
                if self._seniority(left_title) != self._seniority(right_title):
                    continue
                title_similarity = SequenceMatcher(None, left_title, right_title).ratio()
                if title_similarity < .88:
                    continue
                right_text = self._description(right)
                if len(left_text) < 30 or len(right_text) < 30:
                    continue
                if SequenceMatcher(None, left_text, right_text, autojunk=False).ratio() >= .88:
                    self.group[str(left.Job_ID)] = self.group[str(right.Job_ID)]
                    break

    @staticmethod
    def _title(row):
        return re.sub(r'\W+', ' ', plain_text(row.get('Original_Title',row['Title']))).strip()

    @staticmethod
    def _description(row):
        # Giới hạn độ dài cho phép so gần trùng trên CPU; không dùng các câu
        # tóm tắt được tạo cho giao diện vì có thể làm hai JD khác nhau giống nhau.
        return plain_text(row.get('Original_Job_Description',row['Job_Description']))[:2500]

    @staticmethod
    def _seniority(title):
        return tuple(word for word in ('intern','fresher','junior','senior','lead','truong phong') if word in title)

    def select(self, ranked: pd.DataFrame, top_n: int, *, max_per_company=2) -> pd.DataFrame:
        unique, seen = [], set()
        for index,row in ranked.iterrows():
            identifier = str(row.Job_ID); group = self.group[identifier]
            if group in seen:
                continue
            unique.append(index); seen.add(group)
        selected = unique[:top_n]
        companies = Counter(self.company[str(ranked.loc[i,'Job_ID'])] for i in selected)
        for index in unique[top_n:]:
            company = self.company[str(ranked.loc[index,'Job_ID'])]
            if not company or companies[company] >= max_per_company:
                continue
            overfull = [i for i in reversed(selected) if self.company[str(ranked.loc[i,'Job_ID'])] and
                        companies[self.company[str(ranked.loc[i,'Job_ID'])]] > max_per_company]
            if not overfull:
                break
            replace = min(overfull,key=lambda i:float(ranked.loc[i,'Similarity_Score']))
            # Chỉ đổi lấy công ty khác nếu độ phù hợp còn gần nhau. Không để
            # hạn ngạch công ty đưa tin rất yếu lên trước tin phù hợp hơn.
            if float(ranked.loc[index,'Similarity_Score']) < float(ranked.loc[replace,'Similarity_Score'])*.85:
                continue
            companies[self.company[str(ranked.loc[replace,'Job_ID'])]] -= 1
            companies[company] += 1
            selected.remove(replace); selected.append(index)
        result = ranked.loc[selected].sort_values(['Similarity_Score','Job_ID'], ascending=[False,True]).copy()
        result['Rank'] = np.arange(1,len(result)+1)
        return result.reset_index(drop=True)


class HybridJobRecommenderSystem(JobRecommenderSystem):
    def __init__(self, jobs: pd.DataFrame, *, use_semantic=True, model_name=DEFAULT_MODEL,
                 weights: dict | None = None, diversify=True, min_score=.12):
        self.weights = dict(DEFAULT_WEIGHTS if weights is None else weights)
        if set(self.weights) != set(DEFAULT_WEIGHTS) or any(not math.isfinite(v) or v < 0 for v in self.weights.values()) or not math.isclose(sum(self.weights.values()),1.):
            raise ValueError('Hybrid weights must contain the six components and sum to 1')
        self.use_semantic = bool(use_semantic)
        self.model_name = model_name
        self.diversify = bool(diversify)
        if not 0 <= min_score <= 1:
            raise ValueError('min_score must be between 0 and 1')
        self.min_score = min_score
        super().__init__(jobs, backend='tfidf')
        self.backend = 'hybrid' if use_semantic else 'hybrid-lexical'
        self.semantic_status = 'not_loaded' if use_semantic else 'disabled'
        self._semantic = None
        self._semantic_lock = threading.Lock()
        self._documents = [self._job_to_text(row) for _,row in self._jobs.iterrows()]
        self._evidence = [skill_evidence(row) for _,row in self._jobs.iterrows()]
        self._roles = []
        for _,row in self._jobs.iterrows():
            role_codes = tuple(role[0] for role in identify_roles(str(row.get('Original_Title',row.Title))))
            code = str(row.get('Role_Code',''))
            self._roles.append(role_codes or ((code,) if code in ROLE_DOMAINS else ()))
        self.diversifier = JobDiversifier(self._jobs)

    @staticmethod
    def _job_to_text(row):
        title = str(row.get('Original_Title',row['Title']))
        domain = str(row.get('Original_Domain',row['Domain']))
        description = str(row.get('Original_Job_Description',row['Job_Description']))
        requirements = str(row.get('Original_Requirements',row.get('Requirements','')))
        return TextPreprocessor.normalize(f"{title}. {row.get('Title_EN','')}. {row['Skills']}. {domain}. {row.get('Domain_EN','')}. {description} {requirements}")

    def _semantic_scores(self, text):
        if not self.use_semantic:
            return np.zeros(len(self._jobs)), False
        with self._semantic_lock:
            if self._semantic is None and self.semantic_status != 'unavailable':
                try:
                    from semantic_index import PublicSemanticIndex
                    self._semantic = PublicSemanticIndex(self._documents, model_name=self.model_name)
                    self.semantic_status = 'ready'
                except (ImportError, OSError, RuntimeError, ValueError):
                    # API trả trạng thái này cho giao diện, không giả vờ có
                    # điểm ngữ nghĩa khi thiếu thư viện/model hoặc tải lỗi.
                    self.semantic_status = 'unavailable'
        if self._semantic is None:
            return np.zeros(len(self._jobs)), False
        return self._semantic.similarity(text), True

    def _finish(self, scores, top_n, eligible, components=None, *, exclude=None):
        ranked = self._rank(scores,len(self._jobs),exclude_position=exclude,eligible_positions=eligible,components=components)
        if self.diversify:
            return self.diversifier.select(ranked,top_n)
        return ranked.head(top_n).copy()

    def match_cv_to_jobs(self, cv_text, top_n=5, *, location=None, profile: ResumeProfile | None=None):
        self._validate_top_n(top_n)
        if not isinstance(cv_text,str) or not cv_text.strip():
            raise ValueError('cv_text must be a nonempty string')
        eligible = self._eligible_positions(location)
        profile = profile or ResumeAnalyzer().analyze(cv_text)
        if profile.text != cv_text:
            raise ValueError('CV profile does not match current text')
        if not eligible:
            return self._rank(np.zeros(len(self._jobs)),top_n,eligible_positions=[])
        lexical = np.clip(cosine_similarity(self._encoder.transform([profile.matching_text]),self._job_vectors).ravel(),0,1)
        semantic, semantic_available = self._semantic_scores(profile.matching_text)
        components = {field:np.zeros(len(self._jobs)) for field in DEFAULT_WEIGHTS}
        components.update(Lexical=lexical,Semantic=semantic)
        explanations, per_job_weights = [], []
        cv_coverage, job_coverage, intent_supported = [], [], []
        cv_domains = {ROLE_DOMAINS[code] for code in profile.role_codes if code in ROLE_DOMAINS}
        target_stack = set(profile.target_skills) & STACK_LANGUAGES
        if not target_stack:
            candidate_stack = set(profile.skills) & STACK_LANGUAGES
            target_stack = candidate_stack if len(candidate_stack)==1 else set()
        for index,row in self._jobs.iterrows():
            evidence = self._evidence[index]
            coverage, matched, missing = skill_fit(profile.skills,evidence)
            fit, exp_status = experience_fit(profile.experience_years,float(row.Experience_Years),known=bool(row.get('Experience_Known',True)))
            candidate_coverage = len(matched)/len(profile.skills) if profile.skills else 0.
            missing_required = evidence.required-set(profile.skills)
            required_penalty = 1.-.5*len(missing_required)/len(evidence.required) if evidence.required else 1.
            # Kết hợp tỷ lệ kỹ năng của tin được bao phủ và tỷ lệ kỹ năng CV
            # được công việc sử dụng, tránh tin chỉ có một kỹ năng chung thắng
            # tin đúng chuyên môn nhưng nhắc nhiều công nghệ hơn.
            components['Skills'][index] = (.6*candidate_coverage+.4*coverage)*required_penalty
            raw_role_score = role_fit(profile.role_codes,self._roles[index])
            title_score = raw_role_score
            requested_stack = set(profile.target_skills)&STACK_LANGUAGES
            job_title_stack = set(extract_skills(str(row.get('Original_Title',row.Title))))&STACK_LANGUAGES
            stack_conflict = bool(requested_stack and job_title_stack and not requested_stack&job_title_stack)
            intent_supported.append(not stack_conflict and
                                    (not profile.role_explicit or not self._roles[index] or raw_role_score>=.35))
            if target_stack and evidence.mentioned & STACK_LANGUAGES and not (target_stack & evidence.mentioned):
                title_score *= .25
            components['Title'][index] = title_score
            cv_coverage.append(candidate_coverage); job_coverage.append(coverage)
            components['Domain'][index] = float(bool(cv_domains & {ROLE_DOMAINS[code] for code in self._roles[index] if code in ROLE_DOMAINS}))
            components['Experience'][index] = fit
            active = dict(self.weights)
            if not semantic_available: active['Semantic'] = 0.
            if not profile.skills or not evidence.mentioned: active['Skills'] = 0.
            if not profile.role_codes or not self._roles[index]: active['Title'] = 0.; active['Domain'] = 0.
            if exp_status == 'unknown': active['Experience'] = 0.
            total = sum(active.values())
            active = {field:weight/total for field,weight in active.items()} if total else {field:0. for field in active}
            per_job_weights.append(active)
            explanations.append({'matched':matched,'missing':missing,'required_missing':sorted(evidence.required-set(profile.skills)),
                                 'required':sorted(evidence.required),'preferred':sorted(evidence.preferred),'experience_status':exp_status})
        scores = np.array([sum(per_job_weights[i][field]*components[field][i] for field in components) for i in range(len(self._jobs))])
        # Ngữ nghĩa thường có nền dương ngay cả với nội dung không liên quan.
        # Cần ít nhất một tín hiệu nghề nghiệp, kỹ năng hoặc nội dung đáng kể.
        eligible = [i for i in eligible if intent_supported[i] and scores[i]>=self.min_score and
                    (components['Title'][i]>0 or explanations[i]['matched'] or lexical[i]>.04 or (semantic_available and semantic[i]>.4))]
        result = self._finish(scores,top_n,eligible,components)
        by_id = {str(row.Job_ID):i for i,row in self._jobs.iterrows()}
        indices = [by_id[str(identifier)] for identifier in result.Job_ID]
        result['Matched_Skills'] = ['; '.join(explanations[i]['matched']) for i in indices]
        result['Not_Mentioned_Skills'] = ['; '.join(explanations[i]['missing']) for i in indices]
        result['Missing_Required_Skills'] = ['; '.join(explanations[i]['required_missing']) for i in indices]
        result['Required_Skills'] = ['; '.join(explanations[i]['required']) for i in indices]
        result['Preferred_Skills'] = ['; '.join(explanations[i]['preferred']) for i in indices]
        result['Experience_Status'] = [explanations[i]['experience_status'] for i in indices]
        result['Candidate_Experience_Years'] = profile.experience_years
        result['Component_Weights'] = [per_job_weights[i] for i in indices]
        result['CV_Skill_Coverage'] = [cv_coverage[i] for i in indices]
        result['Job_Skill_Coverage'] = [job_coverage[i] for i in indices]
        result['Job_Skills_Count'] = [len(self._evidence[i].mentioned) for i in indices]
        result['Ranking_Method'] = 'hybrid' if semantic_available else 'hybrid-lexical'
        return result

    def recommend_similar_jobs(self, job_id, top_n=5, *, location=None):
        self._validate_top_n(top_n)
        if job_id not in self._id_to_position:
            raise KeyError(job_id)
        position = self._id_to_position[job_id]
        lexical = cosine_similarity(self._job_vectors[position:position+1],self._job_vectors).ravel()
        semantic, available = self._semantic_scores(self._documents[position])
        scores = .5*lexical+.5*semantic if available else lexical
        eligible = [i for i in self._eligible_positions(location)
                    if self.diversifier.group[str(self._jobs.iloc[i].Job_ID)] != self.diversifier.group[job_id]]
        return self._finish(scores,top_n,eligible)
