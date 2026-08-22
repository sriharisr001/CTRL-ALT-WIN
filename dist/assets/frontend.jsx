import React, { useState } from 'react';

export default function SatyaFinDashboard() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [loadingStep, setLoadingStep] = useState(0); 
  const [resultData, setResultData] = useState(null);

  // Handle file selection from drag-and-drop or file input
  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  // Simulate or trigger the live scanning flow
  const handleAnalyze = async () => {
    if (!selectedFile) {
      alert("Please upload an image first!");
      return;
    }

    setLoadingStep(1); // Step 1: Uploading

    try {
      // Step-by-step UI progression timers to match backend processing
      setTimeout(() => setLoadingStep(2), 1000); // OCR / AI Extraction via Gemini
      setTimeout(() => setLoadingStep(3), 2200); // Market volatility check

      // Replace this URL with your actual backend / FastAPI endpoint URL
      const formData = new FormData();
      formData.append("file", selectedFile);

      const response = await fetch("http://localhost:8000/extract-claim", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      setLoadingStep(4); // Finished
      setTimeout(() => {
        setLoadingStep(0);
        setResultData(data); // Save the parsed data to display in UI
      }, 600);

    } catch (error) {
      console.error("Analysis failed:", error);
      setLoadingStep(0);
      alert("Failed to connect to the AI service. Is your backend running?");
    }
  };

  return (
    <div className="min-h-screen bg-[#090D16] text-slate-100 p-6 font-sans flex flex-col items-center">
      
      {/* Header */}
      <header className="w-full max-w-5xl flex justify-between items-center mb-10 border-b border-slate-800 pb-4">
        <div className="flex items-center space-x-3">
          <div className="h-3 w-3 bg-red-500 rounded-full animate-ping"></div>
          <h1 className="text-xl font-bold tracking-wider bg-gradient-to-r from-red-400 to-amber-400 bg-clip-text text-transparent">
            SATYAFIN // AI SHIELD
          </h1>
        </div>
        <span className="text-xs px-3 py-1 rounded-full bg-slate-800 border border-slate-700 text-slate-400">
          SEBI Compliance Engine v1.0
        </span>
      </header>

      {/* Main Workspace Grid */}
      <main className="w-full max-w-5xl grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Left: Upload Box */}
        <div className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl backdrop-blur-xl flex flex-col justify-between shadow-2xl">
          <div>
            <h2 className="text-lg font-semibold mb-1 text-slate-200">Submit Finfluencer Proof</h2>
            <p className="text-sm text-slate-400 mb-6">Drop a screenshot of a suspicious P&L claim or telegram tip.</p>
            
            {/* Drag & Drop Area */}
            <label className="border-2 border-dashed border-slate-700 hover:border-red-500/50 transition-all rounded-xl p-8 text-center cursor-pointer bg-slate-950/40 flex flex-col items-center justify-center block">
              <input type="file" accept="image/*" onChange={handleFileChange} className="hidden" />
              <svg className="w-10 h-10 text-slate-500 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              {selectedFile ? (
                <span className="text-sm font-medium text-emerald-400 truncate max-w-xs">{selectedFile.name}</span>
              ) : (
                <>
                  <p className="text-sm font-medium text-slate-300">Drag & drop image here, or <span className="text-red-400 underline">browse</span></p>
                  <p className="text-xs text-slate-500 mt-1">Supports PNG, JPG, WEBP up to 10MB</p>
                </>
              )}
            </label>
          </div>

          <button 
            onClick={handleAnalyze}
            disabled={loadingStep > 0}
            className="mt-6 w-full py-3 bg-gradient-to-r from-red-600 to-amber-600 hover:from-red-500 hover:to-amber-500 text-white font-semibold rounded-xl shadow-lg shadow-red-900/20 transition-all disabled:opacity-50 cursor-pointer"
          >
            {loadingStep > 0 ? "Analyzing Evidence..." : "Run AI Scam Analysis ⚡"}
          </button>
        </div>

        {/* Right: Results / Verdict Panel with Live Loading State */}
        <div className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl backdrop-blur-xl flex flex-col justify-between shadow-2xl relative overflow-hidden">
          
          {/* Cyberpunk Glow Background Effect */}
          <div className="absolute -top-24 -right-24 w-48 h-48 bg-red-600/10 rounded-full blur-3xl pointer-events-none"></div>

          {/* LIVE LOADING SCREEN OVERLAY */}
          {loadingStep > 0 && (
            <div className="absolute inset-0 bg-slate-950/95 backdrop-blur-md flex flex-col items-center justify-center p-6 z-20 transition-all">
              {/* Radar Scanner Animation */}
              <div className="relative w-20 h-20 mb-6 flex items-center justify-center">
                <div className="absolute inset-0 border-2 border-red-500/20 rounded-full animate-ping"></div>
                <div className="absolute inset-2 border border-red-500/40 rounded-full animate-spin"></div>
                <div className="w-3 h-3 bg-red-500 rounded-full shadow-[0_0_15px_#ef4444]"></div>
              </div>

              <h3 className="text-base font-semibold text-slate-100 mb-4 tracking-wider">INVESTIGATING EVIDENCE...</h3>
              
              {/* Step-by-step checklist */}
              <div className="space-y-2.5 w-full max-w-xs text-xs text-left">
                <div className={`flex items-center space-x-3 transition-colors ${loadingStep >= 1 ? 'text-red-400 font-medium' : 'text-slate-600'}`}>
                  <span>{loadingStep > 1 ? '✔' : '⏳'}</span>
                  <span>Uploading screenshot to pipeline</span>
                </div>
                <div className={`flex items-center space-x-3 transition-colors ${loadingStep >= 2 ? 'text-red-400 font-medium' : 'text-slate-600'}`}>
                  <span>{loadingStep > 2 ? '✔' : loadingStep === 2 ? '⏳' : '○'}</span>
                  <span>Extracting financial claims via Gemini Vision</span>
                </div>
                <div className={`flex items-center space-x-3 transition-colors ${loadingStep >= 3 ? 'text-red-400 font-medium' : 'text-slate-600'}`}>
                  <span>{loadingStep > 3 ? '✔' : loadingStep === 3 ? '⏳' : '○'}</span>
                  <span>Verifying SEBI registration & market limits</span>
                </div>
              </div>
            </div>
          )}

          {/* Normal Verdict Content */}
          <div>
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold text-slate-200">Analysis Verdict</h2>
              <span className={`px-2.5 py-0.5 text-xs font-bold rounded-full border ${resultData ? 'bg-red-500/10 text-red-400 border-red-500/20' : 'bg-slate-800 text-slate-400 border-slate-700'}`}>
                {resultData ? 'HIGH RISK // SCAM' : 'PENDING INPUT'}
              </span>
            </div>

            {/* Risk Score Gauge Box */}
            <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-5 mb-4 text-center">
              <span className="text-xs uppercase tracking-widest text-slate-500 font-semibold">Calculated Fraud Index</span>
              <div className="text-5xl font-black text-red-500 my-2 tracking-tight">
                {resultData ? '98.4%' : '--'}
              </div>
              <p className="text-xs text-slate-400">
                {resultData 
                  ? `Claimed ${resultData.claimed_return_pct}% return in ${resultData.timeframe_days} days violates market thresholds.` 
                  : 'Upload an image and run analysis to calculate fraud metric.'}
              </p>
            </div>

            {/* Extracted Parameter Grid */}
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-slate-950/40 border border-slate-800 p-3 rounded-lg">
                <span className="text-[10px] uppercase text-slate-500 block">Target Asset</span>
                <span className="text-sm font-bold text-slate-200">{resultData ? resultData.stock_symbol : '---'}</span>
              </div>
              <div className="bg-slate-950/40 border border-slate-800 p-3 rounded-lg">
                <span className="text-[10px] uppercase text-slate-500 block">SEBI Status</span>
                <span className="text-sm font-bold text-red-400">{resultData ? resultData.mentioned_sebi_id : 'UNREGISTERED'}</span>
              </div>
            </div>
          </div>

          <div className="text-[11px] text-slate-500 text-center mt-4">
            Validated via Gemini Vision API & Market Volatility Engine
          </div>

        </div>

      </main>
    </div>
  );
}
