import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { certificateService } from '../../services/certificateService';
import {
  ShieldCheck,
  ShieldAlert,
  Search,
  CheckCircle2,
  Award,
  BookOpen,
} from 'lucide-react';

export const CertificateVerificationPage: React.FC = () => {
  const { certificateNumber: routeCertNumber } = useParams<{ certificateNumber?: string }>();
  const navigate = useNavigate();
  const [searchInput, setSearchInput] = useState(routeCertNumber || '');
  const [activeNumber, setActiveNumber] = useState(routeCertNumber || '');

  const {
    data: verification,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ['certificate-verify', activeNumber],
    queryFn: () => certificateService.verifyCertificate(activeNumber),
    enabled: !!activeNumber,
    retry: false,
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchInput.trim()) {
      setActiveNumber(searchInput.trim());
      navigate(`/verify/certificate/${searchInput.trim()}`);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center p-3 bg-primary-100 rounded-full text-primary-700 mb-3">
            <ShieldCheck className="w-8 h-8" />
          </div>
          <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">
            Official Certificate Verification
          </h1>
          <p className="mt-2 text-base text-gray-600">
            Verify the authenticity and integrity of credentials issued by the Enterprise Learning Platform.
          </p>
        </div>

        {/* Search Input */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8">
          <form onSubmit={handleSearch} className="flex gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-3.5 top-3.5 h-4 w-4 text-gray-400" />
              <input
                type="text"
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                placeholder="Enter Certificate ID (e.g. CERT-2026-XXXXX)..."
                className="w-full pl-10 pr-4 py-2.5 rounded-lg border-gray-300 text-sm focus:ring-primary-500 focus:border-primary-500 font-mono"
              />
            </div>
            <button
              type="submit"
              className="px-6 py-2.5 bg-primary-600 hover:bg-primary-700 text-white text-sm font-semibold rounded-lg shadow-sm transition-colors"
            >
              Verify
            </button>
          </form>
        </div>

        {/* Verification Result State */}
        {isLoading && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto mb-3" />
            <p className="text-sm text-gray-500">Querying cryptographic records...</p>
          </div>
        )}

        {isError && (
          <div className="bg-white rounded-xl shadow-sm border border-red-200 p-8 text-center">
            <ShieldAlert className="w-12 h-12 text-red-500 mx-auto mb-3" />
            <h2 className="text-xl font-bold text-gray-900 mb-1">Invalid Certificate Record</h2>
            <p className="text-sm text-red-600 mb-2">
              No matching certificate could be verified for ID: <span className="font-mono font-semibold">{activeNumber}</span>
            </p>
            <p className="text-xs text-gray-500">
              Please double check the certificate number from your credential or contact the issuer.
            </p>
          </div>
        )}

        {verification && verification.is_valid && (
          <div className="bg-white rounded-2xl shadow-md border border-green-200 p-8">
            <div className="flex items-center gap-3 border-b border-gray-100 pb-5 mb-6">
              <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center shrink-0">
                <CheckCircle2 className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-green-100 text-green-800 uppercase tracking-wide">
                  Valid Verified Credential
                </span>
                <h2 className="text-xl font-bold text-gray-900 mt-1">
                  Authentic Certificate Verified
                </h2>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 mb-6">
              <div className="flex items-start gap-3">
                <div>
                  <span className="text-xs text-gray-500 uppercase font-semibold">Recipient</span>
                  <p className="text-base font-bold text-gray-900">{verification.student_name}</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <BookOpen className="w-5 h-5 text-gray-400 mt-0.5" />
                <div>
                  <span className="text-xs text-gray-500 uppercase font-semibold">Course</span>
                  <p className="text-base font-bold text-gray-900">{verification.course_title}</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <div>
                  <span className="text-xs text-gray-500 uppercase font-semibold">Issue Date</span>
                  <p className="text-sm font-medium text-gray-800">
                    {new Date(verification.issued_at).toLocaleDateString(undefined, {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                    })}
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <Award className="w-5 h-5 text-gray-400 mt-0.5" />
                <div>
                  <span className="text-xs text-gray-500 uppercase font-semibold">Certificate ID</span>
                  <p className="text-sm font-mono font-bold text-primary-700">
                    {verification.certificate_number}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-gray-50 rounded-lg p-4 border border-gray-100">
              <span className="text-xs text-gray-500 font-semibold uppercase block mb-1">
                Cryptographic Verification Hash
              </span>
              <p className="text-xs font-mono text-gray-600 break-all">
                {verification.verification_hash}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
