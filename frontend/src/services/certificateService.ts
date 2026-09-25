import { apiClient } from './apiClient';
import { Certificate, CertificateVerification } from '../types/certificate';

export const certificateService = {
  async getCertificateById(certificateId: string): Promise<Certificate> {
    const response = await apiClient.get<Certificate>(`/api/v1/certificates/${certificateId}`);
    return response.data;
  },

  async getCourseCertificate(courseId: string): Promise<Certificate> {
    const response = await apiClient.get<Certificate>(`/api/v1/courses/${courseId}/certificate`);
    return response.data;
  },

  async verifyCertificate(certificateNumber: string): Promise<CertificateVerification> {
    const response = await apiClient.get<CertificateVerification>(
      `/api/v1/certificates/verify/${certificateNumber}`
    );
    return response.data;
  },
};
