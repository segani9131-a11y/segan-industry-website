# Segan Industry Website - Hybrid Architecture

A professional website for Segan Industry Private Limited, a wiring harness manufacturing and automation company based in Chennai, Tamil Nadu, India.

## Project Structure
```
segan-industry/
├── frontend/                 # Static website
│   ├── index.html           # Home page
│   ├── products.html        # Product catalog
│   ├── automation.html      # Automation services
│   ├── about.html           # Company profile
│   ├── contact.html         # Contact form
│   ├── quote.html           # Quote generator
│   ├── style.css            # Main stylesheet
│   ├── app.js               # Main JavaScript
│   └── assets/
│       ├── logo.png         # SI metallic logo
│       └── images/          # Additional images
│
├── backend/                  # Dynamic API + AI agent
│   ├── main.py              # FastAPI backend
│   ├── agent.py             # Wiring harness AI agent logic
│   ├── models.py            # Pydantic models
│   ├── requirements.txt     # Python dependencies
│   └── config.json          # Configuration
│
└── README.md
```

## Features

### Frontend
- Modern, responsive design with dark industrial theme
- SI metallic logo branding
- Colors: Silver, Electric Blue, Yellow Spark
- Fonts: Montserrat / Poppins
- Pages: Home, Products, Automation, About, Contact, Quote Generator

### Backend (FastAPI)
- `/api/quote` - AI-powered wiring harness quotations
- `/api/products` - Product catalog API
- `/api/contact` - Contact form submission
- `/api/automation` - Automation services
- `/api/agent` - Direct AI agent interaction

### AI Agent Capabilities
- Raw material price comparison
- Supplier selection logic
- Profit & loss calculation
- GST calculation (Tamil Nadu, India)
- Employee welfare logic
- Production workflow automation
- Machinery recommendation
- Inventory tracking
- Customer quotation generation

## Deployment

### Frontend (Free Hosting)
- Cloudflare Pages
- Netlify
- GitHub Pages

### Backend (Free Hosting)
- Render
- Railway
- Cloudflare Workers

## Getting Started

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
Open `frontend/index.html` in a browser or serve with any static file server.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/quote` | POST | Generate wiring harness quotation |
| `/api/products` | GET | Get product catalog |
| `/api/contact` | POST | Submit contact inquiry |
| `/api/automation` | GET | Get automation services |
| `/api/agent` | POST | Chat with AI agent |

## Configuration
Edit `backend/config.json` for:
- Company details
- GST rates (Tamil Nadu)
- Supplier information
- Email settings
- Database connections

## License
Proprietary - Segan Industry Private Limited