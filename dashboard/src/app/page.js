"use client";

import { useState } from "react";

// Mock data for demonstration (in production, this comes from Supabase)
const MOCK_COMPANIES = [
    {
        id: "1", name: "Acme Energy BV", industry: "Energy Software", tier: "Tier 1",
        growth_score: 8.4, financial_health_score: 7.2, competitive_position_score: 8.1,
        classification: "Rocket", revenue: 45000000, growth_rate: 32, employees: 280,
        ai_maturity: "Strong", headquarters: "Amsterdam, NL",
    },
    {
        id: "2", name: "GridTech Solutions", industry: "Energy Software", tier: "Tier 1",
        growth_score: 7.8, financial_health_score: 6.9, competitive_position_score: 7.5,
        classification: "Rocket", revenue: 38000000, growth_rate: 28, employees: 210,
        ai_maturity: "Strong", headquarters: "Berlin, DE",
    },
    {
        id: "3", name: "Voltaire Analytics", industry: "Energy Software", tier: "Tier 2",
        growth_score: 6.1, financial_health_score: 6.8, competitive_position_score: 5.9,
        classification: "Neutral", revenue: 22000000, growth_rate: 15, employees: 150,
        ai_maturity: "Moderate", headquarters: "Paris, FR",
    },
    {
        id: "4", name: "FluxCore GmbH", industry: "Energy Software", tier: "Tier 2",
        growth_score: 5.5, financial_health_score: 5.2, competitive_position_score: 6.0,
        classification: "Neutral", revenue: 18000000, growth_rate: 12, employees: 120,
        ai_maturity: "Moderate", headquarters: "Munich, DE",
    },
    {
        id: "5", name: "PowerGrid Systems AG", industry: "Energy Software", tier: "Tier 2",
        growth_score: 4.8, financial_health_score: 5.5, competitive_position_score: 4.2,
        classification: "Neutral", revenue: 15000000, growth_rate: 8, employees: 95,
        ai_maturity: "Low", headquarters: "Zurich, CH",
    },
    {
        id: "6", name: "LegacyPower AG", industry: "Energy Software", tier: "Tier 3",
        growth_score: 3.2, financial_health_score: 4.1, competitive_position_score: 2.8,
        classification: "Dinosaur", revenue: 52000000, growth_rate: -2, employees: 680,
        ai_maturity: "None", headquarters: "Vienna, AT",
    },
    {
        id: "7", name: "OldGrid Corp", industry: "Energy Software", tier: "Tier 4",
        growth_score: 2.1, financial_health_score: 3.5, competitive_position_score: 1.9,
        classification: "Dinosaur", revenue: 28000000, growth_rate: -5, employees: 410,
        ai_maturity: "None", headquarters: "Brussels, BE",
    },
];

function ScoreBar({ score, maxScore = 10, color }) {
    const percentage = (score / maxScore) * 100;
    return (
        <div className="score-bar" style={{ width: '100%' }}>
            <div
                className="score-bar-fill"
                style={{
                    width: `${percentage}%`,
                    background: color || `linear-gradient(90deg, var(--solstein-gold), var(--solstein-gold-light))`,
                }}
            />
        </div>
    );
}

function ClassificationBadge({ classification }) {
    const badgeClass = classification === "Rocket"
        ? "badge-rocket"
        : classification === "Dinosaur"
            ? "badge-dinosaur"
            : "badge-neutral";

    const icon = classification === "Rocket" ? "🚀" : classification === "Dinosaur" ? "🦕" : "⚖️";

    return <span className={badgeClass}>{icon} {classification}</span>;
}

function StatCard({ title, value, subtitle, delay }) {
    return (
        <div className={`glass-card animate-in animate-in-delay-${delay}`} style={{ padding: '24px' }}>
            <p style={{ color: 'var(--solstein-text-muted)', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '8px' }}>
                {title}
            </p>
            <p className="gold-text" style={{ fontSize: '2rem', fontWeight: 700, lineHeight: 1.2 }}>
                {value}
            </p>
            {subtitle && (
                <p style={{ color: 'var(--solstein-text-muted)', fontSize: '0.8rem', marginTop: '4px' }}>
                    {subtitle}
                </p>
            )}
        </div>
    );
}

