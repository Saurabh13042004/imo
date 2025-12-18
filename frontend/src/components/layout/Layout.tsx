import { ReactNode } from 'react';
import { SearchHeader } from '@/components/search/SearchHeader';
import { Footer } from '@/components/layout/Footer';

interface LayoutProps {
  children: ReactNode;
}

export const Layout = ({ children }: LayoutProps) => {
  return (
    <div className="flex flex-col min-h-screen">
      <SearchHeader />
      <main className="flex-1">
        {children}
      </main>
      <Footer />
    </div>
  );
};
