import { Menu } from 'lucide-react';

export default function TopAppBar() {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-primary/80 backdrop-blur-md flex items-center justify-between px-5 h-16 w-full max-w-md mx-auto">
      <div className="flex items-center gap-4">
        <button className="text-white hover:bg-white/10 p-2 rounded-full transition-colors active:scale-95">
          <Menu size={24} />
        </button>
        <h1 className="text-xl font-bold text-white tracking-tight">PlantCare AI</h1>
      </div>
      <div className="w-10 h-10 rounded-full overflow-hidden border border-white/20 active:scale-95 transition-transform cursor-pointer">
        <img 
          alt="User Profile" 
          className="w-full h-full object-cover"
          src="https://lh3.googleusercontent.com/aida-public/AB6AXuAS_gy_4tMjgbP99uVywfuZ1fdBEMbxUOqtSnRSyW7C8h1XwwTW_L6TBlMA3SHF25cwmjqNV_DwtDw9DcIaaGwpOfx6Bo3UHFrHUaxg0yJEV20f8inLPtBZ55DvsidF_K3tkfkWOGFaQp8GhWI8faIgUoBhj5Z0CAFJGkh0Rk7oCEeGhqi6OxtkHU1433Z6_6616IxggNaRCAS2VggGIVOs8zkRKiigFXcZXyRIEenpOX0GzDFL9DsZTbMNYT1v8nZ_vu697C1L_GvG" 
        />
      </div>
    </header>
  );
}
