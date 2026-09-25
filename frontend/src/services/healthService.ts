import { apiClient } from './apiClient';
import { HealthResponse } from '../types';

export const healthService = {
  async checkHealth(): Promise<HealthResponse> {
    const response = await apiClient.get<HealthResponse>('/health');
    return response.data;
  },
  async checkApiV1Health(): Promise<HealthResponse> {
    const response = await apiClient.get<HealthResponse>('/api/v1/health');
    return response.data;
  },
};
