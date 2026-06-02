import React, { useState } from 'react';
import Login from './components/Login';
import Home from './components/Home';
import Result from './components/Result';

export type Screen = 'login' | 'dashboard' | 'result';

export interface AuthState {
  token: string;
  user?: { email: string; name?: string };
}

export interface ScanResult {
  prediction_id?: string;
  plant: string;
  disease: string;
  confidence: number;       // 0–1 float from backend
  severity: 'HEALTHY' | 'MILD' | 'MODERATE' | 'SEVERE';
  is_healthy: boolean;
  top3: { class_name: string; confidence: number }[];
  agent_report: string | null;
  imagePreview: string;
}

export default function App() {
  const [currentScreen, setCurrentScreen] = useState<Screen>('login');
  const [auth, setAuth]                   = useState<AuthState | null>(null);
  const [scanResult, setScanResult]       = useState<ScanResult | null>(null);

  return (
    <div className="antialiased selection:bg-secondary selection:text-white">
      {currentScreen === 'login' && (
        <Login
          onLogin={(a) => {
            setAuth(a);
            setCurrentScreen('dashboard');
          }}
        />
      )}
      {currentScreen === 'dashboard' && (
        <Home
          auth={auth}
          onScanComplete={(r) => {
            setScanResult(r);
            setCurrentScreen('result');
          }}
        />
      )}
      {currentScreen === 'result' && (
        <Result
          result={scanResult}
          onBack={() => setCurrentScreen('dashboard')}
        />
      )}
    </div>
  );
}
