import React, { useMemo, useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import { AlertCircle, ArrowLeft, Download, Play } from 'lucide-react';
import { reportsService, type UiReport } from '../../services/reportsService';

type ResultMode = 'none' | 'array' | 'object';

const ReportDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [report, setReport] = useState<UiReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [executing, setExecuting] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [resultMode, setResultMode] = useState<ResultMode>('none');
  const [resultRows, setResultRows] = useState<Record<string, unknown>[]>([]);
  const [resultObject, setResultObject] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    const load = async () => {
      if (!id) return;
      try {
        setLoading(true);
        setError(null);
        const row = await reportsService.getById(id);
        setReport(row);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to load report');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [id]);

  const executeReport = async () => {
    if (!id) return;
    try {
      setExecuting(true);
      setError(null);
      const result = await reportsService.execute(id);
      if (result.resultType === 'array') {
        setResultMode('array');
        setResultRows(result.rows);
        setResultObject(null);
      } else {
        setResultMode('object');
        setResultRows([]);
        setResultObject(result.objectData);
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to execute report');
    } finally {
      setExecuting(false);
    }
  };

  const exportReport = async () => {
    if (!id) return;
    try {
      setExporting(true);
      setError(null);
      await reportsService.export(id);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to export report');
    } finally {
      setExporting(false);
    }
  };

  const columns = useMemo(() => {
    if (resultRows.length === 0) return [];
    return Object.keys(resultRows[0]);
  }, [resultRows]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
      </div>
    );
  }

  if (!report) {
    return <div className="text-gray-600">Report not found.</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Link to="/analytics/reports" className="p-2 hover:bg-gray-100 rounded-lg transition">
            <ArrowLeft size={20} />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{report.name || 'Untitled Report'}</h1>
            <p className="text-sm text-gray-600 mt-1">/int/v1/reports/{'{id}'}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={executeReport}
            disabled={executing}
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition"
          >
            <Play size={16} />
            <span>{executing ? 'Executing...' : 'Execute Report'}</span>
          </button>
          <button
            type="button"
            onClick={exportReport}
            disabled={exporting}
            className="inline-flex items-center gap-2 px-4 py-2 border border-gray-200 text-gray-700 rounded-lg hover:bg-gray-50 disabled:opacity-50 transition"
          >
            <Download size={16} />
            <span>{exporting ? 'Exporting...' : 'Export Report'}</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center space-x-2">
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      <div className="bg-white rounded-xl border border-gray-200 p-6 space-y-3">
        <div>
          <div className="text-xs font-medium text-gray-500 uppercase">name</div>
          <div className="text-sm text-gray-900 mt-1">{report.name || '—'}</div>
        </div>
        <div>
          <div className="text-xs font-medium text-gray-500 uppercase">description</div>
          <div className="text-sm text-gray-900 mt-1 whitespace-pre-wrap">{report.description || '—'}</div>
        </div>
        <div>
          <div className="text-xs font-medium text-gray-500 uppercase">created_at</div>
          <div className="text-sm text-gray-900 mt-1">
            {report.created_at ? new Date(report.created_at).toLocaleString() : '—'}
          </div>
        </div>
      </div>

      {resultMode !== 'none' && (
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="text-lg font-bold text-gray-900 mb-4">Execution Result</h2>

          {resultMode === 'array' ? (
            resultRows.length === 0 ? (
              <p className="text-sm text-gray-600">No rows returned.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      {columns.map((column) => (
                        <th key={column} className="text-left py-3 px-4 text-xs font-semibold text-gray-600 uppercase">
                          {column}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {resultRows.map((row, idx) => (
                      <tr key={idx}>
                        {columns.map((column) => (
                          <td key={column} className="py-3 px-4 text-sm text-gray-700">
                            {row[column] == null ? '—' : String(row[column])}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )
          ) : (
            <pre className="text-sm bg-gray-50 border border-gray-100 rounded-lg p-4 overflow-x-auto whitespace-pre-wrap">
              {JSON.stringify(resultObject, null, 2)}
            </pre>
          )}
        </div>
      )}
    </div>
  );
};

export default ReportDetail;
