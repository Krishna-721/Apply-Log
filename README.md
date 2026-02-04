# 🎯 Apply-Log - Job Application Tracker

A smart job application tracking system that automatically syncs with your Gmail to monitor job application lifecycle events (Applied, Interview, Offer, Rejected).

## 🌟 Features

- **Gmail Integration**: OAuth2 authentication to access job-related emails
- **Automatic Classification**: Intelligent email parsing to detect application status
- **Application Timeline**: Track the complete journey of each job application
- **Supabase Backend**: Scalable database for storing applications and events
- **RESTful API**: FastAPI-powered backend with clean endpoints

## 🏗️ Architecture

### Backend Stack
- **Framework**: FastAPI (Python)
- **Database**: Supabase (PostgreSQL)
- **Authentication**: Gmail OAuth2
- **Email Processing**: Gmail API

### Key Components

```
backend/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Environment configuration
│   ├── db.py                # Supabase client
│   ├── routes/
│   │   ├── gmail_auth.py    # Gmail OAuth flow
│   │   ├── gmail_sync.py    # Email sync logic
│   │   ├── applications.py  # Application CRUD
│   │   └── health.py        # Health check endpoints
│   └── gmail/
│       ├── service.py       # Gmail service wrapper
│       ├── job_filter.py    # Email classification logic
│       ├── body_parser.py   # Email body extraction
│       └── status_rank.py   # Status priority ranking
└── requirements.txt
```

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Supabase account
- Google Cloud Console project with Gmail API enabled

### 1. Clone the Repository
```bash
git clone https://github.com/Krishna-721/Apply-Log.git
cd Apply-Log
```

### 2. Set Up Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the `backend/` directory:

```env
# Supabase Configuration
SUPABASE_URL=your_supabase_url
SERVICE_ROLE_KEY=your_supabase_service_role_key

# Gmail OAuth
GMAIL_CLIENT_ID=your_gmail_client_id
GMAIL_CLIENT_SECRET=your_gmail_client_secret

# Cron Secret (for scheduled syncs)
CRON_SECRET=your_random_secret
```

### 4. Set Up Supabase Database

Create the following tables in your Supabase project:

#### `applications` table
```sql
CREATE TABLE applications (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id TEXT NOT NULL,
  company TEXT,
  role TEXT,
  current_status TEXT,
  last_event_at BIGINT,
  source TEXT DEFAULT 'gmail',
  gmail_thread_id TEXT UNIQUE,
  created_at TIMESTAMP DEFAULT NOW()
);
```

#### `application_events` table
```sql
CREATE TABLE application_events (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  application_id UUID REFERENCES applications(id),
  gmail_message_id TEXT UNIQUE,
  gmail_thread_id TEXT,
  event_type TEXT,
  subject TEXT,
  sender TEXT,
  occurred_at BIGINT,
  source TEXT DEFAULT 'gmail',
  created_at TIMESTAMP DEFAULT NOW()
);
```

#### `sync_state` table
```sql
CREATE TABLE sync_state (
  user_id TEXT PRIMARY KEY,
  last_internal_date BIGINT DEFAULT 0,
  updated_at TIMESTAMP DEFAULT NOW()
);
```

#### `gmail_tokens` table
```sql
CREATE TABLE gmail_tokens (
  user_id TEXT PRIMARY KEY,
  token TEXT,
  refresh_token TEXT,
  token_uri TEXT,
  client_id TEXT,
  client_secret TEXT,
  scopes TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### 5. Set Up Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable **Gmail API**
4. Create OAuth 2.0 credentials (Web application)
5. Add authorized redirect URI: `http://127.0.0.1:8000/auth/gmail/callback`
6. Copy Client ID and Client Secret to `.env`

### 6. Run the Backend
```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://127.0.0.1:8000`

## 📡 API Endpoints

### Authentication
- `GET /auth/gmail/login?user_id={user_id}` - Initiate Gmail OAuth
- `GET /auth/gmail/callback` - OAuth callback handler

### Sync
- `POST /gmail/sync?user_id={user_id}` - Sync emails for a user

### Applications
- `GET /applications/?user_id={user_id}` - List all applications
- `GET /applications/{id}?user_id={user_id}` - Get specific application
- `GET /applications/{id}/timeline?user_id={user_id}` - Get application timeline

### Testing
- `GET /gmail/test` - Test email classification
- `GET /` - Health check

## 🔄 How It Works

1. **User authenticates** with Gmail via OAuth2
2. **Backend syncs emails** from Gmail using the Gmail API
3. **Emails are classified** using keyword-based rules:
   - **Applied**: "thank you for applying", "application received"
   - **Interview**: "interview invitation", "coding test"
   - **Offer**: "congratulations", "offer letter"
   - **Rejected**: "unfortunately", "not moving forward"
4. **Applications are created/updated** based on Gmail thread
5. **Events are logged** in timeline for each application

## 🛡️ Current Status Classification

The system uses simple keyword matching in `job_filter.py`:
- Checks email subject and body
- Filters spam emails (job alerts, recommendations)
- Whitelists known ATS domains (Lever, Greenhouse, Workday, Ashby)

## 📝 Known Limitations

- No frontend UI yet
- Basic keyword-based classification (not ML-powered)
- Manual user_id management
- No automated scheduled syncs (cron endpoint exists but commented out)
- Limited to Gmail only

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a PR.

## 📄 License

MIT License