export default function Dashboard() {
    const [selectedCompany, setSelectedCompany] = useState(null);

    const rockets = MOCK_COMPANIES.filter(c => c.classification === "Rocket");
    const neutrals = MOCK_COMPANIES.filter(c => c.classification === "Neutral");
    const dinosaurs = MOCK_COMPANIES.filter(c => c.classification === "Dinosaur");

    const totalRevenue = MOCK_COMPANIES.reduce((sum, c) => sum + c.revenue, 0);
    const avgGrowth = MOCK_COMPANIES.reduce((sum, c) => sum + c.growth_rate, 0) / MOCK_COMPANIES.length;

    return (
        <div>
            {/* Header */}
            <div className="animate-in" style={{ marginBottom: '32px' }}>
                <h1 style={{ fontSize: '2rem', fontWeight: 700, marginBottom: '8px' }}>
                    <span className="gold-text">Attractiveness Board</span>
                </h1>
                <p style={{ color: 'var(--solstein-text-muted)', fontSize: '0.9rem' }}>
                    European Energy Software — 7 companies scored, classified, and fully explained.
                </p>
            </div>

            {/* KPI Cards */}
            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                gap: '16px',
                marginBottom: '32px',
            }}>
                <StatCard title="Total Companies" value={MOCK_COMPANIES.length} subtitle="Profiled & Scored" delay={1} />
                <StatCard title="Rockets" value={rockets.length} subtitle="High-growth targets" delay={2} />
                <StatCard title="Market Size" value={`€${(totalRevenue / 1000000).toFixed(0)}M`} subtitle="Combined revenue" delay={3} />
                <StatCard title="Avg Growth" value={`${avgGrowth.toFixed(1)}%`} subtitle="Year-over-year" delay={4} />
            </div>

            {/* Attractiveness Board Table */}
            <div className="glass-card animate-in" style={{ padding: '0', overflow: 'hidden', marginBottom: '32px' }}>
                <div style={{
                    padding: '20px 24px',
                    borderBottom: '1px solid var(--solstein-border)',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                }}>
                    <h2 style={{ fontSize: '1rem', fontWeight: 600 }}>Ranked Companies</h2>
                    <span style={{ color: 'var(--solstein-text-muted)', fontSize: '0.75rem' }}>
                        Sorted by Growth Score ↓
                    </span>
                </div>

                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                    <thead>
                        <tr style={{ borderBottom: '1px solid var(--solstein-border)' }}>
                            {['Rank', 'Company', 'Growth', 'Financial', 'Competitive', 'Classification'].map(h => (
                                <th key={h} style={{
                                    padding: '12px 16px',
                                    textAlign: 'left',
                                    color: 'var(--solstein-text-muted)',
                                    fontSize: '0.7rem',
                                    textTransform: 'uppercase',
                                    letterSpacing: '0.1em',
                                    fontWeight: 500,
                                }}>
                                    {h}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {MOCK_COMPANIES
                            .sort((a, b) => b.growth_score - a.growth_score)
                            .map((company, index) => (
                                <tr
                                    key={company.id}
                                    onClick={() => setSelectedCompany(selectedCompany?.id === company.id ? null : company)}
                                    style={{
                                        borderBottom: '1px solid var(--solstein-border)',
                                        cursor: 'pointer',
                                        transition: 'background 0.2s',
                                        background: selectedCompany?.id === company.id ? 'var(--solstein-glow)' : 'transparent',
                                    }}
                                    onMouseEnter={e => e.currentTarget.style.background = 'rgba(212, 168, 67, 0.05)'}
                                    onMouseLeave={e => e.currentTarget.style.background = selectedCompany?.id === company.id ? 'var(--solstein-glow)' : 'transparent'}
                                >
                                    <td style={{ padding: '16px', fontWeight: 600, color: 'var(--solstein-gold)' }}>
                                        #{index + 1}
                                    </td>
                                    <td style={{ padding: '16px' }}>
                                        <div>
                                            <span style={{ fontWeight: 600 }}>{company.name}</span>
                                            <div style={{ fontSize: '0.75rem', color: 'var(--solstein-text-muted)', marginTop: '2px' }}>
                                                {company.headquarters} · {company.tier}
                                            </div>
                                        </div>
                                    </td>
                                    <td style={{ padding: '16px' }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', minWidth: '120px' }}>
                                            <span style={{ fontWeight: 600, fontSize: '0.9rem', minWidth: '28px' }}>{company.growth_score}</span>
                                            <ScoreBar score={company.growth_score} color="linear-gradient(90deg, #2ecc71, #27ae60)" />
                                        </div>
                                    </td>
                                    <td style={{ padding: '16px' }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', minWidth: '120px' }}>
                                            <span style={{ fontWeight: 600, fontSize: '0.9rem', minWidth: '28px' }}>{company.financial_health_score}</span>
                                            <ScoreBar score={company.financial_health_score} color="linear-gradient(90deg, #3498db, #2980b9)" />
                                        </div>
                                    </td>
                                    <td style={{ padding: '16px' }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', minWidth: '120px' }}>
                                            <span style={{ fontWeight: 600, fontSize: '0.9rem', minWidth: '28px' }}>{company.competitive_position_score}</span>
                                            <ScoreBar score={company.competitive_position_score} color="linear-gradient(90deg, #9b59b6, #8e44ad)" />
                                        </div>
                                    </td>
                                    <td style={{ padding: '16px' }}>
                                        <ClassificationBadge classification={company.classification} />
                                    </td>
                                </tr>
                            ))}
                    </tbody>
                </table>
            </div>

            {/* Company Detail Panel */}
            {selectedCompany && (
                <div className="glass-card animate-in" style={{ padding: '24px', marginBottom: '32px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px' }}>
                        <div>
                            <h2 className="gold-text" style={{ fontSize: '1.5rem', fontWeight: 700 }}>{selectedCompany.name}</h2>
                            <p style={{ color: 'var(--solstein-text-muted)', fontSize: '0.85rem' }}>
                                {selectedCompany.headquarters} · {selectedCompany.industry} · {selectedCompany.tier}
                            </p>
                        </div>
                        <ClassificationBadge classification={selectedCompany.classification} />
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '16px' }}>
                        <div style={{ padding: '16px', background: 'var(--solstein-slate)', borderRadius: '12px' }}>
                            <p style={{ color: 'var(--solstein-text-muted)', fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.08em' }}>Revenue</p>
                            <p style={{ fontSize: '1.2rem', fontWeight: 700, marginTop: '4px' }}>€{(selectedCompany.revenue / 1000000).toFixed(1)}M</p>
                        </div>
                        <div style={{ padding: '16px', background: 'var(--solstein-slate)', borderRadius: '12px' }}>
                            <p style={{ color: 'var(--solstein-text-muted)', fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.08em' }}>Growth Rate</p>
                            <p style={{ fontSize: '1.2rem', fontWeight: 700, marginTop: '4px', color: selectedCompany.growth_rate > 0 ? 'var(--solstein-emerald)' : 'var(--solstein-ruby)' }}>
                                {selectedCompany.growth_rate > 0 ? '+' : ''}{selectedCompany.growth_rate}%
                            </p>
                        </div>
                        <div style={{ padding: '16px', background: 'var(--solstein-slate)', borderRadius: '12px' }}>
                            <p style={{ color: 'var(--solstein-text-muted)', fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.08em' }}>Employees</p>
                            <p style={{ fontSize: '1.2rem', fontWeight: 700, marginTop: '4px' }}>{selectedCompany.employees}</p>
                        </div>
                        <div style={{ padding: '16px', background: 'var(--solstein-slate)', borderRadius: '12px' }}>
                            <p style={{ color: 'var(--solstein-text-muted)', fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.08em' }}>AI Maturity</p>
                            <p style={{ fontSize: '1.2rem', fontWeight: 700, marginTop: '4px' }}>{selectedCompany.ai_maturity}</p>
                        </div>
                    </div>

                    {/* Scoring breakdown - transparent reasoning */}
                    <div style={{ marginTop: '20px', padding: '16px', background: 'var(--solstein-slate)', borderRadius: '12px' }}>
                        <p style={{ color: 'var(--solstein-gold)', fontSize: '0.8rem', fontWeight: 600, marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                            ⚗️ Signal Chain — Why This Score
                        </p>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px' }}>
                            <div>
                                <p style={{ fontSize: '0.75rem', color: 'var(--solstein-text-muted)', marginBottom: '6px' }}>Growth Score</p>
                                <p style={{ fontSize: '1.5rem', fontWeight: 700, color: '#2ecc71' }}>{selectedCompany.growth_score}</p>
                                <p style={{ fontSize: '0.7rem', color: 'var(--solstein-text-muted)', marginTop: '4px' }}>
                                    Revenue trajectory ({selectedCompany.growth_rate}% YoY) + Employee efficiency
                                </p>
                            </div>
                            <div>
                                <p style={{ fontSize: '0.75rem', color: 'var(--solstein-text-muted)', marginBottom: '6px' }}>Financial Health</p>
                                <p style={{ fontSize: '1.5rem', fontWeight: 700, color: '#3498db' }}>{selectedCompany.financial_health_score}</p>
                                <p style={{ fontSize: '0.7rem', color: 'var(--solstein-text-muted)', marginTop: '4px' }}>
                                    Revenue scale (€{(selectedCompany.revenue / 1000000).toFixed(0)}M) + Funding cushion
                                </p>
                            </div>
                            <div>
                                <p style={{ fontSize: '0.75rem', color: 'var(--solstein-text-muted)', marginBottom: '6px' }}>Competitive Position</p>
                                <p style={{ fontSize: '1.5rem', fontWeight: 700, color: '#9b59b6' }}>{selectedCompany.competitive_position_score}</p>
                                <p style={{ fontSize: '0.7rem', color: 'var(--solstein-text-muted)', marginTop: '4px' }}>
                                    AI maturity ({selectedCompany.ai_maturity}) + {selectedCompany.tier} positioning
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Classification Distribution */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
                <div className="glass-card animate-in animate-in-delay-1" style={{ padding: '20px', textAlign: 'center' }}>
                    <p style={{ fontSize: '2.5rem', marginBottom: '4px' }}>🚀</p>
                    <p className="gold-text" style={{ fontSize: '2rem', fontWeight: 700 }}>{rockets.length}</p>
                    <p style={{ color: 'var(--solstein-text-muted)', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Rockets</p>
                    <p style={{ color: 'var(--solstein-text-muted)', fontSize: '0.7rem', marginTop: '4px' }}>Act now. High-growth targets.</p>
                </div>
                <div className="glass-card animate-in animate-in-delay-2" style={{ padding: '20px', textAlign: 'center' }}>
                    <p style={{ fontSize: '2.5rem', marginBottom: '4px' }}>⚖️</p>
                    <p className="gold-text" style={{ fontSize: '2rem', fontWeight: 700 }}>{neutrals.length}</p>
                    <p style={{ color: 'var(--solstein-text-muted)', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Neutrals</p>
                    <p style={{ color: 'var(--solstein-text-muted)', fontSize: '0.7rem', marginTop: '4px' }}>Watch for directional signals.</p>
                </div>
                <div className="glass-card animate-in animate-in-delay-3" style={{ padding: '20px', textAlign: 'center' }}>
                    <p style={{ fontSize: '2.5rem', marginBottom: '4px' }}>🦕</p>
                    <p className="gold-text" style={{ fontSize: '2rem', fontWeight: 700 }}>{dinosaurs.length}</p>
                    <p style={{ color: 'var(--solstein-text-muted)', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Dinosaurs</p>
                    <p style={{ color: 'var(--solstein-text-muted)', fontSize: '0.7rem', marginTop: '4px' }}>Assess the people. Hidden diamonds?</p>
                </div>
            </div>
        </div>
    );
}
