"use client";

import { useState, useEffect } from "react";
import { api } from "@/../lib/api";

import { KPICards } from "@/components/KPICards";
import { CompanyTable } from "@/components/CompanyTable";
import { SignalChainPanel } from "@/components/SignalChainPanel";
import { Text } from "@tremor/react";
import { Company } from "@/types";

export default function Dashboard() {
    const [companies, setCompanies] = useState<Company[]>([]);
    const [selectedCompany, setSelectedCompany] = useState<Company | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        async function fetchCompanies() {
            try {
                setLoading(true);
                const { data } = await api.get('/companies');
                setCompanies(data || []);
                setError(null);
            } catch (err: any) {
                console.error("Aura | Dashboard Fetch Failed:", err);
                setError(err.message || "Failed to consult the Oracle.");
            } finally {
                setLoading(false);
            }
        }

        fetchCompanies();
    }, []);

    const phoenixes = companies.filter(c => c.tier === "Phoenix" || c.classification === "Phoenix");
    const salts = companies.filter(c => c.tier === "Salt" || c.classification === "Salt");
    const leads = companies.filter(c => c.tier === "Lead" || c.classification === "Lead");

    return (
        <div>
            {/* Header */}
            <div className="animate-in" style={{ marginBottom: "32px" }}>
                <h1 style={{ fontSize: "2rem", fontWeight: 700, marginBottom: "8px" }}>
                    <span className="gold-text">Attractiveness Board</span>
                </h1>
                <Text>
                    European Energy Software — dynamically scored, classified, and fully explained by Solstein.
                </Text>
            </div>

            {loading ? (
                <div style={{ textAlign: "center", padding: "64px 0", color: "var(--solstein-gold)" }}>
                    <p className="animate-pulse">Consulting the Oracle...</p>
                </div>
            ) : companies.length === 0 ? (
                <div style={{ textAlign: "center", padding: "64px 0" }}>
                    <p style={{ color: "var(--solstein-text-muted)" }}>No companies found in database.</p>
                    <p style={{ fontSize: "0.8rem", color: "var(--solstein-text-muted)", marginTop: "8px" }}>Run the FastAPI seed script or batch scoring workflow to populate data.</p>
                </div>
            ) : (
                <>
                    <KPICards companies={companies} />

                    <CompanyTable
                        companies={companies}
                        selectedCompany={selectedCompany}
                        onSelect={setSelectedCompany}
                    />

                    <SignalChainPanel selectedCompany={selectedCompany} />

                    {/* Classification Distribution */}
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "16px", marginTop: "32px" }}>
                        <div className="glass-card animate-in animate-in-delay-1" style={{ padding: "20px", textAlign: "center" }}>
                            <p style={{ fontSize: "2.5rem", marginBottom: "4px" }}>🔥</p>
                            <p className="gold-text" style={{ fontSize: "2rem", fontWeight: 700 }}>{phoenixes.length}</p>
                            <p style={{ color: "var(--solstein-text-muted)", fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.1em" }}>Phoenixes</p>
                            <p style={{ color: "var(--solstein-text-muted)", fontSize: "0.7rem", marginTop: "4px" }}>Act now. High-growth targets.</p>
                        </div>
                        <div className="glass-card animate-in animate-in-delay-2" style={{ padding: "20px", textAlign: "center" }}>
                            <p style={{ fontSize: "2.5rem", marginBottom: "4px" }}>🧂</p>
                            <p className="gold-text" style={{ fontSize: "2rem", fontWeight: 700 }}>{salts.length}</p>
                            <p style={{ color: "var(--solstein-text-muted)", fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.1em" }}>Salts</p>
                            <p style={{ color: "var(--solstein-text-muted)", fontSize: "0.7rem", marginTop: "4px" }}>Watch for directional signals.</p>
                        </div>
                        <div className="glass-card animate-in animate-in-delay-3" style={{ padding: "20px", textAlign: "center" }}>
                            <p style={{ fontSize: "2.5rem", marginBottom: "4px" }}>⚖️</p>
                            <p className="gold-text" style={{ fontSize: "2rem", fontWeight: 700 }}>{leads.length}</p>
                            <p style={{ color: "var(--solstein-text-muted)", fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.1em" }}>Leads</p>
                            <p style={{ color: "var(--solstein-text-muted)", fontSize: "0.7rem", marginTop: "4px" }}>Assess the people. Hidden diamonds?</p>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
}
