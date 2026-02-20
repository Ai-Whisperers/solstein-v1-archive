import React from 'react';
import { X, Calculator, Lightbulb, Info, ArrowRight } from 'lucide-react';

function TransparencyModal({ company, onClose }) {
  const breakdown = company.scoring_breakdown || {};
  
  const ScoreSection = ({ title, expl }) => {
    if (!expl) return null;
    
    return (
      <div className="space-y-4 mb-8">
        <div className="flex items-center justify-between border-b border-slate-700 pb-2">
          <h4 className="font-wizard text-alchemist-gold text-lg uppercase tracking-wider">{title} Score</h4>
          <span className="text-2xl font-mono font-bold text-white">{expl.final_score.toFixed(1)}</span>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-4">
            <div className="flex items-center space-x-2 text-xs text-slate-500 uppercase tracking-widest">
              <Calculator className="w-3 h-3" />
              <span>Mathematical Components</span>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between items-center bg-slate-900/50 p-3 rounded-lg border border-slate-800">
                <span className="text-sm text-slate-400">Base Doctrine Score</span>
                <span className="font-mono text-white">+{expl.base_score.toFixed(1)}</span>
              </div>
              {expl.components.map((comp, i) => (
                <div key={i} className="flex justify-between items-center bg-slate-900/30 p-3 rounded-lg border border-slate-800/50 hover:border-alchemist-gold/30 transition-all">
                  <div className="flex flex-col">
                    <span className="text-sm font-semibold text-slate-200">{comp.name}</span>
                    <span className="text-[10px] font-mono text-slate-500">{comp.formula}</span>
                  </div>
                  <span className={`font-mono ${comp.value >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                    {comp.value >= 0 ? '+' : ''}{comp.value.toFixed(1)}
                  </span>
                </div>
              ))}
              <div className="flex justify-between items-center pt-2 border-t border-slate-800">
                <span className="text-sm font-bold text-alchemist-gold">Calculated Sigma</span>
                <span className="font-mono font-bold text-alchemist-gold">{expl.final_score.toFixed(1)}</span>
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <div className="flex items-center space-x-2 text-xs text-slate-500 uppercase tracking-widest">
              <Lightbulb className="w-3 h-3" />
              <span>Logic Flow & Reasoning</span>
            </div>
            <div className="space-y-3">
              <div className="bg-slate-900/20 border-l-2 border-alchemist-gold p-4 rounded-r-lg">
                <p className="text-xs text-slate-300 italic leading-relaxed">
                  "The Guild initiates every calculation with the Baseline of Reality (5.0). From there, we adjust based on the signals harvested from the market fog."
                </p>
              </div>
              {expl.components.map((comp, i) => (
                <div key={i} className="flex items-start space-x-3 group">
                  <div className="mt-1.5 w-1.5 h-1.5 rounded-full bg-slate-700 group-hover:bg-alchemist-gold transition-colors" />
                  <div className="space-y-1">
                    <div className="text-xs font-bold text-slate-400 uppercase tracking-tighter">{comp.name}</div>
                    <p className="text-sm text-slate-300 font-light">{comp.reasoning}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-alchemist-bg/90 backdrop-blur-xl animate-in fade-in duration-300" onClick={onClose} />
      
      <div className="relative w-full max-w-5xl max-h-[90vh] glass-card shadow-2xl overflow-hidden border-slate-700/50 flex flex-col animate-in zoom-in-95 duration-300">
        <div className="flex items-center justify-between p-6 bg-slate-900/50 border-b border-slate-800">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-slate-800 rounded-lg flex items-center justify-center border border-slate-700">
              <Info className="text-alchemist-gold w-6 h-6" />
            </div>
            <div>
              <h3 className="text-xl font-wizard text-white tracking-widest">{company.name}</h3>
              <p className="text-xs text-slate-500 font-mono tracking-tighter uppercase">{company.id} // SIGNAL BREAKDOWN</p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-slate-800 rounded-full text-slate-500 hover:text-white transition-all">
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-8 custom-scrollbar">
          <div className="max-w-4xl mx-auto">
            <ScoreSection title="Growth" expl={breakdown.growth} />
            <ScoreSection title="Financial Health" expl={breakdown.financial} />
            <ScoreSection title="Competitive Position" expl={breakdown.competitive} />
          </div>
        </div>

        <div className="p-6 bg-slate-900/50 border-t border-slate-800 flex justify-between items-center">
           <div className="text-xs text-slate-500 font-mono">
             CALC_TIMESTAMP: {new Date().toISOString()}
           </div>
           <button 
             onClick={onClose}
             className="px-6 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition-all text-sm font-wizard tracking-widest uppercase"
           >
             Close Scroll
           </button>
        </div>
      </div>
    </div>
  );
}

export default TransparencyModal;
