import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import { Sparkles, Scroll, Activity } from 'lucide-react';

function App() {
  return (
    <Router>
      <div className="min-h-screen flex flex-col">
        <header className="border-b border-slate-800 bg-alchemist-bg/80 backdrop-blur-md sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-alchemist-gold rounded-full flex items-center justify-center shadow-[0_0_20px_rgba(251,191,36,0.3)]">
                <Sparkles className="text-alchemist-bg w-6 h-6" />
              </div>
              <h1 className="text-xl font-wizard uppercase tracking-[0.2em] text-alchemist-gold">Solstein</h1>
            </div>
            <nav className="hidden md:flex items-center space-x-8 text-sm font-medium tracking-widest text-slate-400">
              <span className="flex items-center space-x-2 text-alchemist-gold cursor-pointer">
                <Scroll className="w-4 h-4" />
                <span>Attractiveness Board</span>
              </span>
              <span className="flex items-center space-x-2 hover:text-slate-200 cursor-not-allowed">
                <Activity className="w-4 h-4" />
                <span>Simulations</span>
              </span>
            </nav>
          </div>
        </header>

        <main className="flex-1 max-w-7xl mx-auto px-4 py-8 w-full">
          <Routes>
            <Route path="/" element={<Dashboard />} />
          </Routes>
        </main>

        <footer className="border-t border-slate-800 py-8 bg-alchemist-bg">
          <div className="max-w-7xl mx-auto px-4 text-center">
            <p className="text-slate-500 text-xs tracking-widest">
              Built by <span className="text-alchemist-gold">AI Whisperers</span> — The wizards who find the diamonds nobody knew were there.
            </p>
          </div>
        </footer>
      </div>
    </Router>
  );
}

export default App;
