"use client";

interface PieChartProps {
  data: Array<{ label: string; value: number; color?: string }>;
  size?: number;
  title?: string;
}

export default function PieChart({ data, size = 200, title }: PieChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="h-48 flex items-center justify-center text-slate-400">
        No data available
      </div>
    );
  }

  const total = data.reduce((sum, d) => sum + d.value, 0);
  const center = size / 2;
  const radius = size / 2 - 20;

  let currentAngle = -90;
  const colors = ["#3b82f6", "#ef4444", "#f59e0b", "#10b981", "#8b5cf6", "#ec4899", "#06b6d4"];

  const segments = data.map((d, i) => {
    const percentage = (d.value / total) * 100;
    const angle = (d.value / total) * 360;
    const startAngle = currentAngle;
    const endAngle = currentAngle + angle;
    currentAngle += angle;

    const x1 = center + radius * Math.cos((startAngle * Math.PI) / 180);
    const y1 = center + radius * Math.sin((startAngle * Math.PI) / 180);
    const x2 = center + radius * Math.cos((endAngle * Math.PI) / 180);
    const y2 = center + radius * Math.sin((endAngle * Math.PI) / 180);
    const largeArc = angle > 180 ? 1 : 0;

    const path = `M ${center} ${center} L ${x1} ${y1} A ${radius} ${radius} 0 ${largeArc} 1 ${x2} ${y2} Z`;

    return {
      path,
      percentage,
      label: d.label,
      value: d.value,
      color: d.color || colors[i % colors.length],
      midAngle: startAngle + angle / 2,
    };
  });

  return (
    <div className="w-full">
      {title && <div className="text-sm font-semibold text-slate-300 mb-4">{title}</div>}
      <div className="flex items-center justify-center gap-8">
        <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
          {segments.map((seg, i) => (
            <g key={i}>
              <path
                d={seg.path}
                fill={seg.color}
                className="hover:opacity-80 transition-opacity cursor-pointer"
              />
              <text
                x={center + (radius * 0.7) * Math.cos((seg.midAngle * Math.PI) / 180)}
                y={center + (radius * 0.7) * Math.sin((seg.midAngle * Math.PI) / 180)}
                textAnchor="middle"
                className="text-xs fill-white font-bold"
              >
                {seg.percentage.toFixed(1)}%
              </text>
            </g>
          ))}
        </svg>
        <div className="space-y-2">
          {segments.map((seg, i) => (
            <div key={i} className="flex items-center gap-2">
              <div
                className="w-4 h-4 rounded"
                style={{ backgroundColor: seg.color }}
              />
              <span className="text-sm text-slate-300">{seg.label}</span>
              <span className="text-sm text-slate-400">({seg.value})</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

