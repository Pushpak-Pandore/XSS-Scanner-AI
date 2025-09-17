import React, { useState, useEffect } from 'react';
import './App.css';

const App = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [scans, setScans] = useState([]);
  const [vulnerabilities, setVulnerabilities] = useState([]);
  const [selectedScan, setSelectedScan] = useState(null);
  const [dashboardStats, setDashboardStats] = useState(null);
  const [scanForm, setScanForm] = useState({
    target_url: '',
    scan_type: 'comprehensive',
    include_forms: true,
    include_urls: true,
    max_depth: 3
  });
  const [nlpQuery, setNlpQuery] = useState('');
  const [nlpResponse, setNlpResponse] = useState(null);
  const [loading, setLoading] = useState(false);

  const API_BASE = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  useEffect(() => {
    fetchDashboardStats();
    fetchScans();
  }, []);

  const fetchDashboardStats = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/dashboard/stats`);
      const data = await response.json();
      setDashboardStats(data);
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
    }
  };

  const fetchScans = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/scans`);
      const data = await response.json();
      setScans(data);
    } catch (error) {
      console.error('Error fetching scans:', error);
    }
  };

  const fetchVulnerabilities = async (scanId) => {
    try {
      const response = await fetch(`${API_BASE}/api/scans/${scanId}/vulnerabilities`);
      const data = await response.json();
      setVulnerabilities(data);
    } catch (error) {
      console.error('Error fetching vulnerabilities:', error);
    }
  };

  const createScan = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/scans`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(scanForm),
      });
      
      if (response.ok) {
        const newScan = await response.json();
        setScans([newScan, ...scans]);
        setScanForm({
          target_url: '',
          scan_type: 'comprehensive',
          include_forms: true,
          include_urls: true,
          max_depth: 3
        });
        setActiveTab('scans');
        // Refresh dashboard stats
        setTimeout(fetchDashboardStats, 1000);
      }
    } catch (error) {
      console.error('Error creating scan:', error);
    }
    setLoading(false);
  };

  const handleNLPQuery = async (e) => {
    e.preventDefault();
    if (!nlpQuery.trim()) return;
    
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/ai/nlp-query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: nlpQuery }),
      });
      
      if (response.ok) {
        const data = await response.json();
        setNlpResponse(data);
      }
    } catch (error) {
      console.error('Error processing NLP query:', error);
    }
    setLoading(false);
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return 'text-red-400 bg-red-900/20';
      case 'high': return 'text-orange-400 bg-orange-900/20';
      case 'medium': return 'text-yellow-400 bg-yellow-900/20';
      case 'low': return 'text-blue-400 bg-blue-900/20';
      default: return 'text-gray-400 bg-gray-900/20';
    }
  };

  const getScanStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'text-green-400 bg-green-900/20';
      case 'running': return 'text-blue-400 bg-blue-900/20';
      case 'pending': return 'text-yellow-400 bg-yellow-900/20';
      case 'failed': return 'text-red-400 bg-red-900/20';
      default: return 'text-gray-400 bg-gray-900/20';
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-xl font-bold text-white flex items-center">
                  <span className="text-red-500 mr-2">🔐</span>
                  XSS Scanner AI
                </h1>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-300">AI-Powered Security Platform</span>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {['dashboard', 'new-scan', 'scans', 'ai-assistant'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`py-4 px-1 border-b-2 font-medium text-sm capitalize ${
                  activeTab === tab
                    ? 'border-red-500 text-red-400'
                    : 'border-transparent text-gray-400 hover:text-gray-200 hover:border-gray-300'
                }`}
              >
                {tab.replace('-', ' ')}
              </button>
            ))}
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Dashboard Tab */}
        {activeTab === 'dashboard' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-white">Security Dashboard</h2>
              <div className="flex items-center space-x-2">
                <span className="w-2 h-2 bg-green-400 rounded-full"></span>
                <span className="text-sm text-gray-300">AI Systems Online</span>
              </div>
            </div>

            {dashboardStats && (
              <>
                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 bg-blue-600 rounded-md flex items-center justify-center">
                          <span className="text-white text-sm font-medium">S</span>
                        </div>
                      </div>
                      <div className="ml-4">
                        <p className="text-sm font-medium text-gray-400">Total Scans</p>
                        <p className="text-2xl font-semibold text-white">{dashboardStats.total_scans}</p>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 bg-red-600 rounded-md flex items-center justify-center">
                          <span className="text-white text-sm font-medium">V</span>
                        </div>
                      </div>
                      <div className="ml-4">
                        <p className="text-sm font-medium text-gray-400">Vulnerabilities</p>
                        <p className="text-2xl font-semibold text-white">{dashboardStats.total_vulnerabilities}</p>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 bg-red-500 rounded-md flex items-center justify-center">
                          <span className="text-white text-sm font-medium">C</span>
                        </div>
                      </div>
                      <div className="ml-4">
                        <p className="text-sm font-medium text-gray-400">Critical Issues</p>
                        <p className="text-2xl font-semibold text-white">{dashboardStats.severity_distribution.critical}</p>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 bg-green-600 rounded-md flex items-center justify-center">
                          <span className="text-white text-sm font-medium">✓</span>
                        </div>
                      </div>
                      <div className="ml-4">
                        <p className="text-sm font-medium text-gray-400">Completed Scans</p>
                        <p className="text-2xl font-semibold text-white">{dashboardStats.completed_scans}</p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Severity Distribution Chart */}
                <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                  <h3 className="text-lg font-medium text-white mb-4">Vulnerability Severity Distribution</h3>
                  <div className="space-y-3">
                    {Object.entries(dashboardStats.severity_distribution).map(([severity, count]) => (
                      <div key={severity} className="flex items-center justify-between">
                        <div className="flex items-center">
                          <div className={`w-3 h-3 rounded-full mr-3 ${getSeverityColor(severity).split(' ')[1]}`}></div>
                          <span className="text-sm font-medium text-gray-300 capitalize">{severity}</span>
                        </div>
                        <div className="flex items-center">
                          <span className="text-sm text-white mr-3">{count}</span>
                          <div className="w-24 bg-gray-700 rounded-full h-2">
                            <div 
                              className={`h-2 rounded-full ${getSeverityColor(severity).split(' ')[1]}`}
                              style={{ width: `${Math.min(100, (count / Math.max(1, dashboardStats.total_vulnerabilities)) * 100)}%` }}
                            ></div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Recent Scans */}
                <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                  <h3 className="text-lg font-medium text-white mb-4">Recent Scan Activity</h3>
                  {dashboardStats.recent_scans.length > 0 ? (
                    <div className="space-y-3">
                      {dashboardStats.recent_scans.map((scan, index) => (
                        <div key={index} className="flex items-center justify-between py-2 border-b border-gray-700 last:border-b-0">
                          <div>
                            <p className="text-sm font-medium text-white">Scan #{scan.scan_id.slice(-8)}</p>
                            <p className="text-xs text-gray-400">
                              {scan.completed_at ? new Date(scan.completed_at).toLocaleString() : 'In progress'}
                            </p>
                          </div>
                          <div className="flex items-center space-x-2">
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getScanStatusColor(scan.status)}`}>
                              {scan.status}
                            </span>
                            <span className="text-sm text-gray-300">{scan.total_vulnerabilities} vulns</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-400">No recent scans available</p>
                  )}
                </div>
              </>
            )}
          </div>
        )}

        {/* New Scan Tab */}
        {activeTab === 'new-scan' && (
          <div className="max-w-2xl">
            <h2 className="text-2xl font-bold text-white mb-6">Create New XSS Scan</h2>
            
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <form onSubmit={createScan} className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Target URL
                  </label>
                  <input
                    type="url"
                    required
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
                    placeholder="https://example.com"
                    value={scanForm.target_url}
                    onChange={(e) => setScanForm({...scanForm, target_url: e.target.value})}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Scan Type
                  </label>
                  <select
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
                    value={scanForm.scan_type}
                    onChange={(e) => setScanForm({...scanForm, scan_type: e.target.value})}
                  >
                    <option value="quick">Quick Scan (Basic payloads)</option>
                    <option value="comprehensive">Comprehensive Scan (All payloads)</option>
                    <option value="custom">Custom Scan (User-defined)</option>
                  </select>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="include_forms"
                      className="w-4 h-4 text-red-600 bg-gray-700 border-gray-600 rounded focus:ring-red-500"
                      checked={scanForm.include_forms}
                      onChange={(e) => setScanForm({...scanForm, include_forms: e.target.checked})}
                    />
                    <label htmlFor="include_forms" className="ml-2 text-sm text-gray-300">
                      Scan Forms
                    </label>
                  </div>

                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="include_urls"
                      className="w-4 h-4 text-red-600 bg-gray-700 border-gray-600 rounded focus:ring-red-500"
                      checked={scanForm.include_urls}
                      onChange={(e) => setScanForm({...scanForm, include_urls: e.target.checked})}
                    />
                    <label htmlFor="include_urls" className="ml-2 text-sm text-gray-300">
                      Scan URL Parameters
                    </label>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Max Crawl Depth: {scanForm.max_depth}
                  </label>
                  <input
                    type="range"
                    min="1"
                    max="5"
                    className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
                    value={scanForm.max_depth}
                    onChange={(e) => setScanForm({...scanForm, max_depth: parseInt(e.target.value)})}
                  />
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50 disabled:cursor-not-allowed bg-gradient-to-r from-red-600 to-red-700"
                >
                  {loading ? 'Creating Scan...' : 'Start XSS Scan'}
                </button>
              </form>
            </div>

            {/* AI Security Notice */}
            <div className="mt-6 bg-blue-900/20 border border-blue-700 rounded-lg p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <span className="text-blue-400">🤖</span>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-blue-400">AI-Enhanced Scanning</h3>
                  <p className="text-sm text-blue-300 mt-1">
                    This scan will use GPT-4 and Claude Sonnet for vulnerability analysis, triage assistance, and remediation suggestions.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Scans Tab */}
        {activeTab === 'scans' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-white">Scan History</h2>
              <button
                onClick={fetchScans}
                className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-md text-sm font-medium text-white border border-gray-600"
              >
                Refresh
              </button>
            </div>

            <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-700">
                  <thead className="bg-gray-900">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                        Target
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                        Type
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                        Created
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-gray-800 divide-y divide-gray-700">
                    {scans.map((scan) => (
                      <tr key={scan.id} className="hover:bg-gray-700">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-white truncate max-w-xs">
                            {scan.target_url}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-900/20 text-blue-400">
                            {scan.scan_type}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                          {new Date(scan.created_at).toLocaleString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                          <button
                            onClick={() => {
                              setSelectedScan(scan);
                              fetchVulnerabilities(scan.id);
                            }}
                            className="text-red-400 hover:text-red-300 font-medium"
                          >
                            View Results
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {scans.length === 0 && (
                <div className="text-center py-12">
                  <p className="text-gray-400">No scans found. Create your first scan to get started.</p>
                </div>
              )}
            </div>

            {/* Scan Results Modal */}
            {selectedScan && (
              <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
                <div className="bg-gray-800 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
                  <div className="p-6 border-b border-gray-700">
                    <div className="flex items-center justify-between">
                      <h3 className="text-lg font-medium text-white">
                        Scan Results: {selectedScan.target_url}
                      </h3>
                      <button
                        onClick={() => setSelectedScan(null)}
                        className="text-gray-400 hover:text-white"
                      >
                        ✕
                      </button>
                    </div>
                  </div>

                  <div className="p-6 overflow-y-auto max-h-[70vh]">
                    {vulnerabilities.length > 0 ? (
                      <div className="space-y-4">
                        {vulnerabilities.map((vuln) => (
                          <div key={vuln.id} className="bg-gray-900 rounded-lg p-4 border border-gray-700">
                            <div className="flex items-start justify-between mb-3">
                              <div>
                                <h4 className="text-white font-medium">{vuln.vulnerability_type}</h4>
                                <p className="text-sm text-gray-400">{vuln.endpoint}</p>
                              </div>
                              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(vuln.severity)}`}>
                                {vuln.severity.toUpperCase()}
                              </span>
                            </div>

                            <div className="space-y-3">
                              <div>
                                <p className="text-sm font-medium text-gray-300">Parameter:</p>
                                <p className="text-sm text-gray-400 font-mono bg-gray-800 px-2 py-1 rounded">
                                  {vuln.parameter}
                                </p>
                              </div>

                              <div>
                                <p className="text-sm font-medium text-gray-300">Payload:</p>
                                <p className="text-sm text-gray-400 font-mono bg-gray-800 px-2 py-1 rounded break-all">
                                  {vuln.payload}
                                </p>
                              </div>

                              {vuln.ai_summary && (
                                <div>
                                  <p className="text-sm font-medium text-blue-400">🤖 AI Analysis:</p>
                                  <p className="text-sm text-gray-300 bg-blue-900/10 px-3 py-2 rounded border border-blue-800">
                                    {vuln.ai_summary}
                                  </p>
                                </div>
                              )}

                              {vuln.remediation_suggestion && (
                                <div>
                                  <p className="text-sm font-medium text-green-400">💡 Remediation:</p>
                                  <p className="text-sm text-gray-300 bg-green-900/10 px-3 py-2 rounded border border-green-800">
                                    {vuln.remediation_suggestion}
                                  </p>
                                </div>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-8">
                        <p className="text-gray-400">No vulnerabilities found in this scan.</p>
                        <p className="text-sm text-green-400 mt-2">✅ The target appears to be secure!</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* AI Assistant Tab */}
        {activeTab === 'ai-assistant' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-white">AI Security Assistant</h2>
              <div className="flex items-center space-x-2">
                <span className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></span>
                <span className="text-sm text-gray-300">GPT-4 & Claude Active</span>
              </div>
            </div>

            {/* NLP Query Interface */}
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <h3 className="text-lg font-medium text-white mb-4">Natural Language Security Queries</h3>
              
              <form onSubmit={handleNLPQuery} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Ask me anything about your security scans...
                  </label>
                  <div className="flex space-x-3">
                    <input
                      type="text"
                      className="flex-1 px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="e.g., Show me high severity XSS vulnerabilities from last week"
                      value={nlpQuery}
                      onChange={(e) => setNlpQuery(e.target.value)}
                    />
                    <button
                      type="submit"
                      disabled={loading}
                      className="px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded-md text-sm font-medium text-white focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                    >
                      {loading ? 'Processing...' : 'Query'}
                    </button>
                  </div>
                </div>
              </form>

              {/* Sample Queries */}
              <div className="mt-4">
                <p className="text-sm text-gray-400 mb-2">Try these sample queries:</p>
                <div className="flex flex-wrap gap-2">
                  {[
                    "What are the most critical vulnerabilities?",
                    "Show me XSS trends over time",
                    "Which endpoints are most vulnerable?",
                    "How many scans completed today?"
                  ].map((query, index) => (
                    <button
                      key={index}
                      onClick={() => setNlpQuery(query)}
                      className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded-md text-xs text-gray-300 border border-gray-600"
                    >
                      {query}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* NLP Response */}
            {nlpResponse && (
              <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                <h3 className="text-lg font-medium text-white mb-4">AI Response</h3>
                <div className="space-y-4">
                  <div className="bg-blue-900/20 border border-blue-700 rounded-lg p-4">
                    <p className="text-sm font-medium text-blue-400 mb-2">Query:</p>
                    <p className="text-sm text-blue-300">{nlpResponse.query}</p>
                  </div>
                  
                  <div className="bg-gray-900 rounded-lg p-4 border border-gray-600">
                    <p className="text-sm font-medium text-green-400 mb-2">🤖 AI Analysis:</p>
                    <p className="text-sm text-gray-300 whitespace-pre-wrap">{nlpResponse.response}</p>
                  </div>

                  {nlpResponse.context_summary && (
                    <div className="bg-gray-900 rounded-lg p-4 border border-gray-600">
                      <p className="text-sm font-medium text-gray-400 mb-2">Data Context:</p>
                      <pre className="text-xs text-gray-400 overflow-x-auto">
                        {JSON.stringify(nlpResponse.context_summary, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* AI Features Info */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                <h3 className="text-lg font-medium text-white mb-3">🎯 AI Triage Assistant</h3>
                <p className="text-sm text-gray-300 mb-3">
                  Automatically prioritizes vulnerabilities using GPT-4 analysis, considering business impact and exploitability.
                </p>
                <div className="space-y-2 text-xs text-gray-400">
                  <p>• Severity classification with context</p>
                  <p>• Business risk assessment</p>
                  <p>• Remediation priority ranking</p>
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                <h3 className="text-lg font-medium text-white mb-3">💡 Smart Remediation</h3>
                <p className="text-sm text-gray-300 mb-3">
                  Claude Sonnet generates specific, actionable remediation guidance with code examples and security best practices.
                </p>
                <div className="space-y-2 text-xs text-gray-400">
                  <p>• Custom code snippets</p>
                  <p>• Framework-specific fixes</p>
                  <p>• CSP and validation guidance</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default App;