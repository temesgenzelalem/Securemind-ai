import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SecureMind AI | Web Application Security & Remediation",
  description: "Agentic AI-powered Web Application Security Analysis and Remediation Platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="bg-slate-950 text-slate-100 antialiased min-h-screen">
        {children}
      </body>
    </html>
  );
}
