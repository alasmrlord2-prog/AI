import type { Metadata } from "next";
import CRMSidebar from "@/components/crm/CRMSidebar";
import CRMHeader from "@/components/crm/CRMHeader";

export const metadata: Metadata = {
  title: "Shiftwave CRM",
  description: "Customer Relationship Management",
};

export default function CRMLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <div className="flex bg-sw-bg h-screen w-screen overflow-hidden">
      <CRMSidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <CRMHeader />
        <main className="flex-1 overflow-y-auto overflow-x-hidden scrollbar-thin">
          {children}
        </main>
      </div>
    </div>
  );
}

