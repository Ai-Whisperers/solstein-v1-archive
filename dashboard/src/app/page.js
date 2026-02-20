"use client";

import { useState, useEffect } from "react";
import { supabase } from "@/lib/supabase";

import { KPICards } from "@/components/KPICards";
import { CompanyTable } from "@/components/CompanyTable";
import { SignalChainPanel } from "@/components/SignalChainPanel";
import { Text } from "@tremor/react";

export default function Dashboard() {
    const [companies, setCompanies] = useState([]);
    const [selectedCompany, setSelectedCompany] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchCompanies() {
            // Fetch 50 records primarily for the initial dashboard render
            const { data, error } = await supabase
                .from("companies")
                .select("*")
                .order("growth_score", { ascending: false })
                .limit(50);

            if (error) {
                console.error("Error fetching companies:", error);
            } else {
                // Hydrate JSONB fields if they are strings. Supabase JS usually parses them automatically.
                setCompanies(data || []);
            }
            setLoading(false);
        }

        fetchCompanies();
    }, []);

    const rockets = companies.filter(c => c.classification === "Rocket");
    const neutrals = companies.filter(c => c.classification === "Neutral");
    const dinosaurs = companies.filter(c => c.classification === "Dinosaur");

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
                            <p style={{ fontSize: "2.5rem", marginBottom: "4px" }}>🚀</p>
                            <p className="gold-text" style={{ fontSize: "2rem", fontWeight: 700 }}>{rockets.length}</p>
                            <p style={{ color: "var(--solstein-text-muted)", fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.1em" }}>Rockets</p>
                            <p style={{ color: "var(--solstein-text-muted)", fontSize: "0.7rem", marginTop: "4px" }}>Act now. High-growth targets.</p>
                        </div>
                        <div className="glass-card animate-in animate-in-delay-2" style={{ padding: "20px", textAlign: "center" }}>
                            <p style={{ fontSize: "2.5rem", marginBottom: "4px" }}>⚖️</p>
                            <p className="gold-text" style={{ fontSize: "2rem", fontWeight: 700 }}>{neutrals.length}</p>
                            <p style={{ color: "var(--solstein-text-muted)", fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.1em" }}>Neutrals</p>
                            <p style={{ color: "var(--solstein-text-muted)", fontSize: "0.7rem", marginTop: "4px" }}>Watch for directional signals.</p>
                        </div>
                        <div className="glass-card animate-in animate-in-delay-3" style={{ padding: "20px", textAlign: "center" }}>
                            <p style={{ fontSize: "2.5rem", marginBottom: "4px" }}>🦕</p>
                            <p className="gold-text" style={{ fontSize: "2rem", fontWeight: 700 }}>{dinosaurs.length}</p>
                            <p style={{ color: "var(--solstein-text-muted)", fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.1em" }}>Dinosaurs</p>
                            <p style={{ color: "var(--solstein-text-muted)", fontSize: "0.7rem", marginTop: "4px" }}>Assess the people. Hidden diamonds?</p>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
}
