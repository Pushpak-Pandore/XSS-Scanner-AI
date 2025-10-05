# 🔒 AI-Enhanced XSS Scanner Platform

An intelligent web security scanning platform that combines traditional XSS detection with advanced AI-powered vulnerability analysis and natural language query processing.

## ✨ Features

- **🎯 Comprehensive XSS Scanning**: Multi-layered scanning with custom payloads
- **🤖 AI-Powered Analysis**: GPT-4 & Claude integration for intelligent vulnerability assessment
- **💬 Natural Language Queries**: Ask questions about your security posture in plain English
- **📊 Real-time Dashboard**: Live statistics and vulnerability tracking
- **🔍 Smart Triage**: AI-assisted vulnerability prioritization
- **🎨 Modern UI**: Dark-themed, responsive interface built with React and Tailwind CSS

## 🏗️ Architecture

- **Frontend**: React 19 with Tailwind CSS and Radix UI components
- **Backend**: FastAPI with async/await support
- **Database**: MongoDB for data persistence
- **AI Integration**: Emergent LLM integration (GPT-4, Claude Sonnet)
- **Deployment**: Containerized with supervisor process management

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- MongoDB
- Yarn package manager

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd <project-directory>
```

### 2. Backend Setup

```bash
# Navigate to backend
cd backend/

# Install Python dependencies
pip install -r requirements.txt

# Create environment file
cat > .env << EOF
MONGO_URL=mongodb://localhost:27017
DB_NAME=xss_scanner
EMERGENT_LLM_KEY=sk-emergent-556F249747fEbDfFd2
CORS_ORIGINS=http://localhost:3000,https://essentials-only.preview.emergentagent.com
EOF
```

### 3. Frontend Setup

```bash
# Navigate to frontend
cd ../frontend/

# Install dependencies
yarn install

# Create environment file
cat > .env << EOF
REACT_APP_BACKEND_URL=https://essentials-only.preview.emergentagent.com
EOF
```

### 4. Database Setup

```bash
# Start MongoDB (if not running)
sudo systemctl start mongodb
# or
mongod --dbpath /path/to/your/data
```

### 5. Start Services

#### Using Supervisor (Recommended for Production)

```bash
# Start all services
sudo supervisorctl restart all

# Check status
sudo supervisorctl status

# View logs
sudo supervisorctl tail -f backend
sudo supervisorctl tail -f frontend
```

#### Manual Development Mode

```bash
# Terminal 1 - Backend
cd backend/
python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload

# Terminal 2 - Frontend
cd frontend/
yarn start

# Terminal 3 - MongoDB (if needed)
mongod
```

## 📁 Project Structure

```
/
├── backend/                    # FastAPI Backend
│   ├── .env                   # Environment variables
│   ├── server.py              # Main FastAPI application
│   └── requirements.txt       # Python dependencies
├── frontend/                   # React Frontend
│   ├── .env                   # Frontend environment variables
│   ├── src/
│   │   ├── App.js            # Main React component
│   │   ├── components/       # Reusable UI components
│   │   ├── hooks/           # Custom React hooks
│   │   └── lib/             # Utility functions
│   ├── public/              # Static assets
│   ├── package.json         # Node.js dependencies
│   └── tailwind.config.js   # Tailwind CSS configuration
└── README.md                # This file
```

## 🔌 API Endpoints

### Scan Management
- `POST /api/scans` - Create new XSS scan
- `GET /api/scans` - Get all scans
- `GET /api/scans/{id}/result` - Get scan results
- `GET /api/scans/{id}/vulnerabilities` - Get vulnerabilities

### AI Features
- `POST /api/ai/nlp-query` - Natural language security queries
- `POST /api/ai/triage` - AI-powered vulnerability triage

### Dashboard
- `GET /api/dashboard/stats` - Security statistics and metrics

## 🤖 AI Integration

The platform integrates with advanced AI models through the Emergent LLM service:

### Supported Models
- **GPT-4**: Advanced reasoning and vulnerability analysis
- **Claude Sonnet**: Alternative AI perspective for comprehensive analysis

### Features
- **Natural Language Queries**: "What vulnerabilities were found in recent scans?"
- **Intelligent Triage**: Automatic vulnerability prioritization
- **Executive Summaries**: AI-generated security reports
- **Remediation Suggestions**: Context-aware fix recommendations

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
MONGO_URL=mongodb://localhost:27017          # MongoDB connection string
DB_NAME=xss_scanner                          # Database name
EMERGENT_LLM_KEY=sk-emergent-***            # AI service API key
CORS_ORIGINS=http://localhost:3000           # Allowed CORS origins
```

