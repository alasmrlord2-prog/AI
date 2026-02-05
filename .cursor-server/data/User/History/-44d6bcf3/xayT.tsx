import type { Metadata } from "next";
import AAASidebar from "@/components/aaa/AAASidebar";
import AAAHeader from "@/components/aaa/AAAHeader";

export const metadata: Metadata = {
  title: "Shiftwave AAA",
  description: "Authentication, Authorization, and Accounting",
};

export default function AAALayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <div className="flex bg-swAuth-bg min-h-screen w-screen overflow-hidden">
      <AAASidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <AAAHeader />
        <main className="flex-1 overflow-y-auto overflow-x-hidden scrollbar-thin">
          {children}
        </main>
      </div>
    </div>
  );
}

