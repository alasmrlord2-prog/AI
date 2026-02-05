"use client";

import { useState, useEffect } from "react";
import { X, Check, AlertCircle, AlertTriangle, Info, Bell } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

type Alert = {
  id: string;
  type: "critical" | "high" | "medium" | "low" | "info";
  title: string;
  message: string;
  timestamp: string;
  source?: string;
  read: boolean;
};

type AlertNotificationProps = {
  alerts: Alert[];
  onDismiss: (id: string) => void;
  onMarkRead: (id: string) => void;
};

export default function AlertNotification({
  alerts,
  onDismiss,
  onMarkRead,
}: AlertNotificationProps) {
  const [isOpen, setIsOpen] = useState(true);
  const [position, setPosition] = useState<"top-right" | "bottom-right">("top-right");

  const unreadCount = alerts.filter(a => !a.read).length;
  const criticalAlerts = alerts.filter(a => a.type === "critical" && !a.read);

  const getAlertIcon = (type: string) => {
    switch (type) {
      case "critical":
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      case "high":
        return <AlertTriangle className="h-5 w-5 text-orange-500" />;
      case "medium":
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
      case "low":
        return <Info className="h-5 w-5 text-blue-500" />;
      default:
        return <Bell className="h-5 w-5 text-slate-400" />;
    }
  };

  const getAlertColor = (type: string) => {
    switch (type) {
      case "critical":
        return "bg-red-900/30 border-red-700 text-red-300";
      case "high":
        return "bg-orange-900/30 border-orange-700 text-orange-300";
      case "medium":
        return "bg-yellow-900/30 border-yellow-700 text-yellow-300";
      case "low":
        return "bg-blue-900/30 border-blue-700 text-blue-300";
      default:
        return "bg-slate-900/30 border-slate-700 text-slate-300";
    }
  };

  if (alerts.length === 0) {
    return null;
  }

  return (
    <div
      className={`fixed ${position === "top-right" ? "top-4 right-4" : "bottom-4 right-4"} z-50 w-96 max-w-[calc(100vw-2rem)]`}
    >
      {/* Alert Panel Toggle */}
      <div className="mb-2 flex items-center justify-end">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="flex items-center gap-2 px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg hover:bg-slate-800 transition-colors"
        >
          <Bell className="h-4 w-4 text-slate-300" />
          <span className="text-sm text-slate-300">Alerts</span>
          {unreadCount > 0 && (
            <span className="px-2 py-0.5 bg-red-600 text-white text-xs font-bold rounded-full">
              {unreadCount}
            </span>
          )}
        </button>
      </div>

      {/* Alert Panel */}
      {isOpen && (
        <Card className="bg-slate-900 border-slate-800 shadow-2xl max-h-[600px] overflow-hidden flex flex-col">
          <CardContent className="p-0">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-slate-700">
              <div className="flex items-center gap-2">
                <Bell className="h-5 w-5 text-slate-300" />
                <h3 className="text-lg font-semibold text-slate-200">Security Alerts</h3>
                {unreadCount > 0 && (
                  <span className="px-2 py-0.5 bg-red-600 text-white text-xs font-bold rounded-full">
                    {unreadCount} new
                  </span>
                )}
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="text-slate-400 hover:text-slate-200 transition-colors"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Alerts List */}
            <div className="overflow-y-auto max-h-[500px]">
              {alerts.length === 0 ? (
                <div className="p-8 text-center text-slate-400">
                  <Bell className="h-12 w-12 mx-auto mb-2 opacity-50" />
                  <p>No alerts</p>
                </div>
              ) : (
                <div className="divide-y divide-slate-800">
                  {alerts.map((alert, index) => (
                    <div
                      key={`${alert.id}-${index}`}
                      className={`p-4 border-l-4 transition-all ${
                        alert.read
                          ? "bg-slate-800/50 border-slate-700 opacity-60"
                          : getAlertColor(alert.type)
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        <div className="mt-0.5">{getAlertIcon(alert.type)}</div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-start justify-between gap-2 mb-1">
                            <h4 className="font-semibold text-sm">{alert.title}</h4>
                            {!alert.read && (
                              <span className="px-1.5 py-0.5 bg-red-600 text-white text-xs rounded-full flex-shrink-0">
                                NEW
                              </span>
                            )}
                          </div>
                          <p className="text-xs text-slate-300 mb-2 line-clamp-2">
                            {alert.message}
                          </p>
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2 text-xs text-slate-400">
                              {alert.source && (
                                <span className="capitalize">{alert.source}</span>
                              )}
                              <span>•</span>
                              <span>
                                {new Date(alert.timestamp).toLocaleTimeString()}
                              </span>
                            </div>
                            <div className="flex items-center gap-1">
                              {!alert.read && (
                                <button
                                  onClick={() => onMarkRead(alert.id)}
                                  className="p-1 text-slate-400 hover:text-green-400 transition-colors"
                                  title="Mark as read"
                                >
                                  <Check className="h-4 w-4" />
                                </button>
                              )}
                              <button
                                onClick={() => onDismiss(alert.id)}
                                className="p-1 text-slate-400 hover:text-red-400 transition-colors"
                                title="Dismiss"
                              >
                                <X className="h-4 w-4" />
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Footer Actions */}
            {alerts.length > 0 && (
              <div className="p-3 border-t border-slate-700 flex items-center justify-between bg-slate-800/50">
                <button
                  onClick={() => {
                    alerts.forEach(a => {
                      if (!a.read) onMarkRead(a.id);
                    });
                  }}
                  className="text-xs text-slate-400 hover:text-slate-200 transition-colors"
                >
                  Mark all as read
                </button>
                <button
                  onClick={() => {
                    alerts.forEach(a => onDismiss(a.id));
                  }}
                  className="text-xs text-red-400 hover:text-red-300 transition-colors"
                >
                  Dismiss all
                </button>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Critical Alert Badge (if any) */}
      {criticalAlerts.length > 0 && (
        <div className="mt-2 p-3 bg-red-900/30 border border-red-700 rounded-lg animate-pulse">
          <div className="flex items-center gap-2">
            <AlertCircle className="h-5 w-5 text-red-500" />
            <div>
              <div className="text-sm font-semibold text-red-300">
                {criticalAlerts.length} Critical Alert{criticalAlerts.length > 1 ? "s" : ""}
              </div>
              <div className="text-xs text-red-400">
                Immediate attention required
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
