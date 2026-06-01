// TODO: Implemented by FE-01-02
// Dashboard layout: top nav + collapsible sidebar + main content area
export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return <div className="flex h-screen">{children}</div>;
}
