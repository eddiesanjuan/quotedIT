# Quoted - Voice to Quote for Contractors

**Turn voice notes into professional budgetary quotes in seconds.**

Quoted helps contractors generate quick budgetary estimates from voice descriptions of jobs. Speak naturally about the work, and get a professional quote ready to send.

## Key Features

- **Voice-First Input**: Describe the job in your own words
- **AI-Powered Synthesis**: Claude converts natural language to structured quotes
- **Learned Pricing**: Gets smarter from every correction you make
- **Per-Contractor Isolation**: Your pricing model is yours alone
- **Professional PDFs**: Ready to send to customers

## Important: Budgetary Estimates Only

Quoted generates **budgetary estimates** for quick pricing guidance. These are NOT detailed takeoffs or binding contracts. Final pricing should be confirmed after site assessment.

## Quick Start

### 1. Install Dependencies

```bash
cd quoted
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your API keys
```

Required API keys:
- `ANTHROPIC_API_KEY` - For Claude AI synthesis
- `OPENAI_API_KEY` - For Whisper transcription (or use Deepgram)

### 3. Run the Server

```bash
python run.py
```

The API will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

### 4. Open the Frontend

Open `frontend/index.html` in your browser for a simple test interface.

## API Endpoints

### Quotes

- `POST /api/quotes/generate` - Generate quote from text
- `POST /api/quotes/generate-from-audio` - Generate quote from audio file
- `GET /api/quotes/{id}` - Get a quote
- `PUT /api/quotes/{id}` - Update/correct a quote (triggers learning)
- `POST /api/quotes/{id}/pdf` - Generate PDF

### Contractors

- `POST /api/contractors/` - Create contractor account
- `GET /api/contractors/{id}` - Get contractor info
- `GET /api/contractors/{id}/pricing` - Get pricing model
- `PUT /api/contractors/{id}/pricing` - Update pricing model
- `GET /api/contractors/{id}/terms` - Get terms
- `PUT /api/contractors/{id}/terms` - Update terms

### Onboarding

- `POST /api/onboarding/start` - Start setup interview
- `POST /api/onboarding/{session_id}/continue` - Continue interview
- `POST /api/onboarding/{session_id}/complete` - Extract pricing model
- `POST /api/onboarding/quick` - Quick setup (skip interview)

## Architecture

```
quoted/
├── backend/
│   ├── api/           # FastAPI routes
│   │   ├── quotes.py      # Quote generation endpoints
│   │   ├── contractors.py # Contractor management
│   │   └── onboarding.py  # Setup interview
│   ├── models/
│   │   └── database.py    # SQLAlchemy models
│   ├── prompts/       # Claude prompt templates
│   │   ├── quote_generation.py
│   │   └── setup_interview.py
│   ├── services/      # Core business logic
│   │   ├── transcription.py   # Whisper/Deepgram
│   │   ├── quote_generator.py # Quote synthesis
│   │   ├── pdf_generator.py   # PDF creation
│   │   ├── onboarding.py      # Setup flow
│   │   └── learning.py        # Correction loop
│   ├── config.py      # Settings
│   └── main.py        # FastAPI app
├── frontend/
│   └── index.html     # Simple test UI
├── tests/
│   └── test_quote_generation.py
├── requirements.txt
├── run.py
└── README.md
```

## How It Works

### 1. Voice Input
Contractor speaks: "16 by 20 composite deck, Trex Select. Demo the old deck. Standard railing, 45 feet. Customer is John at 123 Oak..."

### 2. Transcription
OpenAI Whisper converts audio to text.

### 3. AI Synthesis
Claude analyzes the transcription using the contractor's learned pricing model:
- Detects job type (composite deck)
- Calculates square footage (320 sqft)
- Applies per-sqft rate ($58/sqft baseline)
- Adds line items (demo, railing, etc.)
- Estimates timeline

### 4. Quote Generation
Returns structured JSON:
```json
{
  "job_type": "composite_deck",
  "job_description": "New 16x20 composite deck with demolition...",
  "line_items": [
    {"name": "Demolition", "amount": 1200},
    {"name": "Framing", "amount": 3800},
    {"name": "Decking - Trex Select", "amount": 5600},
    {"name": "Railing", "amount": 1710}
  ],
  "subtotal": 12310,
  "confidence": "high"
}
```

### 5. Learning Loop
When contractor edits a quote, the system learns:
- Adjusts baseline rates
- Learns special rules ("add 10% in this neighborhood")
- Improves confidence over time

## The Moat

After 50+ quotes, Quoted knows YOUR pricing deeply:
- Your specific rates and markups
- Your terminology and job patterns
- Your adjustment rules
- Your customer history

Switching means starting over. The learning is the lock-in.

## Development

### Run Tests

```bash
# Set API keys first
export ANTHROPIC_API_KEY=your-key
export OPENAI_API_KEY=your-key

# Run tests
python tests/test_quote_generation.py
```

### Project Status

This is an MVP/prototype. Production would need:
- [ ] Real database (PostgreSQL)
- [ ] User authentication
- [ ] Multi-tenant isolation verification
- [ ] Rate limiting
- [ ] Email/SMS delivery
- [ ] Mobile app
- [ ] Stripe integration

## License

Proprietary - All rights reserved.
