"use client";

interface LineChartProps {
  data: Array<{ label: string; value: number }>;
  color?: string;
  height?: number;
  title?: string;
}

export default function LineChart({ data, color = "#3b82f6", height = 200, title }: LineChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="h-48 flex items-center justify-center text-slate-400">
        No data available
      </div>
    );
  }

  // Filter out invalid values
  const validData = data.filter(d => typeof d.value === 'number' && !isNaN(d.value) && isFinite(d.value));
  
  if (validData.length === 0) {
    return (
      <div className="h-48 flex items-center justify-center text-slate-400">
        No valid data available
      </div>
    );
  }

  const maxValue = Math.max(...validData.map(d => d.value), 1);
  const minValue = Math.min(...validData.map(d => d.value), 0);
  const range = maxValue - minValue || 1;
  const padding = 40;
  const chartWidth = 600;
  const chartHeight = height - padding * 2;
  const pointRadius = 4;

  const points = validData.map((d, i) => {
    const value = typeof d.value === 'number' && !isNaN(d.value) ? d.value : 0;
    const x = padding + (i / (validData.length - 1 || 1)) * (chartWidth - padding * 2);
    const y = padding + chartHeight - ((value - minValue) / range) * chartHeight;
    return { 
      x: isNaN(x) ? padding : x, 
      y: isNaN(y) ? padding + chartHeight : y, 
      label: d.label || '', 
      value: value 
    };
  });

  const pathData = points
    .map((p, i) => `${i === 0 ? "M" : "L"} ${p.x} ${p.y}`)
    .join(" ");

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

        {/* Line */}
        <path
          d={pathData}
          fill="none"
          stroke={color}
          strokeWidth="2"
          className="drop-shadow-lg"
        />

        {/* Area under line */}
        <path
          d={`${pathData} L ${points[points.length - 1].x} ${padding + chartHeight} L ${points[0].x} ${padding + chartHeight} Z`}
          fill={color}
          fillOpacity="0.1"
        />

        {/* Points */}
        {points.map((point, i) => (
          <g key={i}>
            <circle
              cx={point.x}
              cy={point.y}
              r={pointRadius}
              fill={color}
              stroke="#1e293b"
              strokeWidth="2"
              className="hover:r-6 transition-all"
            />
            <text
              x={point.x}
              y={point.y - 10}
              textAnchor="middle"
              className="text-xs fill-slate-400"
            >
              {point.value}
            </text>
          </g>
        ))}

        {/* X-axis labels */}
        {points.map((point, i) => (
          i % Math.ceil(points.length / 6) === 0 && (
            <text
              key={i}
              x={point.x}
              y={height - 10}
              textAnchor="middle"
              className="text-xs fill-slate-400"
            >
              {point.label}
            </text>
          )
        ))}
      </svg>
    </div>
  );
}

