import { ClassificationBadge } from "./ClassificationBadge";
import { Company } from "@/types";

export function ScoreBar({ score, maxScore = 10, color }: { score: number; maxScore?: number; color?: string }) {
    const percentage = (score / maxScore) * 100;
    return (
        <div className="score-bar" style={{ width: "100%" }}>
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

export function CompanyTable({
    companies,
    selectedCompany,
    onSelect,
}: {
    companies: Company[];
    selectedCompany: Company | null;
    onSelect: (company: Company | null) => void;
}) {
    return (
        <div className="glass-card animate-in overflow-x-auto" style={{ padding: "0", marginBottom: "32px" }}>
            <div
                style={{
                    padding: "20px 24px",
                    borderBottom: "1px solid var(--solstein-border)",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                }}
            >
                <h2 style={{ fontSize: "1rem", fontWeight: 600 }}>Ranked Companies</h2>
                <span style={{ color: "var(--solstein-text-muted)", fontSize: "0.75rem" }}>
                    Sorted by Growth Score ↓
                </span>
            </div>

            <table style={{ width: "100%", borderCollapse: "collapse", minWidth: "800px" }}>
                <thead>
                    <tr style={{ borderBottom: "1px solid var(--solstein-border)" }}>
                        {["Rank", "Company", "Growth", "Financial", "Competitive", "Classification"].map((h) => (
                            <th
                                key={h}
                                style={{
                                    padding: "12px 16px",
                                    textAlign: "left",
                                    color: "var(--solstein-text-muted)",
                                    fontSize: "0.7rem",
                                    textTransform: "uppercase",
                                    letterSpacing: "0.1em",
                                    fontWeight: 500,
                                }}
                            >
                                {h}
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {[...companies]
                        .sort((a, b) => (b.growth_score || 0) - (a.growth_score || 0))
                        .map((company, index) => (
                            <tr
                                key={company.id}
                                onClick={() => onSelect(selectedCompany?.id === company.id ? null : company)}
                                style={{
                                    borderBottom: "1px solid var(--solstein-border)",
                                    cursor: "pointer",
                                    transition: "background 0.2s",
                                    background: selectedCompany?.id === company.id ? "var(--solstein-glow)" : "transparent",
                                }}
                                onMouseEnter={(e) => (e.currentTarget.style.background = "rgba(212, 168, 67, 0.05)")}
                                onMouseLeave={(e) =>
                                (e.currentTarget.style.background =
                                    selectedCompany?.id === company.id ? "var(--solstein-glow)" : "transparent")
                                }
                            >
                                <td style={{ padding: "16px", fontWeight: 600, color: "var(--solstein-gold)" }}>
                                    #{index + 1}
                                </td>
                                <td style={{ padding: "16px" }}>
                                    <div>
                                        <span style={{ fontWeight: 600 }}>{company.name}</span>
                                        <div style={{ fontSize: "0.75rem", color: "var(--solstein-text-muted)", marginTop: "2px" }}>
                                            {company.headquarters || "Unknown"} · {company.tier}
                                        </div>
                                    </div>
                                </td>
                                <td style={{ padding: "16px" }}>
                                    <div style={{ display: "flex", alignItems: "center", gap: "8px", minWidth: "120px" }}>
                                        <span style={{ fontWeight: 600, fontSize: "0.9rem", minWidth: "32px" }}>
                                            {company.growth_score?.toFixed(1) || "N/A"}
                                        </span>
                                        <ScoreBar score={company.growth_score || 0} color="linear-gradient(90deg, #2ecc71, #27ae60)" />
                                    </div>
                                </td>
                                <td style={{ padding: "16px" }}>
                                    <div style={{ display: "flex", alignItems: "center", gap: "8px", minWidth: "120px" }}>
                                        <span style={{ fontWeight: 600, fontSize: "0.9rem", minWidth: "32px" }}>
                                            {company.financial_health_score?.toFixed(1) || "N/A"}
                                        </span>
                                        <ScoreBar score={company.financial_health_score || 0} color="linear-gradient(90deg, #3498db, #2980b9)" />
                                    </div>
                                </td>
                                <td style={{ padding: "16px" }}>
                                    <div style={{ display: "flex", alignItems: "center", gap: "8px", minWidth: "120px" }}>
                                        <span style={{ fontWeight: 600, fontSize: "0.9rem", minWidth: "32px" }}>
                                            {company.competitive_position_score?.toFixed(1) || "N/A"}
                                        </span>
                                        <ScoreBar score={company.competitive_position_score || 0} color="linear-gradient(90deg, #9b59b6, #8e44ad)" />
                                    </div>
                                </td>
                                <td style={{ padding: "16px" }}>
                                    <ClassificationBadge classification={company.classification || "Salt"} />
                                </td>
                            </tr>
                        ))}
                </tbody>
            </table>
        </div>
    );
}
