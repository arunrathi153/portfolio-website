import re
from typing import List, Dict, Optional
from datetime import datetime
import nltk
from dateutil import parser as date_parser

CURRENT_YEAR = datetime.today().year

# Download punkt tokenizer if not present
try:
    nltk.data.find("tokenizers/punkt")
except Exception:
    try:
        nltk.download("punkt", quiet=True)
    except Exception:
        pass

DEGREE_SYNONYMS = {
    "btech": ["btech", "b.tech", "b e", "be", "bachelor of technology", "bachelor of engineering", "b.tech."],
    "bsc": ["bsc", "b.sc", "bachelor of science"],
    "bba": ["bba", "b.b.a", "bachelor of business administration"],
    "mba": ["mba", "m.b.a", "master of business administration"],
    "mtech": ["mtech", "m.tech", "master of technology"],
    "msc": ["msc", "m.sc", "master of science"],
    "phd": ["phd", "ph.d", "doctor of philosophy"],
    "12th": ["12th", "class 12", "class xii", "xii", "senior secondary", "higher secondary", "hsc"],
    "10th": ["10th", "class 10", "class x", "x", "secondary", "matriculation", "ssc", "high school"]
}

BRANCH_SYNONYMS = {
    "cse": ["cse", "computer science", "cs", "cst", "computer science and engineering", "computer engineering", "comp sci"],
    "it": ["it", "information technology", "informationtechnology"],
    "ece": ["ece", "electronics and communication", "electronics & communication", "electronics and comm", "electronics"],
    "eee": ["eee", "electrical and electronics", "electrical & electronics", "electrical"],
    "mech": ["mechanical", "mech", "mechanical engineering"],
    "civil": ["civil", "ce", "civil engineering"],
    "aiml": ["aiml", "ai/ml", "ai ml", "ai-ml", "ai & ml", "artificial intelligence and machine learning"],
    "ai": ["ai", "artificial intelligence"],
    "ml": ["ml", "machine learning"],
    "ds": ["data science", "ds", "data-science"]
}

COURSE_DURATION = {
    "btech": 4, "be": 4,
    "bsc": 3, "bba": 3,
    "mba": 2, "mtech": 2,
    "msc": 2, "phd": 5
}

def _variant_pattern(variant: str) -> str:
    escaped = re.escape(variant)
    escaped = escaped.replace(r'\ ', r'\s+')  # allow flexible spaces
    return r'(?<!\w)' + escaped + r'(?!\w)'

def _contains_variant(text: str, variants: List[str]) -> bool:
    for v in variants:
        pattern = _variant_pattern(v)
        if re.search(pattern, text, flags=re.IGNORECASE):
            return True
    return False

def _find_degree_in_text(text: str) -> Optional[str]:
    for norm, variants in DEGREE_SYNONYMS.items():
        for v in variants:
            pattern = _variant_pattern(v)
            if re.search(pattern, text, flags=re.IGNORECASE):
                return norm
    return None

def _find_branch_in_text(text: str) -> Optional[str]:
    for norm, variants in BRANCH_SYNONYMS.items():
        for v in variants:
            pattern = _variant_pattern(v)
            if re.search(pattern, text, flags=re.IGNORECASE):
                return norm
    return None

def _parse_date(text: str) -> Optional[datetime]:
    try:
        dt = date_parser.parse(text, fuzzy=True, default=datetime(1900,1,1))
        return dt
    except Exception:
        return None

# --- NEW FUNCTION to extract experience section from full resume text ---
def extract_experience_section(text: str) -> str:
    lines = text.splitlines()
    start_idx = None
    end_idx = None

    for i, line in enumerate(lines):
        if re.search(r'\bexperience\b', line, re.IGNORECASE):
            start_idx = i
            break

    if start_idx is None:
        # Experience section not found, return full text (fallback)
        return text

    for j in range(start_idx + 1, len(lines)):
        if re.search(r'\b(education|skills|projects|certifications|achievements|summary|objective)\b', lines[j], re.IGNORECASE):
            end_idx = j
            break

    if end_idx is None:
        end_idx = len(lines)

    return "\n".join(lines[start_idx:end_idx])

# Parse date strings like "June 2024"
def parse_date_simple(date_str: str) -> Optional[datetime]:
    try:
        return datetime.strptime(date_str, "%B %Y")
    except Exception:
        try:
            return datetime.strptime(date_str, "%b %Y")
        except Exception:
            return None

