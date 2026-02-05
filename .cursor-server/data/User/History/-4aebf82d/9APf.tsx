"use client";

import { useMemo } from "react";

type BarChartProps = {
  data: Array<{ label: string; value: number }>;
  color?: string;
  height?: number;
};

export default function BarChart({ data, color = "#3b82f6", height = 200 }: BarChartProps) {
  const maxValue = useMemo(() => {
    return Math.max(...data.map(d => d.value), 1);
  }, [data]);

  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-slate-400">
        No data available
      </div>
    );
  }

  return (
    <div className="w-full" style={{ height: `${height}px` }}>
      <div className="flex items-end justify-between h-full gap-2">
        {data.map((item, idx) => {
          const percentage = (item.value / maxValue) * 100;
          return (
            <div key={idx} className="flex-1 flex flex-col items-center gap-1">
              <div className="w-full flex flex-col items-center justify-end" style={{ height: "90%" }}>
                <div
                  className="w-full rounded-t transition-all hover:opacity-80"
                  style={{
                    height: `${percentage}%`,
                    backgroundColor: color,
                    minHeight: item.value > 0 ? "4px" : "0",
                  }}
                  title={`${item.label}: ${item.value}`}
                ></div>
              </div>
              <div className="text-xs text-slate-400 text-center truncate w-full" title={item.label}>
                {item.label.length > 8 ? `${item.label.substring(0, 8)}...` : item.label}
              </div>
              <div className="text-xs font-bold" style={{ color }}>
                {item.value}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
