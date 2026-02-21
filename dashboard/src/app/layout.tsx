import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
    subsets: ["latin"],
    variable: "--font-inter",
});

export const metadata = {
    title: "Solstein — The Sunstone for Capital Navigation",
    description: "AI-Powered Competitive Intelligence Platform for PE/VC. See through the market fog.",
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en" className={inter.variable}>
            <body className="grid-bg min-h-screen">
                {/* Top navigation bar */}
                <nav style={{
                    position: 'sticky',
                    top: 0,
                    zIndex: 50,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '16px 32px',
                    borderBottom: '1px solid var(--solstein-border)',
                    background: 'var(--solstein-glass)',
                    backdropFilter: 'blur(16px)',
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <span style={{
                            fontSize: '1.5rem',
                            fontWeight: 700,
                        }} className="gold-text">𝔖𝔬𝔩𝔰𝔱𝔢𝔦𝔫</span>
                        <span style={{
                            fontSize: '0.75rem',
                            color: 'var(--solstein-text-muted)',
                            letterSpacing: '0.15em',
                            textTransform: 'uppercase',
                        }}>Intelligence Engine</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
                        <a href="/" style={{
                            color: 'var(--solstein-gold)',
                            textDecoration: 'none',
                            fontSize: '0.875rem',
                            fontWeight: 500,
                        }}>Dashboard</a>
                        <a href="/companies" style={{
                            color: 'var(--solstein-text-muted)',
                            textDecoration: 'none',
                            fontSize: '0.875rem',
                        }}>Companies</a>
                        <a href="/market" style={{
                            color: 'var(--solstein-text-muted)',
                            textDecoration: 'none',
                            fontSize: '0.875rem',
                        }}>Market Analysis</a>
                    </div>
                </nav>
                <main style={{ padding: '32px', maxWidth: '1440px', margin: '0 auto', width: '100%' }}>
                    {children}
                </main>
            </body>
        </html>
    );
}
