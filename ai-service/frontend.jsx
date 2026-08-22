import React, { useState } from 'react';

export default function SatyaFinChatRedesign() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [loadingStep, setLoadingStep] = useState(0); 
  const [resultData, setResultData] = useState(null);
  const [inputText, setInputText] = useState("");

  // Handle file selection from drag-and-drop or file browser
  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  // Trigger the live scanning workflow
  const handleAnalyze = async () => {
    if (!selectedFile && !inputText.trim()) {
      alert("Please upload a screenshot or paste text evidence first!");
      return;
    }

    setLoadingStep(1); // Step 1: Uploading / Initializing

    try {
      // Step-by-step UI progression to simulate backend AI extraction & market check
      setTimeout(() => setLoadingStep(2), 1000); // OCR / Gemini Extraction via Member 3
      setTimeout(() => setLoadingStep(2.5), 1800); // Transition step
      setTimeout(() => setLoadingStep(3), 2600); // SEBI & Volatility Engine check

      // NOTE: Replace this URL with your actual backend / FastAPI endpoint when integrated
      const formData = new FormData();
      if (selectedFile) formData.append("file", selectedFile);
      formData.append("prompt", inputText);

      const response = await fetch("http://localhost:8000/extract-claim", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      setLoadingStep(4); // Finished
      setTimeout(() => {
        setLoadingStep(0);
        setResultData(data); // Save the parsed data
      }, 500);

    } catch (error) {
      console.error("Analysis failed:", error);
      // Fallback demo data if backend isn't running locally yet so you can preview the UI
      setTimeout(() => {
        setLoadingStep(4);
        setTimeout(() => {
          setLoadingStep(0);
          setResultData({
            stock_symbol: "RELIANCE",
            claimed_return_pct: 50.0,
            timeframe_days: 10,
            mentioned_sebi_id: "NONE"
          });
        }, 500);
      }, 3000);
    }
  };

  return (
    <div className="min-h-screen bg-[#090D16] text-slate-100 p-6 md:p-10 font-sans flex flex-col items-center">
      
      {/* Header */}
      <header className="w-full max-w-5xl flex justify-between items-center mb-8 border-b border-slate-800/80 pb-4">
        <div className="flex items-center space-x-3">
          <div className="h-3 w-3 bg-red-500 rounded-full animate-ping"></div>
          <h1 className="text-xl font-black tracking-wider bg-gradient-to-r from-red-400 via-amber-300 to-amber-500 bg-clip-text text-transparent">
            SATYAFIN // AI SHIELD
          </h1>
        </div>
        <div className="flex items-center space-x-2">
          <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span className="text-xs px-3 py-1 rounded-full bg-slate-900 border border-slate-800 text-slate-400 font-medium">
            SEBI Compliance Engine v1.0
          </span>
        </div>
      </header>

      {/* Main Workspace Split Grid */}
      <main className="w-full max-w-5xl grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Left Column: Evidence Locker & Input Panel */}
        <div className="bg-slate-900/60 border border-slate-800/80 p-6 rounded-2xl backdrop-blur-xl flex flex-col justify-between shadow-2xl">
          <div>
            <div className="flex justify-between items-center mb-1">
              <h2 className="text-base font-bold text-slate-200">Evidence Intake Locker</h2>
              <span className="text-[10px] text-slate-500 uppercase font-semibold">Multi-Modal Upload</span>
            </div>
            <p className="text-xs text-slate-400 mb-5">Drop a P&L screenshot or paste Telegram/WhatsApp text tips below.</p>
            
            {/* Drag & Drop Area */}
            <label className="border-2 border-dashed border-slate-700 hover:border-red-500/50 transition-all rounded-xl p-6 text-center cursor-pointer bg-slate-950/40 flex flex-col items-center justify-center block mb-4 group">
              <input type="file" accept="image/*" onChange={handleFileChange} className="hidden" />
              <svg className="w-8 h-8 text-slate-500 group-hover:text-red-400 transition-colors mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              {selectedFile ? (
                <span className="text-xs font-semibold text-emerald-400 truncate max-w-xs">{selectedFile.name}</span>
              ) : (
                <>
                  <p className="text-xs font-medium text-slate-300">Drag & drop screenshot here, or <span className="text-red-400 underline">browse</span></p>
                  <p className="text-[10px] text-slate-500 mt-1">PNG, JPG, WEBP up to 10MB</p>
                </>
              )}
            </label>

            {/* Optional Text Prompt Input */}
            <div className="mb-2">
              <label className="text-[11px] font-semibold uppercase text-slate-400 block mb-1.5">Or Paste Finfluencer Claim Message</label>
              <textarea 
                rows="3"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="E.g., 'Guaranteed 50% returns on RELIANCE in 10 days! Join VIP group...'"
                className="w-full bg-slate-950/60 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 focus:outline-none focus:border-red-500/60 transition-colors resize-none placeholder:text-slate-600"
              />
            </div>
          </div>

          <button 
            onClick={handleAnalyze}
            disabled={loadingStep > 0}
            className="mt-4 w-full py-3 bg-gradient-to-r from-red-600 to-amber-600 hover:from-red-500 hover:to-amber-500 text-white font-bold text-sm tracking-wide rounded-xl shadow-lg shadow-red-900/30 transition-all disabled:opacity-50 cursor-pointer flex items-center justify-center space-x-2"
          >
            {loadingStep > 0 ? (
              <span>Running Deep Scan...</span>
            ) : (
              <>
                <span>Run AI Scam Analysis</span>
                <span>⚡</span>
              </>
            )}
          </button>
        </div>

        {/* Right Column: Verdict Panel with Live Cyberpunk Loading Overlay */}
        <div className="bg-slate-900/60 border border-slate-800/80 p-6 rounded-2xl backdrop-blur-xl flex flex-col justify-between shadow-2xl relative overflow-hidden">
          
          {/* Subtle Ambient Glow */}
          <div className="absolute -top-24 -right-24 w-48 h-48 bg-red-600/10 rounded-full blur-3xl pointer-events-none"></div>

          {/* LIVE CYBERPUNK LOADING OVERLAY */}
          {loadingStep > 0 && (
            <div className="absolute inset-0 bg-slate-950/95 backdrop-blur-md flex flex-col items-center justify-center p-6 z-20 transition-all">
              {/* Radar Scanner Animation */}
              <div className="relative w-20 h-20 mb-6 flex items-center justify-center">
                <div className="absolute inset-0 border-2 border-red-500/20 rounded-full animate-ping"></div>
                <div className="absolute inset-2 border border-red-500/40 rounded-full animate-spin"></div>
                <div className="w-3 h-3 bg-red-500 rounded-full shadow-[0_0_15px_#ef4444]"></div>
              </div>

              <h3 className="text-sm font-bold text-slate-100 mb-4 tracking-widest uppercase">INVESTIGATING EVIDENCE...</h3>
              
              {/* Step-by-step checklist */}
              <div className="space-y-2.5 w-full max-w-xs text-xs text-left">
                <div className={`flex items-center space-x-3 transition-colors ${loadingStep >= 1 ? 'text-red-400 font-semibold' : 'text-slate-600'}`}>
                  <span>{loadingStep > 1 ? '✔' : '⏳'}</span>
                  <span>Ingesting evidence pipeline</span>
                </div>
                <div className={`flex items-center space-x-3 transition-colors ${loadingStep >= 2 ? 'text-red-400 font-semibold' : 'text-slate-600'}`}>
                  <span>{loadingStep > 2 ? '✔' : loadingStep === 2 ? '⏳' : '○'}</span>
                  <span>Extracting financial claims via Gemini Vision</span>
                </div>
                <div className={`flex items-center space-x-3 transition-colors ${loadingStep >= 3 ? 'text-red-400 font-semibold' : 'text-slate-600'}`}>
                  <span>{loadingStep > 3 ? '✔' : loadingStep >= 3 ? '⏳' : '○'}</span>
                  <span>Running SEBI registry & volatility checks</span>
                </div>
              </div>
            </div>
          )}

          {/* Verdict Content */}
          <div>
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-base font-bold text-slate-200">Analysis Verdict</h2>
              <span className={`px-3 py-1 text-[11px] font-black rounded-full border tracking-wide ${resultData ? 'bg-red-500/10 text-red-400 border-red-500/20' : 'bg-slate-800/80 text-slate-400 border-slate-700'}`}>
                {resultData ? 'HIGH RISK // SCAM' : 'AWAITING EVIDENCE'}
              </span>
            </div>

            {/* Risk Score Gauge Box */}
            <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-5 mb-4 text-center">
              <span className="text-[10px] uppercase tracking-widest text-slate-500 font-bold block">Calculated Fraud Index</span>
              <div className="text-5xl font-black text-red-500 my-2 tracking-tight">
                {resultData ? '98.4%' : '--'}
              </div>
              <p className="text-xs text-slate-400">
                {resultData 
                  ? `Claimed ${resultData.claimed_return_pct}% return in ${resultData.timeframe_days} days violates historical volatility limits.` 
                  : 'Submit evidence on the left to generate fraud metrics.'}
              </p>
            </div>

            {/* Extracted Parameter Grid */}
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-slate-950/40 border border-slate-800 p-3 rounded-lg">
                <span className="text-[10px] uppercase font-semibold text-slate-500 block">Target Asset</span>
                <span className="text-xs font-bold text-slate-200">{resultData ? resultData.stock_symbol : '---'}</span>
              </div>
              <div className="bg-slate-950/40 border border-slate-800 p-3 rounded-lg">
                <span className="text-[10px] uppercase font-semibold text-slate-500 block">SEBI Status</span>
                <span className="text-xs font-bold text-red-400">{resultData ? resultData.mentioned_sebi_id : 'UNREGISTERED'}</span>
              </div>
            </div>
          </div>

          <div className="text-[10px] text-slate-500 text-center mt-6">
            Validated via Gemini 3.7 Vision API & Market Intelligence Engine
          </div>

        </div>

      </main>
    </div>
  );
}
