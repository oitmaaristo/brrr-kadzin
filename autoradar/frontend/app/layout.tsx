import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Autoradar',
  description: 'Kasutatud autode kuulutuste monitor',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="et">
      <body className="min-h-screen">
        <nav className="border-b border-gray-800 bg-navy/80 backdrop-blur-sm sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <div className="flex items-center gap-8">
                <a href="/" className="font-heading text-xl text-white">
                  auto<span className="text-teal">.</span>radar
                </a>
                <div className="flex gap-6">
                  <a href="/" className="text-gray-300 hover:text-teal transition-colors text-sm font-medium">
                    Dashboard
                  </a>
                  <a href="/filters" className="text-gray-300 hover:text-teal transition-colors text-sm font-medium">
                    Filtrid
                  </a>
                  <a href="/listings" className="text-gray-300 hover:text-teal transition-colors text-sm font-medium">
                    Kuulutused
                  </a>
                </div>
              </div>
              <div id="status-indicator" className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-teal animate-pulse" />
                <span className="text-xs text-gray-400">Jälgib</span>
              </div>
            </div>
          </div>
        </nav>
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>
      </body>
    </html>
  );
}
