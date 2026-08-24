import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { PageHeader } from '../../components/common/PageHeader';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { ErrorMessage } from '../../components/common/ErrorMessage';
import { DocumentStatusBadge } from '../../components/customs/DocumentStatusBadge';
import { DocumentUploadForm } from '../../components/customs/DocumentUploadForm';
import apiClient from '../../api/axios';
import { API_ENDPOINTS } from '../../api/endpoints';
import { FileText, Upload, ShieldCheck, CheckCircle2, AlertCircle, Plus } from 'lucide-react';

export const CustomsDocumentsPage = () => {
  const queryClient = useQueryClient();
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploadError, setUploadError] = useState('');

  const { data: shipmentsData, isLoading } = useQuery({
    queryKey: ['shipments-for-customs'],
    queryFn: async () => {
      const res = await apiClient.get(API_ENDPOINTS.SHIPMENTS);
      return res.data?.data || res.data;
    },
  });

  const shipmentsList = Array.isArray(shipmentsData) ? shipmentsData : shipmentsData?.results || [];
  const selectedShipmentId = shipmentsList[0]?.id;

  const { data: docsData, error, refetch } = useQuery({
    queryKey: ['customs-documents', selectedShipmentId],
    queryFn: async () => {
      if (!selectedShipmentId) return [];
      const res = await apiClient.get(API_ENDPOINTS.SHIPMENT_CUSTOMS_DOCUMENTS(selectedShipmentId));
      return res.data?.data || res.data;
    },
    enabled: !!selectedShipmentId,
  });

  const uploadMutation = useMutation({
    mutationFn: async (formData) => {
      const res = await apiClient.post(API_ENDPOINTS.SHIPMENT_CUSTOMS_DOCUMENTS(selectedShipmentId), formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return res.data;
    },
    onSuccess: () => {
      setShowUploadModal(false);
      queryClient.invalidateQueries(['customs-documents', selectedShipmentId]);
    },
    onError: (err) => {
      setUploadError(err.response?.data?.detail || 'Failed to upload customs document.');
    },
  });

  const docsList = Array.isArray(docsData) ? docsData : docsData?.results || [];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Customs Documentation & Digital Clearance"
        subtitle="Manage required commercial invoices, packing lists, bills of lading, and certificate of origin clearance documents."
        actions={
          selectedShipmentId && (
            <button
              onClick={() => setShowUploadModal(true)}
              className="px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white rounded-xl text-xs font-semibold flex items-center space-x-1.5 shadow-lg shadow-cyan-500/20 transition"
            >
              <Plus className="w-4 h-4" />
              <span>Upload Document</span>
            </button>
          )
        }
      />

      {isLoading ? (
        <LoadingSpinner label="Fetching customs declaration workspace..." />
      ) : docsList.length === 0 ? (
        <div className="glass-panel p-12 text-center rounded-2xl border border-slate-800 space-y-4 max-w-md mx-auto my-8">
          <FileText className="w-12 h-12 text-cyan-400 mx-auto" />
          <h3 className="text-base font-bold text-white">Digital Customs Declaration Ready</h3>
          <p className="text-xs text-slate-400">
            Upload commercial invoices, packing lists, and bills of lading to initiate Ethiopian Customs Authority validation.
          </p>
          {selectedShipmentId && (
            <button
              onClick={() => setShowUploadModal(true)}
              className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-xl text-xs font-semibold inline-flex items-center space-x-1.5 shadow-lg shadow-cyan-600/20 transition mx-auto"
            >
              <Upload className="w-4 h-4" />
              <span>Upload First Document</span>
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {docsList.map((doc) => (
            <div key={doc.id} className="glass-card p-5 rounded-2xl border border-slate-800 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-white uppercase">{doc.document_type?.replace('_', ' ')}</span>
                <DocumentStatusBadge status={doc.status} />
              </div>
              <p className="text-xs text-slate-400 font-mono">Ref: {doc.document_number}</p>
              <p className="text-[11px] text-slate-500">Uploaded {new Date(doc.created_at).toLocaleDateString()}</p>
            </div>
          ))}
        </div>
      )}

      {showUploadModal && (
        <DocumentUploadForm
          onSubmit={(formData) => uploadMutation.mutate(formData)}
          onCancel={() => setShowUploadModal(false)}
          submitting={uploadMutation.isPending}
          serverError={uploadError}
        />
      )}
    </div>
  );
};
