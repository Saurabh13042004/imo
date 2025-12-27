import { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { AnalyticsDashboardNew } from '@/components/analytics/AnalyticsDashboardNew';
import { ClarityAnalytics } from '@/components/analytics/ClarityAnalytics';
import { SidebarProvider, SidebarTrigger } from '@/components/ui/sidebar';
import { AdminSidebar } from '@/components/layout/AdminSidebar';
import { BarChart3, LineChart as LineChartIcon } from 'lucide-react';

export default function AdminDashboard() {
  const [activeTab, setActiveTab] = useState('overview');

  return (
    <SidebarProvider>
      <div className="min-h-screen flex w-full">
        <AdminSidebar />
        
        <div className="flex-1 flex flex-col">
          {/* Header with trigger */}
          <header className="h-16 flex items-center justify-between border-b bg-card px-6">
            <div className="flex items-center gap-4">
              <SidebarTrigger />
              <div>
                <h1 className="text-2xl font-bold tracking-tight">Analytics Dashboard</h1>
                <p className="text-sm text-muted-foreground">Real-time insights and metrics</p>
              </div>
            </div>
          </header>

          {/* Main Content */}
          <main className="flex-1 p-6 bg-gradient-to-br from-background via-background to-muted/20 overflow-auto">
            <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
              <TabsList className="grid w-full grid-cols-2 lg:w-auto">
                <TabsTrigger value="overview" className="flex items-center gap-2">
                  <LineChartIcon className="w-4 h-4" />
                  <span className="hidden sm:inline">Daily Analytics</span>
                  <span className="sm:hidden">Daily</span>
                </TabsTrigger>
                <TabsTrigger value="clarity" className="flex items-center gap-2">
                  <BarChart3 className="w-4 h-4" />
                  <span className="hidden sm:inline">Clarity Insights</span>
                  <span className="sm:hidden">Clarity</span>
                </TabsTrigger>
              </TabsList>

              <TabsContent value="overview" className="space-y-6">
                <AnalyticsDashboardNew />
              </TabsContent>

              <TabsContent value="clarity" className="space-y-6">
                <ClarityAnalytics />
              </TabsContent>
            </Tabs>
          </main>
        </div>
      </div>
    </SidebarProvider>
  );
}