import { useState } from 'react';
import { Mail, Lock, Eye, EyeOff, ArrowRight, Loader2, AlertCircle, Facebook } from 'lucide-react';
import { motion } from 'motion/react';
import { AuthState } from '../App.tsx';

const API_URL = import.meta.env.VITE_API_URL || 'http://192.168.137.111:8000';

interface LoginProps {
  onLogin: (auth: AuthState) => void;
}

export default function Login({ onLogin }: LoginProps) {
  const [email, setEmail] = useState('admin@agriguard.com');
  const [password, setPassword] = useState('admin');
  const [showPw, setShowPw]     = useState(false);
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState<string | null>(null);

  const handleSubmit = async () => {
    setError(null);
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'ngrok-skip-browser-warning': 'true',
        },
        body: JSON.stringify({ email, password }),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || `Login failed (${res.status})`);
      }

      const data: AuthState = await res.json();
      onLogin(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Cannot reach backend. Is it running?');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col lg:flex-row bg-forest-gradient text-white font-sans overflow-x-hidden relative">
      {/* Decorative Background Elements */}
      <div className="fixed top-20 right-[10%] opacity-[0.1] pointer-events-none animate-float hidden lg:block z-0">
        <motion.div animate={{ rotate: [0, 10, 0] }} transition={{ duration: 10, repeat: Infinity }}>
          <img src="https://img.icons8.com/ios-filled/250/ffffff/leaf.png" alt="leaf" className="w-[180px] invert" />
        </motion.div>
      </div>

      {/* Header */}
      <header className="fixed top-0 left-0 w-full z-50 flex justify-between items-center px-6 h-16 bg-black/20 backdrop-blur-md border-b border-white/10">
        <div className="flex items-center gap-2">
          <img src="https://img.icons8.com/material-rounded/48/c1ecd4/leaf.png" alt="logo" className="w-8 h-8" />
          <span className="text-2xl font-bold tracking-tight">FloraScope</span>
        </div>
        <div className="hidden md:flex items-center gap-6">
          <span className="text-primary-fixed-dim text-xs font-bold uppercase tracking-wider opacity-80">Precision Botany</span>
        </div>
        <button className="p-2 hover:bg-white/10 transition-colors rounded-full opacity-70 hover:opacity-100">
          <img src="https://img.icons8.com/material-outlined/24/ffffff/help.png" alt="help" className="w-6 h-6" />
        </button>
      </header>

      {/* Main Content */}
      <main className="flex-grow pt-16 flex flex-col lg:flex-row relative z-10 w-full">
        {/* Left: Hero */}
        <section className="lg:w-1/2 relative overflow-hidden min-h-[400px] lg:min-h-0 flex flex-col justify-end p-6 lg:p-16">
          <div className="absolute inset-0 z-0 animate-sway">
            <img
              alt="Lush green Monstera Deliciosa leaves"
              className="w-full h-full object-cover opacity-60 mix-blend-soft-light scale-110"
              src="https://images.unsplash.com/photo-1614594975525-e45190c55d0b?q=80&w=1000&auto=format&fit=crop"
            />
          </div>

          <div className="relative z-10 max-w-md">
            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-5xl lg:text-6xl font-extrabold leading-tight mb-6 text-white"
            >
              Identify. Diagnose. Nurture.
            </motion.h2>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="text-lg text-primary-fixed-dim/90 mb-10"
            >
              Empowering plant lovers with high-fidelity diagnostics and expert botanical care tools for every leaf in your garden.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2 }}
              className="glass-panel rounded-xl p-5 max-w-sm"
            >
              <div className="flex items-center gap-2 mb-3">
                <img src="https://img.icons8.com/material-rounded/24/c1ecd4/sparkling.png" alt="icon" className="w-4 h-4" />
                <span className="text-xs font-bold text-primary-fixed uppercase tracking-wider">Featured Plant of the Day</span>
              </div>
              <div className="flex gap-4 items-center">
                <div className="bg-primary/40 rounded-lg p-3">
                  <img src="https://img.icons8.com/material-rounded/48/c1ecd4/potted-plant.png" alt="plant icon" className="w-8 h-8" />
                </div>
                <div>
                  <h3 className="font-bold text-lg mb-1">Ficus Lyrata</h3>
                  <p className="text-sm text-primary-fixed-dim/80 leading-relaxed">
                    Commonly known as the Fiddle Leaf Fig. Keep it in bright, indirect light.
                  </p>
                </div>
              </div>
            </motion.div>
          </div>
        </section>

        {/* Right: Form */}
        <section className="lg:w-1/2 flex items-center justify-center p-6 lg:p-16">
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="w-full max-w-[440px] glass-panel p-8 lg:p-10 rounded-2xl"
          >
            <div className="mb-8">
              <h1 className="text-3xl font-bold mb-2">Welcome Back</h1>
              <p className="text-primary-fixed-dim opacity-80">Log in to your botanical dashboard to track your plant health.</p>
            </div>

            {/* Error banner */}
            {error && (
              <div className="mb-5 flex items-start gap-3 bg-red-500/20 border border-red-400/30 rounded-xl px-4 py-3">
                <AlertCircle size={18} className="text-red-300 mt-0.5 flex-shrink-0" />
                <p className="text-red-200 text-sm leading-snug">{error}</p>
              </div>
            )}

            <div className="space-y-6">
              {/* Email */}
              <div className="space-y-2">
                <label className="text-xs font-bold text-primary-fixed-dim uppercase tracking-wider block">Email Address</label>
                <div className="relative group">
                  <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-primary-fixed-dim/60 group-focus-within:text-secondary-fixed transition-colors" />
                  <input
                    type="email"
                    value={email}
                    onChange={e => setEmail(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && handleSubmit()}
                    placeholder="admin@florascope.com"
                    className="w-full pl-12 pr-4 py-4 bg-white/10 border border-white/10 rounded-xl focus:ring-2 focus:ring-secondary/20 focus:border-secondary outline-none transition-all placeholder:text-white/20 text-white"
                  />
                </div>
              </div>

              {/* Password */}
              <div className="space-y-2">
                <label className="text-xs font-bold text-primary-fixed-dim uppercase tracking-wider block">Password</label>
                <div className="relative group">
                  <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-primary-fixed-dim/60 group-focus-within:text-secondary-fixed transition-colors" />
                  <input
                    type={showPw ? 'text' : 'password'}
                    value={password}
                    onChange={e => setPassword(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && handleSubmit()}
                    placeholder="••••••••"
                    className="w-full pl-12 pr-12 py-4 bg-white/10 border border-white/10 rounded-xl focus:ring-2 focus:ring-secondary/20 focus:border-secondary outline-none transition-all placeholder:text-white/20 text-white"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPw(!showPw)}
                    className="absolute right-4 top-1/2 -translate-y-1/2 p-1"
                  >
                    {showPw
                      ? <EyeOff className="w-5 h-5 text-white" />
                      : <Eye className="w-5 h-5 text-primary-fixed-dim/60" />
                    }
                  </button>
                </div>
              </div>

              {/* Submit */}
              <motion.button
                whileTap={{ scale: 0.97 }}
                onClick={handleSubmit}
                disabled={loading}
                className="w-full py-4 bg-secondary-fixed text-primary font-bold text-lg rounded-xl shadow-xl hover:bg-secondary-container active:scale-95 transition-all flex items-center justify-center gap-2 disabled:opacity-60"
              >
                {loading ? (
                  <><Loader2 className="w-5 h-5 animate-spin" /> Signing in...</>
                ) : (
                  <>Sign In <ArrowRight className="w-5 h-5" /></>
                )}
              </motion.button>
            </div>

            <div className="relative my-8">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-white/10"></div>
              </div>
              <div className="relative flex justify-center">
                <span className="px-4 bg-transparent backdrop-blur-xl text-xs font-bold text-primary-fixed-dim/60 uppercase tracking-wider">Or continue with</span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <button className="flex items-center justify-center gap-2 py-3 px-4 bg-white/10 border border-white/10 rounded-xl hover:bg-white/20 transition-all font-bold text-xs uppercase tracking-wider">
                <img src="https://img.icons8.com/color/24/google-logo.png" alt="google" className="w-5 h-5" />
                Google
              </button>
              <button className="flex items-center justify-center gap-2 py-3 px-4 bg-white/10 border border-white/10 rounded-xl hover:bg-white/20 transition-all font-bold text-xs uppercase tracking-wider">
                <Facebook className="w-5 h-5 text-[#1877F2] fill-[#1877F2]" />
                Facebook
              </button>
            </div>

            <p className="text-primary-fixed-dim/40 text-xs text-center mt-6">
              Demo: admin@florascope.com / admin
            </p>
          </motion.div>
        </section>
      </main>

      <div className="fixed -bottom-16 -left-16 opacity-[0.1] pointer-events-none rotate-12 hidden lg:block z-0">
        <img src="https://img.icons8.com/ios-filled/500/ffffff/potted-plant.png" alt="decor" className="w-[320px] invert" />
      </div>
    </div>
  );
}
