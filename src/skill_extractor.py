import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.skills_db import ALL_SKILLS, CATEGORY_LABELS, SKILLS


def extract_skills(text: str) -> dict:
    text_lower = text.lower()
    found: dict[str, list[str]] = {cat: [] for cat in SKILLS}

    for skill in ALL_SKILLS:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text_lower):
            category = CATEGORY_LABELS.get(skill, "other")
            if skill not in found.get(category, []):
                found[category].append(skill)

    return {k: v for k, v in found.items() if v}


def get_skill_overlap(resume_skills: dict, jd_skills: dict) -> dict:
    resume_flat = {s for skills in resume_skills.values() for s in skills}
    jd_flat = {s for skills in jd_skills.values() for s in skills}

    matched = resume_flat & jd_flat
    missing = jd_flat - resume_flat
    extra = resume_flat - jd_flat

    return {
        "matched": sorted(matched),
        "missing": sorted(missing),
        "extra": sorted(extra),
        "match_rate": len(matched) / len(jd_flat) if jd_flat else 0.0,
    }
