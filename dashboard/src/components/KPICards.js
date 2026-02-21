import { Card, Metric, Text } from "@tremor/react";

export function KPICards({ companies }) {
    const phoenixes = companies.filter((c) => c.classification === "Phoenix");
    const totalRevenue = companies.reduce((sum, c) => sum + (c.revenue || 0), 0);
    const avgGrowth =
        companies.length > 0
            ? companies.reduce((sum, c) => sum + (c.growth_rate || 0), 0) / companies.length
            : 0;

    return (
        <div
            style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
                gap: "16px",
                marginBottom: "32px",
            }}
        >
            <Card decoration="top" decorationColor="blue" className="glass-card !bg-transparent !ring-solstein-border">
                <Text className="!text-solstein-text-muted uppercase tracking-widest text-xs">Total Companies</Text>
                <Metric className="!text-solstein-gold">{companies.length}</Metric>
                <Text className="!text-solstein-text-muted text-xs mt-1">Profiled & Scored</Text>
            </Card>

            <Card decoration="top" decorationColor="amber" className="glass-card !bg-transparent !ring-solstein-border">
                <Text className="!text-solstein-text-muted uppercase tracking-widest text-xs">Phoenixes</Text>
                <Metric className="!text-solstein-gold">{phoenixes.length}</Metric>
                <Text className="!text-solstein-text-muted text-xs mt-1">High-growth targets</Text>
            </Card>

            <Card decoration="top" decorationColor="blue" className="glass-card !bg-transparent !ring-solstein-border">
                <Text className="!text-solstein-text-muted uppercase tracking-widest text-xs">Market Size</Text>
                <Metric className="!text-solstein-gold">€{(totalRevenue / 1000000).toFixed(0)}M</Metric>
                <Text className="!text-solstein-text-muted text-xs mt-1">Combined revenue</Text>
            </Card>

            <Card decoration="top" decorationColor="purple" className="glass-card !bg-transparent !ring-solstein-border">
                <Text className="!text-solstein-text-muted uppercase tracking-widest text-xs">Avg Growth</Text>
                <Metric className="!text-solstein-gold">{avgGrowth.toFixed(1)}%</Metric>
                <Text className="!text-solstein-text-muted text-xs mt-1">Year-over-year</Text>
            </Card>
        </div>
    );
}
