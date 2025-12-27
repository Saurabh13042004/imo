import { useDockerHealth, useCeleryHealth, useCeleryTasks, useSystemHealth } from "@/hooks/useHealthCheck";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { HardDrive, Cpu, BarChart3, Activity, AlertCircle } from "lucide-react";

export const ServerMonitoring = () => {
  const { data: dockerHealth } = useDockerHealth();
  const { data: celeryHealth } = useCeleryHealth();
  const { data: celeryTasks } = useCeleryTasks();
  const { data: systemHealth } = useSystemHealth();

  const getStatusBadge = (status: string | undefined) => {
    switch (status) {
      case "ok":
        return (
          <Badge className="bg-green-100 text-green-800 hover:bg-green-100">
            OK
          </Badge>
        );
      case "error":
        return (
          <Badge className="bg-red-100 text-red-800 hover:bg-red-100">
            ERROR
          </Badge>
        );
      case "unavailable":
        return (
          <Badge className="bg-amber-100 text-amber-800 hover:bg-amber-100">
            UNAVAILABLE
          </Badge>
        );
      default:
        return (
          <Badge className="bg-gray-100 text-gray-800 hover:bg-gray-100">
            UNKNOWN
          </Badge>
        );
    }
  };


  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Server Monitoring</h1>
        <p className="text-gray-600 mt-1">Real-time infrastructure health overview</p>
      </div>

      {/* System Health */}
      {systemHealth?.status === "ok" && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* CPU */}
          <Card className="bg-white border-slate-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Cpu className="w-5 h-5 text-blue-600" />
                <h3 className="font-semibold text-slate-900">CPU Usage</h3>
              </div>
            </div>
            <p className="text-3xl font-bold text-slate-900">
              {systemHealth.cpu?.percent.toFixed(1)}%
            </p>
            <p className="text-sm text-slate-600 mt-2">
              {systemHealth.cpu?.cores} cores
            </p>
            <div className="mt-4 h-2 bg-slate-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-500 transition-all duration-500"
                style={{ width: `${Math.min(systemHealth.cpu?.percent || 0, 100)}%` }}
              />
            </div>
          </Card>

          {/* Memory */}
          <Card className="bg-white border-slate-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-purple-600" />
                <h3 className="font-semibold text-slate-900">Memory</h3>
              </div>
            </div>
            <p className="text-3xl font-bold text-slate-900">
              {systemHealth.memory?.percent.toFixed(1)}%
            </p>
            <p className="text-sm text-slate-600 mt-2">
              {systemHealth.memory?.available_gb}GB / {systemHealth.memory?.total_gb}GB
            </p>
            <div className="mt-4 h-2 bg-slate-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-purple-500 transition-all duration-500"
                style={{ width: `${Math.min(systemHealth.memory?.percent || 0, 100)}%` }}
              />
            </div>
          </Card>

          {/* Disk */}
          <Card className="bg-white border-slate-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <HardDrive className="w-5 h-5 text-orange-600" />
                <h3 className="font-semibold text-slate-900">Disk Space</h3>
              </div>
            </div>
            <p className="text-3xl font-bold text-slate-900">
              {systemHealth.disk?.percent.toFixed(1)}%
            </p>
            <p className="text-sm text-slate-600 mt-2">
              {systemHealth.disk?.free_gb}GB / {systemHealth.disk?.total_gb}GB
            </p>
            <div className="mt-4 h-2 bg-slate-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-orange-500 transition-all duration-500"
                style={{ width: `${Math.min(systemHealth.disk?.percent || 0, 100)}%` }}
              />
            </div>
          </Card>
        </div>
      )}

      {/* Docker Containers */}
      <Card className="bg-white border-slate-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-slate-900" />
            <h3 className="text-lg font-semibold text-slate-900">
              Docker Containers ({dockerHealth?.total_containers || 0})
            </h3>
          </div>
          {getStatusBadge(dockerHealth?.status)}
        </div>

        {dockerHealth?.status === "error" && (
          <div className="flex items-center gap-3 p-4 bg-red-50 rounded border border-red-200 mb-4">
            <AlertCircle className="w-4 h-4 text-red-600 flex-shrink-0" />
            <div>
              <p className="text-sm font-medium text-red-900">Error</p>
              <p className="text-sm text-red-800">{dockerHealth.message}</p>
            </div>
          </div>
        )}

        {dockerHealth?.status === "unavailable" && (
          <div className="flex items-center gap-3 p-4 bg-amber-50 rounded border border-amber-200 mb-4">
            <AlertCircle className="w-4 h-4 text-amber-600 flex-shrink-0" />
            <div>
              <p className="text-sm font-medium text-amber-900">Unavailable</p>
              <p className="text-sm text-amber-800">{dockerHealth.message}</p>
            </div>
          </div>
        )}

        {dockerHealth?.status === "ok" && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {dockerHealth.containers && dockerHealth.containers.length > 0 ? (
              dockerHealth.containers.map((container: any, idx: number) => (
                <div
                  key={idx}
                  className={`p-4 rounded-lg border ${
                    container.state === "running"
                      ? "bg-green-50 border-green-200"
                      : "bg-gray-50 border-gray-200"
                  }`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <p className="font-medium text-slate-900">{container.name}</p>
                      <p className="text-xs text-slate-600 font-mono">{container.id}</p>
                    </div>
                    <Badge
                      variant="outline"
                      className={`${
                        container.state === "running"
                          ? "bg-green-100 text-green-800 hover:bg-green-100"
                          : "bg-gray-100 text-gray-800 hover:bg-gray-100"
                      }`}
                    >
                      {container.state}
                    </Badge>
                  </div>
                  <p className="text-xs text-slate-600">{container.status}</p>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-slate-500 col-span-2">
                No containers found
              </div>
            )}
          </div>
        )}
      </Card>

      {/* Celery Workers */}
      <Card className="bg-white border-slate-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-slate-900" />
            <h3 className="text-lg font-semibold text-slate-900">
              Celery Workers ({celeryHealth?.total_workers || 0})
            </h3>
          </div>
          {getStatusBadge(celeryHealth?.status)}
        </div>

        {celeryHealth?.status === "error" && (
          <div className="flex items-center gap-3 p-4 bg-red-50 rounded border border-red-200 mb-4">
            <AlertCircle className="w-4 h-4 text-red-600 flex-shrink-0" />
            <div>
              <p className="text-sm font-medium text-red-900">Error</p>
              <p className="text-sm text-red-800">{celeryHealth.message}</p>
            </div>
          </div>
        )}

        {celeryHealth?.status === "unavailable" && (
          <div className="flex items-center gap-3 p-4 bg-amber-50 rounded border border-amber-200 mb-4">
            <AlertCircle className="w-4 h-4 text-amber-600 flex-shrink-0" />
            <div>
              <p className="text-sm font-medium text-amber-900">Unavailable</p>
              <p className="text-sm text-amber-800">{celeryHealth.message}</p>
            </div>
          </div>
        )}

        {celeryHealth?.status === "ok" && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {celeryHealth.workers && celeryHealth.workers.length > 0 ? (
              celeryHealth.workers.map((worker: any, idx: number) => (
                <div
                  key={idx}
                  className={`p-4 rounded-lg border ${
                    worker.state === "online"
                      ? "bg-green-50 border-green-200"
                      : "bg-gray-50 border-gray-200"
                  }`}
                >
                  <div className="flex items-start justify-between mb-3">
                    <p className="font-medium text-slate-900">{worker.name}</p>
                    <Badge
                      variant="outline"
                      className={`${
                        worker.state === "online"
                          ? "bg-green-100 text-green-800 hover:bg-green-100"
                          : "bg-gray-100 text-gray-800 hover:bg-gray-100"
                      }`}
                    >
                      {worker.state}
                    </Badge>
                  </div>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-slate-600">Active Tasks</span>
                      <span className="font-semibold text-slate-900">
                        {worker.active_tasks}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-600">Registered Tasks</span>
                      <span className="font-semibold text-slate-900">
                        {worker.registered_tasks}
                      </span>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-slate-500 col-span-2">
                No workers found
              </div>
            )}
          </div>
        )}
      </Card>

      {/* Running Tasks */}
      <Card className="bg-white border-slate-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-slate-900">
            Running Tasks ({celeryTasks?.total_tasks || 0})
          </h3>
          {getStatusBadge(celeryTasks?.status)}
        </div>

        {celeryTasks?.status === "error" && (
          <div className="flex items-center gap-3 p-4 bg-red-50 rounded border border-red-200 mb-4">
            <AlertCircle className="w-4 h-4 text-red-600 flex-shrink-0" />
            <div>
              <p className="text-sm font-medium text-red-900">Error</p>
              <p className="text-sm text-red-800">{celeryTasks.message}</p>
            </div>
          </div>
        )}

        {celeryTasks?.status === "unavailable" && (
          <div className="flex items-center gap-3 p-4 bg-amber-50 rounded border border-amber-200 mb-4">
            <AlertCircle className="w-4 h-4 text-amber-600 flex-shrink-0" />
            <div>
              <p className="text-sm font-medium text-amber-900">Unavailable</p>
              <p className="text-sm text-amber-800">{celeryTasks.message}</p>
            </div>
          </div>
        )}

        {celeryTasks?.status === "ok" && (
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {celeryTasks.tasks && celeryTasks.tasks.length > 0 ? (
              celeryTasks.tasks.slice(0, 20).map((task: any, idx: number) => (
                <div
                  key={idx}
                  className="p-4 rounded-lg border border-slate-200 hover:shadow-sm transition-shadow"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <p className="font-medium text-slate-900">{task.name}</p>
                      <p className="text-xs text-slate-600 font-mono">
                        {task.id.substring(0, 12)}...
                      </p>
                    </div>
                    <Badge
                      variant="outline"
                      className={`${
                        task.status === "active"
                          ? "bg-blue-100 text-blue-800 hover:bg-blue-100"
                          : "bg-yellow-100 text-yellow-800 hover:bg-yellow-100"
                      }`}
                    >
                      {task.status}
                    </Badge>
                  </div>
                  <div className="text-xs text-slate-600 space-y-1">
                    <p>Worker: {task.worker}</p>
                    {task.started_at && (
                      <p>Started: {new Date(task.started_at).toLocaleString()}</p>
                    )}
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-slate-500">
                No running tasks
              </div>
            )}
          </div>
        )}
      </Card>

      {/* Last Updated */}
      <div className="text-xs text-slate-500 text-center">
        Last updated: {new Date().toLocaleTimeString()}
      </div>
    </div>
  );
};
