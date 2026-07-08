import React, { useState, useEffect } from 'react';
import './index.css';

const LOADING_STEPS = [
  "Initializing autonomous agent...",
  "Analyzing request parameters...",
  "Drafting project timeline...",
  "Consulting industry standards...",
  "Writing document content...",
  "Formatting final .docx artifact...",
  "Finalizing..."
];

// Sub-components
const ExecutionLog = ({ logs }) => (
  <div className="result-card">
    <h3>
      <svg width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
      Execution Log
    </h3>
    <ul className="log-list">
      {logs.map((log, idx) => (
        <li key={idx} className={`log-item status-${log.status}`}>
          <div className="log-header">
            <span>Step {log.step}</span>
            <span>{log.status.replace('_', ' ')}</span>
          </div>
          <div className="log-details">{log.details}</div>
        </li>
      ))}
    </ul>
  </div>
);

const PlanViewer = ({ plan, assumptions }) => (
  <div className="result-card">
    <h3>
      <svg width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
      Generated Plan
    </h3>
    <div className="plan-list">
      {plan.map((step, idx) => (
        <div key={idx} className="plan-item">
          <div className="plan-number">{step.step}</div>
          <div className="plan-content">
            <div className="plan-action">{step.action}</div>
            <span className={`tag tag-${step.tool}`}>{step.tool}</span>
          </div>
        </div>
      ))}
    </div>
    
    {assumptions && assumptions.length > 0 && (
      <div className="assumptions-box">
        <h4>Planner Assumptions</h4>
        <ul>
          {assumptions.map((ass, idx) => (
            <li key={idx}>{ass}</li>
          ))}
        </ul>
      </div>
    )}
  </div>
);

function App() {
  const [request, setRequest] = useState('');
  
  // App States: 'input' | 'loading' | 'success' | 'error'
  const [appState, setAppState] = useState('input');
  const [result, setResult] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');
  
  // Loading animation state
  const [loadingStepIndex, setLoadingStepIndex] = useState(0);
  const [showDetails, setShowDetails] = useState(false);

  useEffect(() => {
    let interval;
    if (appState === 'loading') {
      interval = setInterval(() => {
        setLoadingStepIndex(prev => {
          if (prev < LOADING_STEPS.length - 1) return prev + 1;
          return prev;
        });
      }, 2500); // cycle messages every 2.5 seconds
    } else {
      setLoadingStepIndex(0);
    }
    return () => clearInterval(interval);
  }, [appState]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!request.trim()) return;

    setAppState('loading');
    setErrorMsg('');
    setResult(null);
    setShowDetails(false);

    try {
      const response = await fetch('http://localhost:8000/agent', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ request }),
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.statusText}`);
      }

      const data = await response.json();
      setResult(data);
      setAppState('success');
    } catch (err) {
      setErrorMsg(err.message);
      setAppState('error');
    }
  };

  const handleReset = () => {
    setAppState('input');
    setRequest('');
    setResult(null);
    setErrorMsg('');
  };

  return (
    <div className="app-container">
      {/* 1. INPUT STATE */}
      {appState === 'input' && (
        <div className="state-view animate-fade-in">
          <header className="hero-section">
            <div className="hero-content">
              <h1 className="title">
                <span className="highlight-1">Draftline</span> <br />
                <span className="highlight-2">AI Engine</span>
              </h1>
              <p className="subtitle">
                Transform natural language ideas into comprehensive, fully formatted project plans and documents in seconds.
              </p>
            </div>
            <div className="hero-illustration">
              <img src="/illustration.png" alt="AI Agent structuring a project plan" />
            </div>
          </header>

          <main>
            <section className="input-section">
              <div className="input-card">
                <form onSubmit={handleSubmit}>
                  <div className="textarea-wrapper">
                    <textarea
                      value={request}
                      onChange={(e) => setRequest(e.target.value)}
                      placeholder="Describe what you want to build or plan (e.g. 'Create a project plan for launching a mobile banking app MVP in 3 months')..."
                    />
                  </div>
                  <button type="submit" className="submit-btn" disabled={!request.trim()}>
                    <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
                    Generate Document
                  </button>
                </form>
              </div>
            </section>
          </main>
        </div>
      )}

      {/* 2. LOADING STATE */}
      {appState === 'loading' && (
        <div className="state-view loading-view animate-fade-in">
          <div className="loading-animation-container">
            <div className="radar-spinner"></div>
            <h2 className="loading-title">Agent is working...</h2>
            <p className="loading-step animate-slide-up" key={loadingStepIndex}>
              {LOADING_STEPS[loadingStepIndex]}
            </p>
          </div>
        </div>
      )}

      {/* ERROR STATE */}
      {appState === 'error' && (
        <div className="state-view animate-fade-in" style={{ textAlign: 'center', marginTop: '10vh' }}>
           <h2 style={{ color: '#e74c3c', marginBottom: '1rem' }}>Something went wrong</h2>
           <p style={{ marginBottom: '2rem' }}>{errorMsg}</p>
           <button onClick={handleReset} className="submit-btn">Try Again</button>
        </div>
      )}

      {/* 3. SUCCESS STATE */}
      {appState === 'success' && result && (
        <div className="state-view success-view animate-fade-in">
          
          <div className="success-header">
            <div className="success-icon">
              <svg width="48" height="48" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
            </div>
            <h2>Document Ready!</h2>
            <p>Your document was successfully generated ({result.plan_source === 'llm' ? 'Live AI Planning' : 'Fallback Mode'}).</p>
          </div>

          <div className="massive-download-container">
            <a 
              href={`http://localhost:8000/${result.document_path}`} 
              className="massive-download-btn"
              download
              target="_blank"
              rel="noreferrer"
            >
              <svg width="28" height="28" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
              Download Document
            </a>
            <button className="text-btn" onClick={handleReset}>Generate Another</button>
          </div>

          <div className="details-toggle-container">
            <button 
              className="toggle-details-btn" 
              onClick={() => setShowDetails(!showDetails)}
            >
              {showDetails ? 'Hide Generation Details' : 'View Generation Details'}
              <svg 
                style={{ transform: showDetails ? 'rotate(180deg)' : 'rotate(0)' }} 
                width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
              >
                <polyline points="6 9 12 15 18 9"></polyline>
              </svg>
            </button>
          </div>

          {showDetails && (
            <section className="results-container animate-slide-up">
              <PlanViewer plan={result.plan} assumptions={result.assumptions} />
              <ExecutionLog logs={result.execution_log} />
            </section>
          )}

        </div>
      )}
    </div>
  );
}

export default App;