# Calculate total experience from date ranges in experience section
def calculate_experience(exp_section_text: str) -> float:
    today = datetime.today()
    total_months = 0

    date_ranges = re.findall(
        r'([A-Za-z]{3,9} \d{4})\s*[-–—to]+\s*(current|present|ongoing|now|[A-Za-z]{3,9} \d{4})',
        exp_section_text, flags=re.IGNORECASE
    )
    if not date_ranges:
        return 0.0

    for start_str, end_str in date_ranges:
        start_date = parse_date_simple(start_str)
        if end_str.lower() in ('current', 'present', 'ongoing', 'now'):
            end_date = today
        else:
            end_date = parse_date_simple(end_str)

        if start_date and end_date and end_date >= start_date:
            months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
            total_months += months

    years = total_months // 12
    months = total_months % 12

    # Modified part: convert months to decimal in 0.1 increments; if months >=10, count as full year
    if months >= 10:
        years += 1
        months = 0

    experience = round(years + months * 0.1, 1)
    return experience


# Main experience extraction function to call inside resume parsing
def extract_experience(text: str) -> float:
    exp_section = extract_experience_section(text)
    return calculate_experience(exp_section)

# --- rest of your existing code for education, skills etc. ---

def extract_education(text: str) -> List[Dict]:
    lines = [ln.rstrip() for ln in text.splitlines()]
    lines_norm = [re.sub(r'[-_/•\u2022]', ' ', ln).strip() for ln in lines]

    edu_start = None
    for i, ln in enumerate(lines_norm):
        if re.search(r'\b(education|academic|academics|qualifications|qualification|education and qualifications|educational)\b', ln, flags=re.IGNORECASE):
            edu_start = i + 1
            break
    if edu_start is None:
        edu_start = 0

    edu_end = None
    for j in range(edu_start, len(lines_norm)):
        if re.search(r'\b(experience|project|projects|skills|certification|certifications|internship|work experience|achievements)\b', lines_norm[j], flags=re.IGNORECASE):
            edu_end = j
            break
    if edu_end is None:
        edu_end = len(lines_norm)

    edu_block_lines = lines_norm[edu_start:edu_end]
    results: List[Dict] = []

    for idx in range(len(edu_block_lines)):
        window_lines = []
        for k in range(idx-2, idx+3):
            if 0 <= k < len(edu_block_lines):
                window_lines.append(edu_block_lines[k])
        window_text = " ".join(window_lines).strip()

        clean_window_text = re.sub(r'[\(\)&]', ' ', window_text).lower()
        clean_window_text = re.sub(r'\s+', ' ', clean_window_text).strip()

        degree = _find_degree_in_text(clean_window_text)
        branch = _find_branch_in_text(clean_window_text)
        specialization = None
        if branch in ('aiml', 'ds'):
            specialization = branch
            branch = None
        else:
            for spec_key in ('aiml', 'ds', 'ai', 'ml'):
                if _contains_variant(clean_window_text, BRANCH_SYNONYMS.get(spec_key, [])):
                    specialization = 'aiml' if spec_key in ('aiml', 'ai', 'ml') else 'ds'
                    break

        start_year = None
        grad_year = None
        m = re.search(
            r'(\b(19[5-9]\d|20\d{2})\b)\s*[-–—to]+\s*(current|present|ongoing|curr|\b(19[5-9]\d|20\d{2})\b)',
            clean_window_text, flags=re.IGNORECASE)
        if m:
            try:
                start_year = int(m.group(1))
                end_val = m.group(3).lower()
                if end_val in ('current', 'present', 'ongoing', 'curr'):
                    grad_year = start_year + COURSE_DURATION.get(degree, 4)
                else:
                    grad_year = int(end_val)
            except:
                pass
        else:
            years_found = [int(y) for y in re.findall(r'\b(19[5-9]\d|20\d{2})\b', clean_window_text)]
            if years_found:
                grad_year = max(years_found)

        if not grad_year and start_year and degree:
            grad_year = start_year + COURSE_DURATION.get(degree, 4)

        if degree or branch or specialization or grad_year or start_year:
            results.append({
                'degree': degree,
                'branch': branch,
                'specialization': specialization,
                'year': grad_year,
                'start_year': start_year,
                'context': window_text
            })

    unique = []
    seen = set()
    for r in results:
        key = (r.get('degree'), r.get('branch'), r.get('specialization'), r.get('year'), r.get('start_year'))
        if key not in seen:
            seen.add(key)
            unique.append(r)

    return unique

def extract_skills(text: str, skills_pool: Optional[List[str]] = None) -> List[str]:
    DEFAULT_SKILLS = [
        'python', 'java', 'c++', 'c', 'machine learning', 'deep learning',
        'data science', 'sql', 'javascript', 'html', 'css', 'aws', 'azure',
        'django', 'flask', 'react', 'node', 'tensorflow', 'pytorch', 'git'
    ]
    pool = skills_pool or DEFAULT_SKILLS
    text_lower = text.lower()
    found = []
    for skill in pool:
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found.append(skill)
    return sorted(set(found))

def extract_resume_details(text: str, skills_pool: Optional[List[str]] = None) -> Dict:
    return {
        'skills': extract_skills(text, skills_pool),
        'experience': extract_experience(text),
        'education': extract_education(text),
        'raw_text': text
    }
