# DataForSEO Extension

Adds live SERP data, keyword research, and backlink analysis capabilities to Claude SEO.

## Features

- **SERP Analysis**: Real-time search engine rankings for any keyword
- **Keyword Research**: Search volumes, difficulty scores, related keywords
- **Backlink Analysis**: Competitor backlink profiles, referring domains
- **Rank Tracking**: Monitor position changes over time
- **Local Search**: Geo-specific SERP data

## Installation

```bash
cd extensions/dataforseo
bash install.sh
```

## API Pricing

- **Free tier**: $100 credit on signup
- **Pay-as-you-go**: ~$0.25 per SERP request
- **Volume discounts**: Available for 10k+ requests/month

Get started: https://app.dataforseo.com

## Usage

```bash
# Get SERP rankings for keyword
/seo dataforseo serp "AI SEO tools" --location "United States"

# Analyze backlinks
/seo dataforseo backlinks https://competitor.com

# Keyword research
/seo dataforseo keywords "content marketing" --limit 50
```

## Configuration

Credentials stored in: `~/.antigravity/.env`

```env
DATAFORSEO_USERNAME=your_username
DATAFORSEO_PASSWORD=your_password
```

## Troubleshooting

**Connection fails:**
```bash
# Test credentials manually
curl -u username:password https://api.dataforseo.com/v3/appendix/user_data
```

**Rate limits:**
Default: 10 requests/minute. Upgrade plan for higher limits.

## Support

- Documentation: https://docs.dataforseo.com
- API Status: https://status.dataforseo.com