#### Frontend (.env)
```env
REACT_APP_BACKEND_URL=http://localhost:8001  # Backend API URL
```

### Scan Types
- **Quick**: Basic XSS payload testing
- **Comprehensive**: Extended payload set with form analysis
- **Custom**: User-defined payloads and parameters

## 📊 Dashboard Features

### Security Overview
- Total scans performed
- Vulnerability count by severity
- Completed vs pending scans
- Critical issues summary

### Vulnerability Management
- Detailed vulnerability listings
- Severity-based filtering
- Export capabilities
- Historical trend analysis

### AI Assistant
- Natural language security queries
- Interactive vulnerability exploration
- Contextual help and guidance

## 🚀 Deployment

### Production Deployment

1. **Environment Setup**
   ```bash
   # Set production environment variables
   export MONGO_URL="mongodb://prod-server:27017"
   export DB_NAME="xss_scanner_prod"
   export EMERGENT_LLM_KEY="your-production-key"
   ```

2. **Build Frontend**
   ```bash
   cd frontend/
   yarn build
   ```

3. **Start Services**
   ```bash
   sudo supervisorctl restart all
   ```

### Docker Deployment (Optional)

```dockerfile
# Dockerfile example
FROM node:18 AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/yarn.lock ./
RUN yarn install
COPY frontend/ ./
RUN yarn build

FROM python:3.11
WORKDIR /app
COPY backend/requirements.txt ./
RUN pip install -r requirements.txt
COPY backend/ ./
COPY --from=frontend-build /app/frontend/build ./static
EXPOSE 8001
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001"]
```

## 🔍 Usage Examples

### Creating a Scan

```javascript
// Frontend example
const scanData = {
  target_url: "https://example.com",
  scan_type: "comprehensive",
  include_forms: true,
  include_urls: true,
  max_depth: 3,
  custom_payloads: ["<script>alert('test')</script>"]
};

const response = await fetch('/api/scans', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(scanData)
});
```

### AI Query Example

```javascript
// Ask AI about security status
const query = {
  query: "What are the most critical vulnerabilities in my recent scans?",
  session_id: "user-session-123"
};

const response = await fetch('/api/ai/nlp-query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(query)
});
```

## 🛠️ Development

### Adding New Features

1. **Backend**: Add new endpoints in `server.py`
2. **Frontend**: Create components in `src/components/`
3. **Database**: Define new schemas in the backend models
4. **AI**: Extend LLM integrations for new capabilities

### Running Tests

```bash
# Backend testing
cd backend/
python -m pytest

# Frontend testing
cd frontend/
yarn test
```

### Code Style

- **Backend**: Black formatter, flake8 linting
- **Frontend**: ESLint, Prettier formatting
- **Commits**: Conventional commits format

## 📚 Dependencies

### Backend Dependencies
- **FastAPI**: Modern async web framework
- **Motor**: Async MongoDB driver
- **Pydantic**: Data validation and serialization
- **Emergent Integrations**: AI model access
- **BeautifulSoup4**: Web scraping and parsing
- **aiohttp**: Async HTTP client

### Frontend Dependencies
- **React 19**: Latest React with concurrent features
- **Tailwind CSS**: Utility-first CSS framework
- **Radix UI**: Accessible component primitives
- **Axios**: HTTP client for API calls
- **Lucide React**: Modern icon library

## 🔒 Security Considerations

- All user inputs are validated and sanitized
- XSS payloads are safely contained during testing
- API endpoints include proper authentication (when implemented)
- Environment variables protect sensitive configuration
- CORS policies restrict unauthorized access

## 🐛 Troubleshooting

### Common Issues

1. **Services not starting**
   ```bash
   # Check logs
   sudo supervisorctl tail -f backend
   sudo supervisorctl tail -f frontend
   
   # Restart services
   sudo supervisorctl restart all
   ```

2. **Database connection issues**
   ```bash
   # Check MongoDB status
   sudo systemctl status mongodb
   
   # Verify connection string in .env
   ```

3. **Frontend not loading**
   ```bash
   # Check if backend is running
   curl http://localhost:8001/api/dashboard/stats
   
   # Verify environment variables
   cat frontend/.env
   ```

4. **AI features not working**
   - Verify EMERGENT_LLM_KEY is set correctly
   - Check backend logs for API errors
   - Ensure internet connectivity for AI services

## 📈 Performance Tips

- Use MongoDB indexes for large scan datasets
- Implement caching for frequently accessed data
- Consider pagination for large result sets
- Monitor AI API usage to manage costs
- Use connection pooling for database operations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the troubleshooting section above
- Review the API documentation
- Create an issue in the repository
- Contact the development team

---

**Made with ❤️ using Emergent AI Platform**
