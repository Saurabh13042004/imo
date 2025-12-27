import { useQuery } from '@tanstack/react-query';
import { useAuth } from '@/hooks/useAuth';

interface Container {
  id: string;
  name: string;
  status: string;
  state: string;
  health: string;
}

interface DockerHealth {
  status: string;
  timestamp: string;
  containers: Container[];
  total_containers: number;
}

interface Worker {
  name: string;
  state: string;
  active_tasks: number;
  registered_tasks: number;
}

interface CeleryHealth {
  status: string;
  timestamp: string;
  workers: Worker[];
  total_workers: number;
  total_active_tasks: number;
}

interface Task {
  id: string;
  name: string;
  worker: string;
  status: string;
  args: string;
  kwargs: string;
  started_at?: string;
}

interface CeleryTasks {
  status: string;
  timestamp: string;
  tasks: Task[];
  total_tasks: number;
}

interface SystemHealth {
  status: string;
  timestamp: string;
  cpu?: {
    percent: number;
    cores: number;
  };
  memory?: {
    total_gb: number;
    available_gb: number;
    percent: number;
  };
  disk?: {
    total_gb: number;
    free_gb: number;
    percent: number;
  };
}

async function apiCall<T>(
  endpoint: string,
  accessToken: string
): Promise<T> {
  const response = await fetch(endpoint, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!response.ok) {
    throw new Error(`API call failed: ${response.statusText}`);
  }

  return response.json();
}

// Docker Health Hook
export function useDockerHealth(enabled = true) {
  const { accessToken } = useAuth();

  return useQuery({
    queryKey: ['docker-health'],
    queryFn: async () => {
      if (!accessToken) throw new Error('Not authenticated');
      return apiCall<DockerHealth>(
        '/api/v1/admin/health/docker',
        accessToken
      );
    },
    refetchInterval: 30000, // Refresh every 30 seconds
    enabled: enabled && !!accessToken,
  });
}

// Celery Health Hook
export function useCeleryHealth(enabled = true) {
  const { accessToken } = useAuth();

  return useQuery({
    queryKey: ['celery-health'],
    queryFn: async () => {
      if (!accessToken) throw new Error('Not authenticated');
      return apiCall<CeleryHealth>(
        '/api/v1/admin/health/celery',
        accessToken
      );
    },
    refetchInterval: 30000,
    enabled: enabled && !!accessToken,
  });
}

// Celery Tasks Hook
export function useCeleryTasks(statusFilter?: string, enabled = true) {
  const { accessToken } = useAuth();

  return useQuery({
    queryKey: ['celery-tasks', statusFilter],
    queryFn: async () => {
      if (!accessToken) throw new Error('Not authenticated');
      const url = statusFilter
        ? `/api/v1/admin/health/celery/tasks?status_filter=${statusFilter}`
        : '/api/v1/admin/health/celery/tasks';
      return apiCall<CeleryTasks>(url, accessToken);
    },
    refetchInterval: 15000, // Refresh every 15 seconds for tasks
    enabled: enabled && !!accessToken,
  });
}

// System Health Hook
export function useSystemHealth(enabled = true) {
  const { accessToken } = useAuth();

  return useQuery({
    queryKey: ['system-health'],
    queryFn: async () => {
      if (!accessToken) throw new Error('Not authenticated');
      return apiCall<SystemHealth>(
        '/api/v1/admin/health/system',
        accessToken
      );
    },
    refetchInterval: 30000,
    enabled: enabled && !!accessToken,
  });
}
