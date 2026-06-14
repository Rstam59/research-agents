from urllib.parse import urlparse 
from typing import List 

from research_agent.state import Source, ScoredSource

HIGH_QUALITY_SOURCES = [
    "nature.com",
    "sciencemag.org",
    "edu",
    'gov',
    "who.int",
    "un.org",
    "imf.org",
    "worldbank.org",
    "nejm.org",
    'arxiv.org',
    "biorxiv.org",
    "ssrn.com",
    "researchgate.net",
    "jstor.org",
    "ieee.org",
    "nasa.gov",
]


LOW_QUALITY_HINTS = [
    "top 10",
    "best",
    "click here",
    "sponsored",
    "advertisement",
    "blog",
    "buy now"
]

def get_domain(url: str) -> str:
        parsed_url = urlparse(url)
        return parsed_url.netloc.lower().replace("www.", "")


def classify_source_type(domain: str) -> str:
        if domain.endswith('.gov') or 'gov.' in domain:
            return 'Government'
        if domain.endswith('.edu') or 'edu.' in domain:
            return 'Educational'
        if domain.endswith('.org') or 'org.' in domain:
            return 'Non-Profit'
        if any(pub in domain for pub in ['nature', 'sciencemag', 'nejm', 'arxiv', 'biorxiv', 'ssrn', 'researchgate', 'jstor', 'ieee', 'nasa']):
            return 'Academic'
        if any(org in domain for org in ['who', 'un', 'imf', 'worldbank']):
            return 'International Organization'
        
        return 'general_web'


def score_source(source: Source) -> ScoredSource:
     title = source.get('title', '')
     url = source.get('url', '')
     snippet = source.get('snippet', '')

     domain = get_domain(url)
     source_type = classify_source_type(domain)

     score = 0.5
     reasons = []

     if source_type in {
          'Government',
          'Educational',
          "International Organization",
          "Academic"
     }:
          score += 0.3 
          reasons.append(f"Strong domain type: {source_type}")

    
     if len(snippet) > 120:
          score += 0.1
          reasons.append('Snippet has enough content to inspect')

     text = f'{title} {snippet}'.lower()

     if any(hint in text for hint in LOW_QUALITY_HINTS):
          score -= 0.25
          reasons.append('Contains low-quality or promotional wording')

     
     if not url:
          score -= 0.4 
          reasons.append('Missing URL')

     score = max(0, min(score, 1.0))
     
     return {
          **source,
          'quality_score': score,
          'quality_reason': '; '.join(reasons) if reasons else "No strong quality signals found",
          'source_type': source_type,
          'is_reliable': score >= 0.65

     }

def score_sources(sources: List[Source]) -> List[ScoredSource]:
     return [score_source(source) for source in sources]
    