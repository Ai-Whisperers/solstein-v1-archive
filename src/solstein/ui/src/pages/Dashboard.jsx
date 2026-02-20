import React, { useState, useEffect } from 'react';
import { getCompanies, scoreCompany } from '../api/client';
import TransparencyModal from '../components/TransparencyModal';
import { Rocket, Minus, Skull, Info, Loader2, Search } from 'lucide-react';

function Dashboard() {
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [scoringId, setScoringId] = useState(null);
  const [selectedCompany, setSelectedCompany] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchCompanies();
  }, []);

  const fetchCompanies = async () => {
    try {
      setLoading(true);
      const res = await getCompanies();
      setCompanies(res.data);
    } catch (err) {
      console.error('Failed to fetch companies', err);
    } finally {
      setLoading(false);
    }
  };

  const handleScore = async (id) => {
    try {
      setScoringId(id);
      const res = await scoreCompany(id);
      setCompanies(prev => prev.map(c => c.id === id ? { ...c, ...res.data } : c));
    } catch (err) {
      console.error('Failed to score company', err);
    } finally {
      setScoringId(null);
    }
  };

  const filteredCompanies = companies
    .filter(c => c.name.toLowerCase().includes(searchTerm.toLowerCase()))
    .sort((a, b) => (b.growth_score || 0) - (a.growth_score || 0));

  const getClassification = (score) => {
    if (score === null || score === undefined) return { label: 'Unscored', color: 'text-slate-500', icon: Minus };
    if (score >= 7.0) return { label: 'Rocket', color: 'text-rose-500', icon: Rocket, shadow: 'rocket-shadow' };
    if (score <= 4.0) return { label: 'Dinosaur', color: 'text-slate-400', icon: Skull, shadow: 'dino-shadow' };
    return { label: 'Neutral', color: 'text-amber-400', icon: Minus };
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div className="space-y-2">
          <h2 className="text-3xl font-wizard text-white">Attractiveness Board</h2>
          <p className="text-slate-400 max-w-2xl font-light">
            The ranked view of competitive potential. Every score is a chain of reasoning, every classification a call to action. 
          </p>
        </div>
        
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input 
            type="text" 
            placeholder="Search market signals..." 
            className="bg-alchemist-card/50 border border-slate-800 rounded-lg pl-10 pr-4 py-2 text-sm focus:outline-none focus:border-alchemist-gold/50 w-full md:w-64 transition-all"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      <div className="glass-card overflow-hidden border-slate-800/80">
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead className="bg-slate-900/50 border-b border-slate-800">
              <tr>
                <th className="px-6 py-4 text-xs font-wizard tracking-widest text-slate-500 uppercase">Rank</th>
                <th className="px-6 py-4 text-xs font-wizard tracking-widest text-slate-500 uppercase">Company</th>
                <th className="px-6 py-4 text-xs font-wizard tracking-widest text-slate-500 uppercase text-center">Growth</th>
                <th className="px-6 py-4 text-xs font-wizard tracking-widest text-slate-500 uppercase text-center">Financial</th>
                <th className="px-6 py-4 text-xs font-wizard tracking-widest text-slate-500 uppercase text-center">Comp. Pos</th>
                <th className="px-6 py-4 text-xs font-wizard tracking-widest text-slate-500 uppercase">Classification</th>
                <th className="px-6 py-4 text-xs font-wizard tracking-widest text-slate-500 uppercase text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {loading ? (
                <tr>
                  <td colSpan="7" className="px-6 py-12 text-center text-slate-500">
                    <div className="flex flex-col items-center space-y-4">
                      <Loader2 className="w-8 h-8 animate-spin text-alchemist-gold" />
                      <span className="font-wizard tracking-[0.2em]">Summoning Market Data...</span>
                    </div>
                  </td>
                </tr>
              ) : filteredCompanies.map((company, index) => {
                const cls = getClassification(company.growth_score);
                const Icon = cls.icon;
                
                return (
                  <tr key={company.id} className="hover:bg-slate-800/30 transition-colors group">
                    <td className="px-6 py-4 text-sm font-mono text-slate-500">
                      {(index + 1).toString().padStart(2, '0')}
                    </td>
                    <td className="px-6 py-4">
                      <div className="font-semibold text-slate-200">{company.name}</div>
                      <div className="text-xs text-slate-500 mt-1">{company.industry}</div>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <div className={`text-lg font-mono ${company.growth_score ? 'text-white' : 'text-slate-600'}`}>
                        {company.growth_score?.toFixed(1) || '--'}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <div className={`text-sm font-mono ${company.financial_health_score ? 'text-slate-300' : 'text-slate-600'}`}>
                        {company.financial_health_score?.toFixed(1) || '--'}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <div className={`text-sm font-mono ${company.competitive_position_score ? 'text-slate-300' : 'text-slate-600'}`}>
                        {company.competitive_position_score?.toFixed(1) || '--'}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className={`flex items-center space-x-2 text-xs font-bold uppercase tracking-wider ${cls.color}`}>
                        <Icon className="w-4 h-4" />
                        <span>{cls.label}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end space-x-3">
                        {company.growth_score ? (
                          <button 
                            onClick={() => setSelectedCompany(company)}
                            className="p-2 text-slate-500 hover:text-alchemist-gold hover:bg-alchemist-gold/10 rounded-lg transition-all"
                            title="View Deep Transparency"
                          >
                            <Info className="w-5 h-5" />
                          </button>
                        ) : (
                          <button 
                            onClick={() => handleScore(company.id)}
                            disabled={scoringId === company.id}
                            className="text-xs font-wizard tracking-widest uppercase border border-alchemist-gold/30 px-3 py-1.5 rounded text-alchemist-gold hover:bg-alchemist-gold hover:text-alchemist-bg transition-all disabled:opacity-50"
                          >
                            {scoringId === company.id ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Score'}
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {selectedCompany && (
        <TransparencyModal 
          company={selectedCompany} 
          onClose={() => setSelectedCompany(null)} 
        />
      )}
    </div>
  );
}

export default Dashboard;
