export default function Dashboard() {
  const metrics = [
    { label: "Active Agents", value: "8" },
    { label: "Tasks Completed", value: "1,240" },
    { label: "Avg. Latency", value: "0.4s" },
    { label: "Uptime", value: "99.9%" }
  ];

  return (
    <div>
      <h2 className="text-3xl font-bold mb-8">Founder Dashboard</h2>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {metrics.map((m, i) => (
            <div key={i} className="bg-card-bg p-6 rounded-lg border border-gray-800">
                <div className="text-gray-400 text-sm mb-1">{m.label}</div>
                <div className="text-3xl font-bold text-white">{m.value}</div>
            </div>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="bg-card-bg p-6 rounded-lg border border-gray-800 h-64 flex items-center justify-center">
            <span className="text-gray-500">[System Health Visualization Placeholder]</span>
        </div>
        <div className="bg-card-bg p-6 rounded-lg border border-gray-800 h-64 flex items-center justify-center">
            <span className="text-gray-500">[Task Queue Visualization Placeholder]</span>
        </div>
      </div>
    </div>
  );
}
