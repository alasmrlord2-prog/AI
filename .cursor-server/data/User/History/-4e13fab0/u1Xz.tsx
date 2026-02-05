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
    <div className="flex bg-sw-bg min-h-screen">
      <CRMSidebar />
      <main className="flex-1 p-8">
        {children}
      </main>
    </div>
  );
}

