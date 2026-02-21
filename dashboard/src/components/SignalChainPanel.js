import { Badge } from "@tremor/react";
import ReactECharts from "echarts-for-react";
import { ClassificationBadge } from "./ClassificationBadge";
import { useState, useEffect } from "react";
import { api } from "@/../lib/api";

export function SignalChainPanel({ selectedCompany }) {
    const [auditTrail, setAuditTrail] = useState(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (!selectedCompany) {
            setAuditTrail(null);
            return;
        }

        async function fetchAuditTrail() {
            try {
                setLoading(true);
                const companyId = selectedCompany.id || selectedCompany.company_id || selectedCompany.name.toLowerCase().replace(/ /g, '-');
                const { data } = await api.get(`/drill-down/company/${companyId}/audit-trail`);
                setAuditTrail(data);
            } catch (err) {
                console.error("Aura | Audit Trail Fetch Failed:", err);
                setAuditTrail(null);
            } finally {
                setLoading(false);
            }
        }

        fetchAuditTrail();
    }, [selectedCompany]);

    if (!selectedCompany) return null;

    // Use audit trail data if available, fallback to selectedCompany
    const displayData = auditTrail || {
        ...selectedCompany,
        extracted_signals: selectedCompany.extracted_signals || [],
    };

    // Radar chart configuration for complete visual transparency
    const radarOption = {
        radar: {
            indicator: [
                { name: "Growth Rate", max: 10 },
                { name: "Financial Health", max: 10 },
                { name: "Competitive Pos.", max: 10 },
            ],
            shape: "polygon",
            axisName: { color: "var(--solstein-text-muted)" },
            splitLine: { lineStyle: { color: "var(--solstein-border)" } },
            splitArea: { show: false },
            axisLine: { lineStyle: { color: "var(--solstein-border)" } },
        },
        series: [
            {
                name: "Company Scores",
                type: "radar",
                data: [
                    {
                        value: [
                            selectedCompany.growth_score || 0,
                            selectedCompany.financial_health_score || 0,
                            selectedCompany.competitive_position_score || 0,
                        ],
                        name: selectedCompany.name,
                        itemStyle: { color: "var(--solstein-gold)" },
                        areaStyle: { color: "var(--solstein-glow)" },
                    },
                ],
            },
        ],
    };

    return (
        <div className="glass-card animate-in" style={{ padding: "24px", marginBottom: "32px", marginTop: "32px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "20px" }}>
                <div>
                    <h2 className="gold-text" style={{ fontSize: "1.5rem", fontWeight: 700 }}>
                        {selectedCompany.name}
                    </h2>
                    <p style={{ color: "var(--solstein-text-muted)", fontSize: "0.85rem" }}>
                        {selectedCompany.headquarters || "Unknown"} · {selectedCompany.industry} · {selectedCompany.tier}
                    </p>
                </div>
                <ClassificationBadge classification={selectedCompany.classification || selectedCompany.tier || "Salt"} />
            </div>

            {loading ? (
                <div style={{ textAlign: "center", padding: "32px", color: "var(--solstein-gold)" }}>
                    <p className="animate-pulse">Analyzing Signal Chain...</p>
                </div>
            ) : (
                <>
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "16px" }}>
                        <div style={{ padding: "16px", background: "var(--solstein-slate)", borderRadius: "12px" }}>
                            <p style={{ color: "var(--solstein-text-muted)", fontSize: "0.7rem", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                                Revenue
                            </p>
                            <p style={{ fontSize: "1.2rem", fontWeight: 700, marginTop: "4px" }}>
                                €{((selectedCompany.revenue || selectedCompany.financials?.revenue || 0) / 1000000).toFixed(1)}M
                            </p>
                        </div>
                        <div style={{ padding: "16px", background: "var(--solstein-slate)", borderRadius: "12px" }}>
                            <p style={{ color: "var(--solstein-text-muted)", fontSize: "0.7rem", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                                Growth Rate
                            </p>
                            <p
                                style={{
                                    fontSize: "1.2rem",
                                    fontWeight: 700,
                                    marginTop: "4px",
                                    color: (selectedCompany.growth_rate || selectedCompany.financials?.growth_rate || 0) > 0 ? "var(--solstein-emerald)" : "var(--solstein-ruby)",
                                }}
                            >
                                {(selectedCompany.growth_rate || selectedCompany.financials?.growth_rate || 0) > 0 ? "+" : ""}
                                {selectedCompany.growth_rate || selectedCompany.financials?.growth_rate || 0}%
                            </p>
                        </div>
                        <div style={{ padding: "16px", background: "var(--solstein-slate)", borderRadius: "12px" }}>
                            <p style={{ color: "var(--solstein-text-muted)", fontSize: "0.7rem", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                                Employees
                            </p>
                            <p style={{ fontSize: "1.2rem", fontWeight: 700, marginTop: "4px" }}>
                                {selectedCompany.employees || selectedCompany.financials?.employees || "N/A"}
                            </p>
                        </div>
                        <div style={{ padding: "16px", background: "var(--solstein-slate)", borderRadius: "12px" }}>
                            <p style={{ color: "var(--solstein-text-muted)", fontSize: "0.7rem", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                                Oracle Confidence
                            </p>
                            <p style={{ fontSize: "1.2rem", fontWeight: 700, marginTop: "4px" }}>
                                {displayData.confidence_level || "N/A"}
                            </p>
                        </div>
                    </div>

                    {/* Grid for Reasoning + Radar Chart */}
                    <div style={{ display: "grid", gridTemplateColumns: "1.5fr 1fr", gap: "24px", marginTop: "24px" }}>

                        {/* Scoring breakdown - transparent reasoning */}
                        <div style={{ padding: "20px", background: "var(--solstein-slate)", borderRadius: "12px" }}>
                            <p style={{ color: "var(--solstein-gold)", fontSize: "0.8rem", fontWeight: 600, marginBottom: "16px", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                                ⚗️ Signal Chain — Why This Score
                            </p>
                            <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
                                {displayData.extracted_signals?.length > 0 ? (
                                    displayData.extracted_signals.map((signal, idx) => (
                                        <div key={idx}>
                                            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "4px" }}>
                                                <p style={{ fontSize: "0.75rem", color: "var(--solstein-text-muted)" }}>{signal.signal_name}</p>
                                                <p style={{ fontSize: "1.1rem", fontWeight: 700, color: "var(--solstein-gold)" }}>
                                                    {signal.signal_value}
                                                </p>
                                            </div>
                                            <p style={{ fontSize: "0.7rem", color: "var(--solstein-text-muted)" }}>
                                                Evidence: {signal.source_facts.join(", ")} | Method: {signal.calculation_method}
                                            </p>
                                            {idx < displayData.extracted_signals.length - 1 && (
                                                <div style={{ height: "1px", background: "var(--solstein-border)", marginTop: "12px" }} />
                                            )}
                                        </div>
                                    ))
                                ) : (
                                    <p style={{ fontSize: "0.8rem", color: "var(--solstein-text-muted)" }}>
                                        No deep signals parsed yet. Run the analysis workflow for full transparency.
                                    </p>
                                )}
                            </div>
                        </div>

                        {/* ECharts Radar Visualization */}
                        <div style={{ padding: "16px", background: "var(--solstein-slate)", borderRadius: "12px", display: "flex", flexDirection: "column" }}>
                            <p style={{ color: "var(--solstein-text-muted)", fontSize: "0.7rem", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "auto" }}>
                                Performance Radar
                            </p>
                            <div style={{ height: "250px", width: "100%" }}>
                                <ReactECharts option={radarOption} style={{ height: "100%", width: "100%" }} />
                            </div>
                        </div>

                    </div>
                </>
            )}
        </div>
    );
}
