import { useRef, useState } from 'react';
import { Bell, Maximize as Focus, LayoutGrid, History, Settings, Upload, Camera,
         Lightbulb as TipsAndUpdates, ShieldCheck as Verified, CheckCircle2 as CheckCircle,
         Loader2, AlertCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { ScanResult, AuthState } from '../App.tsx';

const API_URL = import.meta.env.VITE_API_URL || 'http://192.168.137.111:8000';

interface HomeProps {
  auth: AuthState | null;
  onScanComplete: (result: ScanResult) => void;
}

const RECENT_ACTIVITY = [
  {
    id: '1',
    name: 'Monstera Deliciosa',
    status: 'HEALTHY' as const,
    time: '2 HOURS AGO',
    imageUrl: 'https://images.unsplash.com/photo-1614594975525-e45190c55d0b?q=80&w=400&auto=format&fit=crop',
  },
  {
    id: '2',
    name: 'Echeveria Elegans',
    status: 'ISSUES FOUND' as const,
    time: 'YESTERDAY',
    imageUrl: 'https://images.unsplash.com/photo-1509316785289-025f5b846b35?q=80&w=400&auto=format&fit=crop',
  },
  {
    id: '3',
    name: 'Aloe Barbadensis',
    status: 'HEALTHY' as const,
    time: '3 DAYS AGO',
    imageUrl: 'https://images.unsplash.com/photo-1596547609652-9cf5d8d76921?q=80&w=400&auto=format&fit=crop',
  },
];

const LOADING_MESSAGES = [
  { delay: 0,      msg: '🔍 Analysing leaf image...' },
  { delay: 3000,   msg: '🧠 Detecting disease with EfficientNet-B3...' },
  { delay: 8000,   msg: '🤖 Running AI Disease Specialist...' },
  { delay: 60000,  msg: '💊 Generating treatment plan...' },
  { delay: 120000, msg: '🌤️ Checking weather for spray schedule...' },
  { delay: 180000, msg: '📋 Finalising report... almost done!' },
];

export default function Home({ auth, onScanComplete }: HomeProps) {
  const fileInputRef               = useRef<HTMLInputElement>(null);
  const [loading, setLoading]      = useState(false);
  const [loadingMsg, setLoadingMsg] = useState('Analysing...');
  const [error, setError]          = useState<string | null>(null);
  const [preview, setPreview]      = useState<string | null>(null);
  const msgTimers                  = useRef<ReturnType<typeof setTimeout>[]>([]);

  const clearMsgTimers = () => {
    msgTimers.current.forEach(clearTimeout);
    msgTimers.current = [];
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const objectUrl = URL.createObjectURL(file);
    setPreview(objectUrl);
    setError(null);
    setLoading(true);
    setLoadingMsg('🔍 Analysing leaf image...');

    clearMsgTimers();
    LOADING_MESSAGES.forEach(({ delay, msg }) => {
      const t = setTimeout(() => setLoadingMsg(msg), delay);
      msgTimers.current.push(t);
    });

    try {
      const formData = new FormData();
      formData.append('file', file);

      const headers: Record<string, string> = {
        'ngrok-skip-browser-warning': 'true',
      };
      if (auth?.token) {
        headers['Authorization'] = `Bearer ${auth.token}`;
      }

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 9000000);

      const res = await fetch(`${API_URL}/api/v1/predict`, {
        method: 'POST',
        headers,
        body: formData,
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
      clearMsgTimers();

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || `Server error ${res.status}`);
      }

      const data = await res.json();
      const result: ScanResult = {
        prediction_id: data.prediction_id,
        plant:         data.plant,
        disease:       data.disease,
        confidence:    data.confidence,
        severity:      data.severity,
        is_healthy:    data.is_healthy,
        top3:          data.top3 ?? [],
        agent_report:  data.agent_report ?? null,
        imagePreview:  objectUrl,
      };
      onScanComplete(result);
    } catch (err) {
      clearMsgTimers();
      setError(err instanceof Error ? err.message : 'Scan failed. Check backend is running.');
      setLoading(false);
    }
    e.target.value = '';
  };

  const triggerCamera = () => {
    if (fileInputRef.current) {
      fileInputRef.current.setAttribute('capture', 'environment');
      fileInputRef.current.click();
    }
  };

  const triggerGallery = () => {
    if (fileInputRef.current) {
      fileInputRef.current.removeAttribute('capture');
      fileInputRef.current.click();
    }
  };

  return (
    <div className="min-h-screen bg-forest-gradient text-white font-sans flex flex-col relative overflow-hidden pb-40">
      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg,image/png,image/jpg"
        className="hidden"
        onChange={handleFileChange}
      />

      {/* Decorative Botanical elements */}
      <div className="fixed top-20 -left-10 opacity-10 pointer-events-none animate-float">
        <img src="https://img.icons8.com/material-rounded/200/a0f4c8/leaf.png" alt="decor" />
      </div>
      <div className="fixed top-1/2 -right-16 opacity-5 pointer-events-none animate-sway">
        <img src="https://img.icons8.com/material-rounded/250/a0f4c8/potted-plant.png" alt="decor" />
      </div>

      {/* Top App Bar */}
      <header className="fixed top-0 left-0 w-full z-50 flex justify-between items-center px-6 h-16 bg-white/5 backdrop-blur-md shadow-sm border-b border-white/10">
        <div className="flex items-center gap-2">
          <img src="/logo.png" alt="logo" className="w-6 h-6 rounded-md" />
          <span className="text-2xl font-bold tracking-tight text-primary-fixed">AgroAI</span>
        </div>
        <div className="flex items-center gap-4">
          <button className="p-2 hover:bg-white/10 transition-colors rounded-full relative">
            <Bell className="w-6 h-6 text-primary-fixed" />
            <span className="absolute top-2 right-2 w-2 h-2 bg-secondary rounded-full border border-primary"></span>
          </button>
          <div className="w-8 h-8 rounded-full overflow-hidden border border-white/20">
            <img src="/logo.png" alt="AgroAI" className="w-full h-full object-cover" />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-grow pt-24 px-6 max-w-4xl mx-auto w-full relative z-10">
        {/* Hero Section */}
        <section className="mb-10 text-left">
          <h1 className="text-4xl font-bold mb-2">Crop Diagnostic</h1>
          <p className="text-primary-fixed-dim/80 text-lg">Identify crop diseases and get AI-powered treatment plans instantly.</p>

        {/* Bento Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Central Scan Area */}
          <motion.div
            whileHover={{ scale: 1.01 }}
            className="md:col-span-2 bg-white/5 backdrop-blur-md rounded-2xl p-8 border-2 border-dashed border-white/10 flex flex-col items-center justify-center min-h-[400px] text-center hover:border-secondary transition-all group"
          >
            {/* Preview thumbnail */}
            <AnimatePresence>
              {preview && !loading && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="mb-6 rounded-2xl overflow-hidden w-36 h-36 border-2 border-white/20 shadow-lg"
                >
                  <img src={preview} alt="Preview" className="w-full h-full object-cover" />
                </motion.div>
              )}
            </AnimatePresence>

            {/* Loading state */}
            <AnimatePresence>
              {loading && (
                <motion.div
                  initial={{ opacity: 0, y: 4 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  className="mb-6 bg-secondary/20 border border-secondary/30 rounded-xl px-4 py-3 max-w-xs w-full text-left"
                >
                  <div className="flex items-center gap-2 mb-1">
                    <Loader2 className="w-4 h-4 animate-spin text-secondary-fixed" />
                    <p className="text-secondary-fixed text-xs font-medium">{loadingMsg}</p>
                  </div>
                  <p className="text-white/40 text-[10px]">AI agents may take 3–5 minutes. Please wait...</p>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Error */}
            {error && (
              <div className="mb-6 flex items-start gap-2 bg-red-500/20 border border-red-400/30 rounded-xl px-3 py-2 max-w-xs w-full text-left">
                <AlertCircle size={16} className="text-red-300 mt-0.5 flex-shrink-0" />
                <p className="text-red-200 text-xs leading-relaxed">{error}</p>
              </div>
            )}

            {!loading && (
              <>
                <div className="w-20 h-20 rounded-full bg-secondary/10 flex items-center justify-center text-secondary mb-6 group-hover:scale-110 transition-transform border border-secondary/20">
                  <Focus className="w-10 h-10" />
                </div>
                <h2 className="text-2xl font-bold mb-3">Upload or Capture</h2>
                <p className="text-primary-fixed-dim/70 mb-8 max-w-xs mx-auto text-sm leading-relaxed">
                  Drag and drop your high-resolution leaf image here, or use your camera for a live diagnostic.
                </p>
              </>
            )}

            <div className="flex flex-wrap gap-3 justify-center">
              <button
                onClick={triggerGallery}
                disabled={loading}
                className="bg-secondary text-white px-8 py-3 rounded-full font-bold text-xs uppercase tracking-widest flex items-center gap-2 shadow-lg active:scale-95 transition-all disabled:opacity-60"
              >
                <Upload className="w-4 h-4" />
                Browse Files
              </button>
              <button
                onClick={triggerCamera}
                disabled={loading}
                className="bg-white/10 backdrop-blur-md text-white px-8 py-3 rounded-full font-bold text-xs uppercase tracking-widest flex items-center gap-2 hover:bg-white/20 active:scale-95 transition-all disabled:opacity-60"
              >
                <Camera className="w-4 h-4" />
                Open Camera
              </button>
            </div>
          </motion.div>

          {/* Sidebar */}
          <div className="flex flex-col gap-6">
            <div className="bg-primary-container/40 backdrop-blur-sm p-6 rounded-2xl border border-white/10 flex flex-col justify-between flex-grow">
              <TipsAndUpdates className="w-8 h-8 text-secondary mb-4" />
              <div>
                <h3 className="text-lg font-bold mb-2">Optimization Tip</h3>
                <p className="text-sm text-primary-fixed-dim/90 leading-relaxed">
                  For the most accurate analysis, ensure the leaf is placed against a neutral background with soft, natural lighting.
                </p>
              </div>
            </div>

            <div className="bg-white/5 backdrop-blur-sm p-6 rounded-2xl border border-white/10">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xs font-bold uppercase tracking-widest text-secondary opacity-80">Supported</h3>
                <Verified className="w-4 h-4 text-secondary" />
              </div>
              <ul className="space-y-3">
                <li className="flex items-center gap-3 text-sm text-primary-fixed-dim/90">
                  <CheckCircle className="w-4 h-4 text-secondary" /> 30+ Plant Species
                </li>
                <li className="flex items-center gap-3 text-sm text-primary-fixed-dim/90">
                  <CheckCircle className="w-4 h-4 text-secondary" /> 150+ Common Diseases
                </li>
                <li className="flex items-center gap-3 text-sm text-primary-fixed-dim/90">
                  <CheckCircle className="w-4 h-4 text-secondary" /> Macro Leaf Analysis
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <section className="mt-16 mb-20">
          <h3 className="text-xs font-bold text-secondary uppercase tracking-[0.2em] mb-6">Recent Activity</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {RECENT_ACTIVITY.map((activity) => (
              <motion.div
                key={activity.id}
                whileHover={{ y: -5 }}
                className="bg-white/5 backdrop-blur-md rounded-2xl overflow-hidden border border-white/10 group cursor-pointer"
              >
                <div className="h-40 relative overflow-hidden">
                  <img src={activity.imageUrl} alt={activity.name} className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110" />
                  <div className={`absolute top-3 right-3 px-2 py-1 rounded-full text-[10px] font-bold ${activity.status === 'HEALTHY' ? 'bg-secondary text-white' : 'bg-red-500 text-white'}`}>
                    {activity.status}
                  </div>
                </div>
                <div className="p-4">
                  <p className="text-[10px] font-bold text-primary-fixed-dim opacity-60 uppercase tracking-widest mb-1">{activity.time}</p>
                  <p className="font-bold text-sm tracking-tight">{activity.name}</p>
                </div>
              </motion.div>
            ))}
            <div className="bg-white/5 backdrop-blur-md rounded-2xl border-2 border-dashed border-white/10 p-6 flex flex-col items-center justify-center text-center group cursor-pointer hover:bg-white/10 transition-all">
              <History className="w-10 h-10 text-secondary mb-3 group-hover:scale-110 transition-transform" />
              <p className="text-[10px] font-bold text-primary-fixed-dim uppercase tracking-widest">View Full History</p>
            </div>
          </div>
        </section>
      </section>
      </main>

      {/* Bottom Navigation */}
      <nav className="fixed bottom-0 left-0 w-full z-50 flex justify-around items-center px-4 py-3 bg-primary-container/80 backdrop-blur-xl shadow-2xl rounded-t-3xl border-t border-white/10">
        <button className="flex flex-col items-center gap-1 p-2 text-primary-fixed-dim hover:text-secondary group transition-colors">
          <LayoutGrid className="w-6 h-6 group-hover:scale-110 transition-transform" />
          <span className="text-[10px] uppercase font-bold tracking-widest">Dashboard</span>
        </button>
        <button
          onClick={triggerGallery}
          disabled={loading}
          className="flex flex-col items-center gap-1 bg-secondary text-white rounded-full p-4 transform -translate-y-6 shadow-2xl border-4 border-primary shadow-secondary/20 disabled:opacity-60"
        >
          <Focus className="w-8 h-8" />
          <span className="text-[10px] uppercase font-bold tracking-widest mt-1">Scan</span>
        </button>
        <button className="flex flex-col items-center gap-1 p-2 text-primary-fixed-dim hover:text-secondary group transition-colors">
          <History className="w-6 h-6 group-hover:scale-110 transition-transform" />
          <span className="text-[10px] uppercase font-bold tracking-widest">History</span>
        </button>
        <button className="flex flex-col items-center gap-1 p-2 text-primary-fixed-dim hover:text-secondary group transition-colors">
          <Settings className="w-6 h-6 group-hover:scale-110 transition-transform" />
          <span className="text-[10px] uppercase font-bold tracking-widest">Settings</span>
        </button>
      </nav>
    </div>
  );
}
