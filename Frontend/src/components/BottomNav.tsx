import { LayoutGrid, Home, Leaf, Settings, ScanLine } from 'lucide-react';
import { motion } from 'motion/react';
import { Screen } from '../types';

interface BottomNavProps {
  currentScreen: Screen;
  onSetScreen: (screen: Screen) => void;
}

export default function BottomNav({ currentScreen, onSetScreen }: BottomNavProps) {
  const navItems = [
    { id: 'HOME' as Screen, icon: Home, label: 'Home' },
    { id: 'RESULT' as Screen, icon: ScanLine, label: 'Identify' },
    { id: 'PLANTS' as Screen, icon: Leaf, label: 'My Plants' },
    { id: 'SETTINGS' as Screen, icon: Settings, label: 'Settings' },
  ];

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 flex justify-around items-center px-4 py-3 pb-safe max-w-md mx-auto bg-primary/95 backdrop-blur-lg border-t border-white/10 rounded-t-3xl bottom-nav-shadow">
      {navItems.map((item) => {
        const isActive = currentScreen === item.id || (item.id === 'RESULT' && currentScreen === 'RESULT');
        
        return (
          <button
            key={item.id}
            onClick={() => onSetScreen(item.id)}
            className={`flex flex-col items-center justify-center transition-all duration-200 px-5 py-1.5 rounded-full ${
              isActive 
                ? 'bg-secondary-container text-primary' 
                : 'text-primary-fixed hover:bg-white/5'
            }`}
          >
            <item.icon size={20} strokeWidth={isActive ? 2.5 : 2} />
            <span className="text-[10px] font-bold mt-1 uppercase tracking-wider">{item.label}</span>
          </button>
        );
      })}
    </nav>
  );
}
