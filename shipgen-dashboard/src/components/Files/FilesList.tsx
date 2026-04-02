import React, { useEffect, useMemo, useRef, useState } from 'react';
import { AlertCircle, Download, Search, Trash2, Upload, FileText } from 'lucide-react';
import { filesService, type UiFileItem } from '../../services/filesService';

const formatSize = (bytes: number): string => {
  if (!Number.isFinite(bytes) || bytes <= 0) return '0 B';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`;
};

const FilesList: React.FC = () => {
  const [rows, setRows] = useState<UiFileItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const loadFiles = async () => {
    try {
      setLoading(true);
      setError(null);
      const list = await filesService.list({ limit: 100, offset: 0 });
      setRows(list);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load files');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFiles();
  }, []);

  const filtered = useMemo(() => {
    const q = searchTerm.trim().toLowerCase();
    if (!q) return rows;
    return rows.filter((r) => r.name.toLowerCase().includes(q));
  }, [rows, searchTerm]);

  const onUploadClick = () => {
    fileInputRef.current?.click();
  };

  const onFileSelected = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      setUploading(true);
      setError(null);
      setSuccess(null);
      await filesService.upload(file);
      setSuccess('File uploaded successfully.');
      await loadFiles();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  const onDownload = async (id: string) => {
    try {
      setError(null);
      await filesService.download(id);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Download failed');
    }
  };

  const onDelete = async (id: string) => {
    if (!window.confirm('Delete this file?')) return;
    try {
      setError(null);
      setSuccess(null);
      await filesService.remove(id);
      setSuccess('File deleted successfully.');
      await loadFiles();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Delete failed');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Files</h1>
          <p className="text-sm text-gray-600 mt-1">Upload, download and manage files</p>
        </div>
        <button
          type="button"
          onClick={onUploadClick}
          disabled={uploading}
          className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition"
        >
          <Upload size={16} />
          <span>{uploading ? 'Uploading...' : 'Upload File'}</span>
        </button>
        <input ref={fileInputRef} type="file" className="hidden" onChange={onFileSelected} />
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
        <input
          type="text"
          placeholder="Search by file name..."
          className="w-full pl-10 pr-4 py-2 bg-white border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center gap-2">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}
      {success && <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">{success}</div>}

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          {filtered.length === 0 ? (
            <div className="p-12 text-center">
              <FileText size={48} className="mx-auto text-gray-300 mb-4" />
              <p className="text-gray-600">No files found</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="text-left py-3 px-4 text-xs font-semibold text-gray-600 uppercase">name</th>
                    <th className="text-left py-3 px-4 text-xs font-semibold text-gray-600 uppercase">size</th>
                    <th className="text-left py-3 px-4 text-xs font-semibold text-gray-600 uppercase">created_at</th>
                    <th className="text-right py-3 px-4 text-xs font-semibold text-gray-600 uppercase">actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {filtered.map((row) => (
                    <tr key={row.id}>
                      <td className="py-3 px-4 text-sm font-medium text-gray-900">{row.name || '—'}</td>
                      <td className="py-3 px-4 text-sm text-gray-700">{formatSize(row.size)}</td>
                      <td className="py-3 px-4 text-sm text-gray-700">
                        {row.created_at ? new Date(row.created_at).toLocaleString() : '—'}
                      </td>
                      <td className="py-3 px-4 text-right">
                        <div className="inline-flex items-center gap-2">
                          <button
                            type="button"
                            onClick={() => onDownload(row.id)}
                            className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition"
                            title="Download"
                          >
                            <Download size={16} />
                          </button>
                          <button
                            type="button"
                            onClick={() => onDelete(row.id)}
                            className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition"
                            title="Delete"
                          >
                            <Trash2 size={16} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default FilesList;
