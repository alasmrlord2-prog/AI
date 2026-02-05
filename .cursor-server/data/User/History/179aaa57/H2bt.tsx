"use client";

import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";

type Alert = {
  id: string;
  type: "critical" | "high" | "medium" | "low" | "info";
  title: string;
  message: string;
  timestamp: string;
  source?: string;
  read: boolean;
};

interface AlertNotificationProps {
  alerts: Alert[];
  onDismiss?: (id: string) => void;
  onMarkRead?: (id: string) => void;
}

export default function AlertNotification({ alerts, onDismiss, onMarkRead }: AlertNotificationProps) {
  const [visibleAlerts, setVisibleAlerts] = useState<Alert[]>([]);

  useEffect(() => {
    // Show only unread alerts
    const unread = alerts.filter(a => !a.read).slice(0, 5);
    setVisibleAlerts(unread);
  }, [alerts]);

  const getAlertColor = (type: string) => {
    switch (type) {
      case "critical": return "bg-red-900/30 border-red-700 text-red-400";
      case "high": return "bg-orange-900/30 border-orange-700 text-orange-400";
      case "medium": return "bg-yellow-900/30 border-yellow-700 text-yellow-400";
      case "low": return "bg-blue-900/30 border-blue-700 text-blue-400";
      default: return "bg-slate-900/30 border-slate-700 text-slate-400";
    }
  };

  const getAlertIcon = (type: string) => {
    switch (type) {
      case "critical": return "🚨";
      case "high": return "⚠️";
      case "medium": return "⚡";
      case "low": return "ℹ️";
      default: return "📢";
    }
  };

  if (visibleAlerts.length === 0) {
    return null;
  }

  return (
    <div className="fixed top-20 right-4 z-50 space-y-2 max-w-md">
      {visibleAlerts.map((alert) => (
        <Card
          key={alert.id}
          className={`p-4 border-l-4 animate-slide-in ${getAlertColor(alert.type)}`}
        >
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xl">{getAlertIcon(alert.type)}</span>
                <span className="font-bold text-sm">{alert.title}</span>
              </div>
              <p className="text-xs text-slate-300 mb-2">{alert.message}</p>
              <div className="flex items-center gap-2">
                {alert.source && (
                  <span className="text-xs text-slate-400">Source: {alert.source}</span>
                )}
                <span className="text-xs text-slate-400">
                  {new Date(alert.timestamp).toLocaleTimeString()}
                </span>
              </div>
            </div>
            <div className="flex gap-1 ml-2">
              {onMarkRead && (
                <button
                  onClick={() => onMarkRead(alert.id)}
                  className="text-xs px-2 py-1 bg-slate-700 hover:bg-slate-600 rounded"
                >
                  ✓
                </button>
              )}
              {onDismiss && (
                <button
                  onClick={() => onDismiss(alert.id)}
                  className="text-xs px-2 py-1 bg-slate-700 hover:bg-slate-600 rounded"
                >
                  ×
                </button>
              )}
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
}

