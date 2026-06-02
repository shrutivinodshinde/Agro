import React, { useState } from 'react';
import { Bell, AlertTriangle , UserCircle } from 'lucide-react';
import { ScanResult } from '../App.tsx';

interface ResultProps {
  result: ScanResult | null;
  onBack: () => void;
}

// "Apple_BlackRot" → "Black Rot"
function cleanLabel(raw: string): string {
  const parts = raw.split('_');
  const label = parts.length > 1 ? parts.slice(1).join(' ') : raw;
  return label
    .replace(/([a-z])([A-Z])/g, '$1 $2')
    .replace(/_/g, ' ')
    .trim();
}

interface Step {
  title: string;
  detail: string;
}

// Parses numbered agent_report into {title, detail} steps — same logic as result.html
function parseSteps(report: string | null): Step[] {
  if (!report) return [];
  const lines = report.split('\n');
  const steps: Step[] = [];
  let current: Step | null = null;
  lines.forEach((line) => {
    const trimmed = line.trim();
    const match = trimmed.match(/^(?:\*{0,2})?(\d+)[.):\s]\*{0,2}\s*(.+)/);
    if (match) {
      if (current) steps.push(current);
      current = { title: match[2].replace(/\*{1,2}/g, '').trim(), detail: '' };
    } else if (current && trimmed.length > 0 && !trimmed.startsWith('#')) {
      current.detail += (current.detail ? ' ' : '') + trimmed.replace(/\*{1,2}/g, '');
    }
  });
  if (current) steps.push(current);
  return steps;
}

