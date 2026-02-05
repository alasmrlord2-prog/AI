"use client";

interface BarChartProps {
  data: Array<{ label: string; value: number }>;
  color?: string;
  height?: number;
  title?: string;
}

export default function BarChart({ data, color = "#3b82f6", height = 200, title }: BarChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="h-48 flex items-center justify-center text-slate-400">
        No data available
      </div>
    );
  }

  const maxValue = Math.max(...data.map(d => d.value), 1);
  const padding = 40;
  const chartWidth = 600;
  const chartHeight = height - padding * 2;
  const barWidth = (chartWidth - padding * 2) / data.length - 10;

  return (
    <div className="w-full">
      {title && <div className="text-sm font-semibold text-slate-300 mb-2">{title}</div>}
      <svg width="100%" height={height} viewBox={`0 0 ${chartWidth} ${height}`} className="overflow-visible">
        {/* Grid lines */}
        {[0, 0.25, 0.5, 0.75, 1].map((ratio) => {
          const y = padding + chartHeight - ratio * chartHeight;
          return (
            <line
              key={ratio}
              x1={padding}
              y1={y}
              x2={chartWidth - padding}
              y2={y}
              stroke="#334155"
              strokeWidth="1"
              strokeDasharray="4 4"
            />
          );
        })}

        {/* Bars */}
        {data.map((d, i) => {
          const barHeight = (d.value / maxValue) * chartHeight;
          const x = padding + i * (barWidth + 10) + 5;
          const y = padding + chartHeight - barHeight;

          return (
            <g key={i}>
              <rect
                x={x}
                y={y}
                width={barWidth}
                height={barHeight}
                fill={color}
                fillOpacity="0.8"
                className="hover:opacity-100 transition-opacity"
              />
              <text
                x={x + barWidth / 2}
                y={y - 5}
                textAnchor="middle"
                className="text-xs fill-slate-300"
              >
                {d.value}
              </text>
              <text
                x={x + barWidth / 2}
                y={height - 10}
                textAnchor="middle"
                className="text-xs fill-slate-400"
                transform={`rotate(-45 ${x + barWidth / 2} ${height - 10})`}
              >
                {d.label.length > 10 ? d.label.substring(0, 10) + "..." : d.label}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}

