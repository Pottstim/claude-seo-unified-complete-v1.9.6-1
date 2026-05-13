# SEO Business Tool - Quick Start

Turn your SEO analysis engine into a client-facing business tool in minutes.

## 30-Second Start

```bash
# Start the API server
make api

# Open the dashboard (in another terminal)
make dashboard

# Or just open dashboard/index.html in your browser
```

Visit http://localhost:5000 for API, http://localhost:8000 for dashboard.

## Architecture

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   Dashboard     │─────▶│   REST API      │─────▶│   SEO Engine    │
│   (HTML/JS)     │      │   (Flask)       │      │   (Python)      │
│                 │      │                 │      │                 │
│  • Enter URL    │      │  • /analyze     │      │  • Audit        │
│  • View scores  │      │  • /report/pdf  │      │  • Score        │
│  • Download PDF │      │  • /email       │      │  • Recommend    │
└─────────────────┘      └─────────────────┘      └─────────────────┘
```

## Business Features

### 1. White-Label Reports
Customize with your branding:

```javascript
// In dashboard, click Settings ⚙️
// Set your business name, logo, contact info
```

Or in API calls:
```
GET /api/report/pdf?url=example.com&business_name=Your%20Agency
```

### 2. Email Reports to Clients
```bash
curl -X POST http://localhost:5000/api/email \
  -H "Content-Type: application/json" \
  -d '{"url": "https://client.com", "email": "client@example.com"}'
```

### 3. Batch Analysis
```bash
curl -X POST http://localhost:5000/api/batch \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://site1.com", "https://site2.com"]}'
```

### 4. API Keys for Clients
```bash
# Create a key for a client
curl -X POST http://localhost:5000/api/keys \
  -H "Content-Type: application/json" \
  -d '{"name": "Client A", "email": "client@example.com"}'

# Returns: {"api_key": "seo_abc123..."}
```

Clients can then run their own analyses:
```bash
curl http://localhost:5000/api/analyze \
  -H "X-API-Key: seo_abc123..." \
  -H "Content-Type: application/json" \
  -d '{"url": "https://theirsit