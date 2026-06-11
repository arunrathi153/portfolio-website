# job_matcher.py
import re
from typing import Dict, List, Optional
from datetime import datetime
from resume_parser import (
    DEGREE_SYNONYMS, BRANCH_SYNONYMS, COURSE_DURATION
)

CURRENT_YEAR = datetime.today().year

# Helper functions
def _variant_pattern(variant: str) -> str:
    return r"\b" + re.sub(r"\s+", r"\\s+", re.escape(variant)) + r"\b"

def _contains_variant(text: str, variants: List[str]) -> bool:
    for v in variants:
        if re.search(_variant_pattern(v), text, flags=re.IGNORECASE):
            return True
    return False

def _extract_year_from_text(text: str) -> Optional[int]:
    m = re.search(r'\b(19[5-9]\d|20\d{2}|21\d{2})\b', text)
    if m:
        y = int(m.group(1))
        if 1950 <= y <= (CURRENT_YEAR + 10):
            return y
    return None

def normalize_requirement(req: str) -> (Optional[str], Optional[str], Optional[str], Optional[int]):
    if not req:
        return (None, None, None, None)
    s = req.lower()
    s = re.sub(r'[-_/]', ' ', s)
    s = re.sub(r'[(),]+', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()

    year = _extract_year_from_text(s)

    # Degree
    deg = None
    for norm, variants in DEGREE_SYNONYMS.items():
        if _contains_variant(s, variants):
            deg = 'btech' if norm in ('btech', 'be') else norm
            break

    # Branch & specialization
    branch = None
    spec = None
    for norm, variants in BRANCH_SYNONYMS.items():
        if _contains_variant(s, variants):
            if norm in ('aiml', 'ai', 'ml', 'ds'):
                spec = 'aiml' if norm in ('aiml', 'ai', 'ml') else 'ds'
            else:
                branch = norm

    return deg, branch, spec, year

def _estimate_grad_from_start(deg: str, start_year: int) -> int:
    dur = COURSE_DURATION.get(deg, 3)
    return start_year + dur

def education_matches(candidate_resume: Dict, requirement_str: str) -> bool:
    deg_req, branch_req, spec_req, year_req = normalize_requirement(requirement_str or "")
    if not deg_req and not branch_req and not spec_req and not year_req:
        return True

    edus = candidate_resume.get('education', [])
    if not edus:
        return False

    for ed in edus:
        cand_deg = (ed.get('degree') or "").lower()
        cand_branch = ed.get('branch') or None
        cand_spec = ed.get('specialization') or None
        cand_end_year = ed.get('year')
        cand_start_year = ed.get('start_year')

        if cand_deg == 'be':
            cand_deg = 'btech'

        # Degree match
        if deg_req and cand_deg != deg_req:
            continue

        # Branch match
        if branch_req:
            if not cand_branch and cand_spec and cand_spec == branch_req:
                pass
            elif cand_branch != branch_req:
                continue

        # Specialization match
        if spec_req:
            if not cand_spec or cand_spec != spec_req:
                if not (cand_branch and cand_branch == spec_req):
                    continue

        # Year match
        if not year_req:
            return True

        if cand_end_year and cand_end_year == year_req:
            return True

        start_for_calc = None
        if cand_start_year:
            start_for_calc = cand_start_year
        elif cand_end_year and cand_end_year <= CURRENT_YEAR and cand_end_year < year_req:
            start_for_calc = cand_end_year

        if start_for_calc:
            est_grad = _estimate_grad_from_start(cand_deg or deg_req, start_for_calc)
            if est_grad == year_req:
                return True

        # Fallback: search raw text within ±2 lines of degree mention
        raw_text = candidate_resume.get('raw_text', '')
        if raw_text:
            lines = raw_text.splitlines()
            for i, line in enumerate(lines):
                if _contains_variant(line.lower(), DEGREE_SYNONYMS.get(deg_req, [])):
                    context = " ".join(lines[max(0, i-2):min(len(lines), i+3)])
                    if str(year_req) in context:
                        return True

    return False

def score_candidate(resume: Dict, job_requirements: Dict, weights: Dict = None) -> Dict:
    weights = weights or {'skills': 0.6, 'experience': 0.3, 'education': 0.1}

    # Skills
    if isinstance(job_requirements.get('skills'), str):
        job_skills = [s.strip().lower() for s in job_requirements['skills'].split(',') if s.strip()]
    else:
        job_skills = [s.strip().lower() for s in job_requirements.get('skills', [])]

    resume_skills = [s.lower() for s in resume.get('skills', [])]
    matched_skills = [s for s in resume_skills if s in job_skills]
    skills_score = (len(matched_skills) / max(1, len(job_skills))) if job_skills else 0

    # Experience (with months support)
    req_exp = job_requirements.get('experience', 0) or 0
    cand_exp = resume.get('experience', 0) or 0
    if cand_exp < 1 and cand_exp > 0:
        cand_exp = round(cand_exp, 1)  # Keep decimal for months
    if req_exp <= 0:
        experience_score = 1.0
        experience_match = True
    else:
        experience_score = min(1.0, cand_exp / req_exp)
        experience_match = cand_exp >= req_exp

    # Education
    req_edu = job_requirements.get('education')
    if not req_edu:
        education_score = 1.0
        education_match = True
    else:
        education_match = education_matches(resume, req_edu)
        education_score = 1.0 if education_match else 0.0

    total = (
        skills_score * weights.get('skills', 0)
        + experience_score * weights.get('experience', 0)
        + education_score * weights.get('education', 0)
    )
    total_score = round(total * 100, 2)

    return {
        'matched_skills': matched_skills,
        'skills_score': round(skills_score * 100, 2),
        'experience_match': experience_match,
        'education_match': education_match,
        'total_score': total_score
    }

def rank_candidates(resumes: List[Dict], job_requirements: Dict, weights: Dict = None) -> List[Dict]:
    results = []
    for r in resumes:
        sc = score_candidate(r, job_requirements, weights)
        results.append({
            'name': r.get('name') or r.get('file_name') or 'unknown',
            'file_name': r.get('file_name'),
            'details': r,
            'score': sc
        })
    results.sort(key=lambda x: (x['score']['total_score'], x['score']['skills_score'], x['details'].get('experience', 0)), reverse=True)
    return results