export default function Result({ result, onBack }: ResultProps) {
  const [showTreatment, setShowTreatment]   = useState(false);
  const [showFullReport, setShowFullReport] = useState(false);

  if (!result) {
    return (
      <div
        className="flex flex-col items-center justify-center h-screen px-5"
        style={{ background: 'linear-gradient(135deg,#0B2017 0%,#1B4332 100%)' }}
      >
        <AlertTriangle size={48} className="text-red-300 mb-4 opacity-60" />
        <p className="text-white text-center font-bold mb-6">No scan result found.</p>
        <button
          onClick={onBack}
          className="bg-secondary text-white font-bold py-3 px-6 rounded-xl"
        >
          Go Back
        </button>
      </div>
    );
  }

  const diseaseName = cleanLabel(result.disease);
  const confPct     = Math.round(result.confidence * 100);
  const steps       = parseSteps(result.agent_report);

  const fallbackSteps: Step[] = result.is_healthy
    ? [
        { title: 'Continue regular watering',   detail: 'Water when top inch of soil is dry.' },
        { title: 'Ensure adequate sunlight',     detail: 'Maintain proper light for healthy crop growth.' },
        { title: 'Fertilise monthly',            detail: 'During growing season for best yield results.' },
        { title: 'Inspect regularly',            detail: 'Check for early pest signs to prevent spread.' },
      ]
    : [
        { title: 'Remove infected material',     detail: 'Remove all visibly infected leaves immediately.' },
        { title: 'Apply fungicide/bactericide',  detail: 'Apply neem oil or copper-based spray every 7–10 days.' },
        { title: 'Improve air circulation',      detail: 'Space plants adequately; avoid dense canopy.' },
        { title: 'Avoid overhead watering',      detail: 'Water at base in morning to reduce leaf moisture.' },
        { title: 'Monitor closely',              detail: 'Reassess after two weeks and repeat if needed.' },
      ];

  const displaySteps = steps.length > 0 ? steps : fallbackSteps;

  return (
    <div className="min-h-screen text-on-surface font-sans pb-32 relative">

      {/* ── Animated Botanical Background ── */}
      <div
        className="fixed inset-0 z-0 overflow-hidden"
        style={{ background: 'linear-gradient(135deg,#0B2017 0%,#1B4332 100%)' }}
      >
        {/* Organic glowing blobs */}
        <div
          className="absolute w-[500px] h-[500px] -top-40 -left-40 rounded-full"
          style={{
            background: 'radial-gradient(circle,rgba(160,244,200,0.08) 0%,rgba(160,244,200,0) 70%)',
            filter: 'blur(60px)',
            animation: 'pulse-shape 18s infinite alternate ease-in-out',
          }}
        />
        <div
          className="absolute w-[400px] h-[400px] bottom-10 right-0 rounded-full"
          style={{
            background: 'radial-gradient(circle,rgba(160,244,200,0.08) 0%,rgba(160,244,200,0) 70%)',
            filter: 'blur(60px)',
            animation: 'pulse-shape 18s infinite alternate ease-in-out',
            animationDelay: '-7s',
          }}
        />
        {/* Floating Material Symbols */}
        <span
          className="material-symbols-outlined absolute top-[15%] left-[10%] text-8xl select-none"
          style={{ color: 'rgba(160,244,200,0.04)', animation: 'float-around 35s infinite linear' }}
        >eco</span>
        <span
          className="material-symbols-outlined absolute top-[70%] left-[5%] text-9xl select-none"
          style={{ color: 'rgba(160,244,200,0.04)', animation: 'float-around 40s infinite linear', animationDelay: '-10s' }}
        >potted_plant</span>
        <span
          className="material-symbols-outlined absolute top-[25%] right-[15%] text-7xl select-none"
          style={{ color: 'rgba(160,244,200,0.04)', animation: 'float-around 30s infinite linear', animationDelay: '-5s' }}
        >forest</span>
      </div>

      {/* ── Header ── */}
      <header className="fixed top-0 left-0 w-full z-50 flex justify-between items-center px-5 h-16 bg-surface/90 backdrop-blur-md shadow-md border-b border-outline-variant/20">
        <div className="flex items-center gap-2">
          <img
            src="https://img.icons8.com/material-rounded/32/012d1d/wheat.png"
            alt="logo"
            className="w-6 h-6"
          />
          <img src="/logo.png" alt="logo" className="w-6 h-6 rounded-md" />
          <span className="text-2xl font-bold tracking-tight text-primary">AgroAI</span>
        </div>
        <div className="flex items-center gap-4">
          <button className="p-2 hover:bg-surface-container-low transition-colors rounded-full text-primary">
            <Bell className="w-6 h-6" />
          </button>
          <div className="w-8 h-8 rounded-full overflow-hidden bg-surface-container-high">
            <img src="/logo.png" alt="AgroAI" className="w-full h-full object-cover" />
          </div> 
        </div>
      </header>

      {/* ── Main ── */}
      <main className="pt-24 px-5 max-w-2xl mx-auto relative z-10">

        {/* Page title */}
        <section className="mb-6">
          <h1 className="text-4xl font-bold text-white mb-1 drop-shadow-md">Scan Results</h1>
          <p className="text-white/80 drop-shadow-sm">Diagnostic analysis complete.</p>
        </section>

        {/* ── Result Card ── */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-4 mb-10">

          {/* Scanned Image */}
          <div className="md:col-span-5 relative">
            <div
              className="aspect-square rounded-xl overflow-hidden border-4 border-white/20 backdrop-blur-sm bg-white/10 relative"
              style={{ boxShadow: '0 8px 32px rgba(27,67,50,0.12)' }}
            >
              <img
                src={result.imagePreview}
                alt={result.plant}
                className="w-full h-full object-cover"
              />
              {/* Analyzed / Healthy badge */}
              <div className="absolute top-3 right-3 bg-surface-container-lowest/90 backdrop-blur-md px-3 py-1 rounded-full shadow-sm">
                <span
                  className="text-xs font-bold uppercase tracking-widest"
                  style={{ color: result.is_healthy ? '#0e6c4a' : undefined }}
                >
                  {result.is_healthy ? 'HEALTHY' : 'ANALYZED'}
                </span>
              </div>
            </div>
          </div>

          {/* Stats Card */}
          <div className="md:col-span-7 flex flex-col justify-center">
            <div className="bg-white/95 backdrop-blur-md p-6 rounded-xl border border-white/30 shadow-xl">

              {/* Crop / Plant */}
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-bold text-outline uppercase tracking-widest">Crop / Plant</span>
                <span className="text-2xl font-bold text-primary">{result.plant}</span>
              </div>

              {/* Disease */}
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-bold text-outline uppercase tracking-widest">Disease</span>
                <span
                  className={`px-3 py-1 text-xs font-bold rounded-full uppercase tracking-wider ${
                    result.is_healthy
                      ? 'bg-secondary-container text-on-secondary-container'
                      : 'bg-error-container text-on-error-container'
                  }`}
                >
                  {result.is_healthy ? 'Healthy' : diseaseName}
                </span>
              </div>

              <hr className="border-outline-variant/30 my-3" />

              {/* Confidence + Severity */}
              <div className="grid grid-cols-2 gap-4 pt-1">
                <div>
                  <span className="block text-xs font-bold text-outline mb-1 uppercase tracking-widest">Confidence</span>
                  <span className="text-2xl font-bold text-secondary">{confPct}%</span>
                  <div className="w-full h-1.5 bg-surface-container-highest rounded-full mt-1 overflow-hidden">
                    <div
                      className="h-full bg-secondary rounded-full transition-all duration-700"
                      style={{ width: `${confPct}%` }}
                    />
                  </div>
                </div>
                <div>
                  <span className="block text-xs font-bold text-outline mb-1 uppercase tracking-widest">Severity</span>
                  <span className="text-2xl font-bold text-on-surface">{result.severity}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* ── Treatment Section ── */}
        <section className="space-y-4">

          {/* Toggle button */}
          <button
            onClick={() => setShowTreatment(!showTreatment)}
            className="w-full py-4 bg-secondary text-white font-bold rounded-xl flex items-center justify-center gap-2 shadow-lg active:scale-95 transition-transform border border-white/20"
          >
            <span className="material-symbols-outlined">medical_services</span>
            {showTreatment ? 'Hide Treatment Plan' : 'View Treatment Plan'}
          </button>

          {/* Treatment Panel */}
          {showTreatment && (
            <div className="bg-white/95 backdrop-blur-md p-6 rounded-xl border border-secondary/20 shadow-xl">
              <h3 className="text-2xl font-bold text-primary mb-6 flex items-center gap-2">
                <span className="material-symbols-outlined text-secondary">list_alt</span>
                Recommended Actions
              </h3>

              <div className="space-y-3">
                {displaySteps.slice(0, 5).map((step, i) => (
                  <div
                    key={i}
                    className="flex gap-4 p-3 bg-surface-container-low/50 rounded-lg items-start border border-outline-variant/20"
                  >
                    <span className="w-8 h-8 flex items-center justify-center bg-secondary-container text-on-secondary-container font-bold rounded-full flex-shrink-0 text-sm">
                      {i + 1}
                    </span>
                    <div>
                      <p className="font-bold text-on-surface">{step.title}</p>
                      {step.detail && (
                        <p className="text-sm text-on-surface-variant mt-0.5">{step.detail}</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>

              {/* Full AI Report collapsible */}
              {result.agent_report && (
                <>
                  {showFullReport && (
                    <div className="mt-6 pt-6 border-t border-outline-variant/30">
                      <h4 className="text-xs font-bold text-outline uppercase tracking-widest mb-3">
                        Full AI Report
                      </h4>
                      <pre className="text-xs text-on-surface-variant whitespace-pre-wrap leading-relaxed">
                        {result.agent_report}
                      </pre>
                    </div>
                  )}
                  <button
                    onClick={() => setShowFullReport(!showFullReport)}
                    className="mt-3 text-xs text-secondary underline cursor-pointer bg-transparent border-none block"
                  >
                    {showFullReport ? 'Hide full AI report ▲' : 'Show full AI report ▼'}
                  </button>
                </>
              )}
            </div>
          )}

          {/* Back button */}
          <button
            onClick={onBack}
            className="w-full py-4 bg-white/10 backdrop-blur-md text-white font-bold rounded-xl flex items-center justify-center gap-2 hover:bg-white/20 transition-colors border border-white/30 mb-10"
          >
            <span className="material-symbols-outlined">arrow_back</span>
            Back to Dashboard
          </button>
        </section>
      </main>

      {/* ── Bottom Nav ── */}
      <nav className="fixed bottom-0 left-0 w-full z-50 flex justify-around items-center px-4 py-2 bg-surface/90 backdrop-blur-md rounded-t-xl border-t border-outline-variant/20">
        <button
          onClick={onBack}
          className="flex flex-col items-center text-on-surface-variant px-4 py-1 hover:text-primary transition-all cursor-pointer"
        >
          <span className="material-symbols-outlined">dashboard</span>
          <span className="text-xs font-bold uppercase tracking-widest">Dashboard</span>
        </button>
        <button
          onClick={onBack}
          className="flex flex-col items-center bg-secondary-container text-on-secondary-container rounded-full px-4 py-1 cursor-pointer"
        >
          <span
            className="material-symbols-outlined"
            style={{ fontVariationSettings: "'FILL' 1" }}
          >center_focus_strong</span>
          <span className="text-xs font-bold uppercase tracking-widest">Scan</span>
        </button>
        <button className="flex flex-col items-center text-on-surface-variant px-4 py-1 hover:text-primary transition-all cursor-pointer">
          <span className="material-symbols-outlined">history</span>
          <span className="text-xs font-bold uppercase tracking-widest">History</span>
        </button>
        <button className="flex flex-col items-center text-on-surface-variant px-4 py-1 hover:text-primary transition-all cursor-pointer">
          <span className="material-symbols-outlined">settings</span>
          <span className="text-xs font-bold uppercase tracking-widest">Settings</span>
        </button>
      </nav>
    </div>
  );
}
