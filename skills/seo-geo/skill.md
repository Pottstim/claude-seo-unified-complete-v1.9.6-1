---
name: seo-geo
description: "Generative Engine Optimization (GEO) for AI search. Analyzes AI search readiness for Google AI Overviews, ChatGPT, Perplexity, and Claude. Checks llms.txt support, answer-first formatting, and citation readiness."
user-invokable: true
argument-hint: "<url>"
license: MIT
version: "1.9.6-unified"
---

# SEO GEO - AI Search Optimization

## AI Search Platforms

1. **Google AI Overviews** (SGE)
2. **ChatGPT** (with browsing)
3. **Perplexity AI**
4. **Claude**
5. **Microsoft Copilot**

## Optimization Signals

### Answer-First Formatting
- Clear, concise answers (40-60 words)
- Question-based headings
- Bullet point summaries
- Definition boxes

### Citation Readiness
- Authoritative sources linked
- Data/research cited
- Source attribution
- Publication dates visible

### llms.txt Support
- `/llms.txt` file present
- Structured content for AI crawlers
- Clear site purpose and context

### AI Crawler Support
- GPTBot allowed
- ClaudeBot allowed
- PerplexityBot allowed
- Google-Extended allowed

## Scoring (0-10 points)

| Signal | Points |
|--------|--------|
| Answer-first content | 2 |
| Question headings | 2 |
| llms.txt present | 2 |
| AI crawlers allowed | 2 |
| Citation quality | 2 |

## Output

```json
{
  "url": "https://example.com",
  "score": 6,
  "max_score": 10,
  "ai_readiness": {
    "answer_first": {"score": 2, "details": "Clear definitions and summaries"},
    "question_headings": {"score": 1, "details": "Some FAQ sections present"},
    "llms_txt": {"score": 0, "details": "No llms.txt found"},
    "crawler_access": {
      "gptbot": "allowed",
      "claudebot": "allowed", 
      "perplexitybot": "blocked",
      "google_extended": "allowed"
    },
    "citations": {"score": 2, "details": "External sources linked"}
  },
  "recommendations": [
    "Create /llms.txt for AI crawler context",
    "Allow PerplexityBot in robots.txt",
    "Add more question-based headings"
  ]
}
```
