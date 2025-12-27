import { useQuery } from '@tanstack/react-query';
import { useAuth } from '@/hooks/useAuth';
import { API_BASE_URL } from '@/config/api';

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

// Docker Health Hook
export function useDockerHealth(enabled = true) {
  const { accessToken } = useAuth();

  return useQuery({
    queryKey: ['docker-health'],
    queryFn: async () => {
      const response = await fetch(`${API_BASE_URL}/api/v1/admin/health/docker`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch docker health');
      }

      return response.json() as Promise<DockerHealth>;
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
      const response = await fetch(`${API_BASE_URL}/api/v1/admin/health/celery`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch celery health');
      }

      return response.json() as Promise<CeleryHealth>;
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
      const url = statusFilter
        ? `${API_BASE_URL}/api/v1/admin/health/celery/tasks?status_filter=${statusFilter}`
        : `${API_BASE_URL}/api/v1/admin/health/celery/tasks`;

      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch celery tasks');
      }

      return response.json() as Promise<CeleryTasks>;
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
      const response = await fetch(`${API_BASE_URL}/api/v1/admin/health/system`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch system health');
      }

      return response.json() as Promise<SystemHealth>;
    },
    refetchInterval: 30000,
    enabled: enabled && !!accessToken,
  });
}
