"use client";

import { useMemo } from "react";

type PieChartProps = {
  data: Array<{ label: string; value: number; color?: string }>;
  size?: number;
};

export default function PieChart({ data, size = 200 }: PieChartProps) {
  const total = useMemo(() => {
    return data.reduce((sum, item) => sum + item.value, 0);
  }, [data]);

  const segments = useMemo(() => {
    if (total === 0) return [];
    
    let currentAngle = -90; // Start from top
    return data.map((item) => {
      const percentage = (item.value / total) * 100;
      const angle = (percentage / 100) * 360;
      const startAngle = currentAngle;
      const endAngle = currentAngle + angle;
      currentAngle = endAngle;

      // Calculate path for SVG arc
      const radius = size / 2 - 10;
      const startRad = (startAngle * Math.PI) / 180;
      const endRad = (endAngle * Math.PI) / 180;
      
      const x1 = size / 2 + radius * Math.cos(startRad);
      const y1 = size / 2 + radius * Math.sin(startRad);
      const x2 = size / 2 + radius * Math.cos(endRad);
      const y2 = size / 2 + radius * Math.sin(endRad);
      
      const largeArcFlag = angle > 180 ? 1 : 0;
      
      const pathData = [
        `M ${size / 2} ${size / 2}`,
        `L ${x1} ${y1}`,
        `A ${radius} ${radius} 0 ${largeArcFlag} 1 ${x2} ${y2}`,
        "Z",
      ].join(" ");

      return {
        ...item,
        pathData,
        percentage: percentage.toFixed(1),
        startAngle,
        endAngle,
      };
    });
  }, [data, total, size]);

  if (!data || data.length === 0 || total === 0) {
    return (
      <div className="flex items-center justify-center h-full text-sw-text-muted">
        No data available
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center gap-4">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="transform -rotate-90">
          {segments.map((segment, idx) => (
            <path
              key={idx}
              d={segment.pathData}
              fill={segment.color || "var(--sw-blue)"}
              stroke="var(--sw-border)"
              strokeWidth="2"
              className="transition-all hover:opacity-80"
              style={{ opacity: 0.9 }}
            />
          ))}
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <div className="text-2xl font-bold text-sw-text-strong">{total}</div>
            <div className="text-xs text-sw-text-muted">Total</div>
          </div>
        </div>
      </div>
      
      {/* Legend */}
      <div className="grid grid-cols-2 gap-2 w-full">
        {segments.map((segment, idx) => (
          <div key={idx} className="flex items-center gap-2">
            <div
              className="w-4 h-4 rounded"
              style={{ backgroundColor: segment.color || "var(--sw-blue)" }}
            ></div>
            <div className="flex-1">
              <div className="text-xs text-sw-text-soft">{segment.label}</div>
              <div className="text-xs text-sw-text-muted">
                {segment.value} ({segment.percentage}%)
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
