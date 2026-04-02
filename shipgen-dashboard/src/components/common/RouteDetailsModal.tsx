import React, { useMemo, useState } from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';
import Modal from './Modal';
import { Button } from '../ui/Button';

interface RouteDetailsModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  routePath: string | null;
  headerTitle?: string;
  headerSubtitle?: string;
  onEdit?: () => void;
  editLabel?: string;
  onDelete?: () => void | Promise<void>;
  deleteLabel?: string;
}

const RouteDetailsModal: React.FC<RouteDetailsModalProps> = ({
  isOpen,
  onClose,
  title,
  routePath,
  headerTitle,
  headerSubtitle,
  onEdit,
  editLabel = 'Edit',
  onDelete,
  deleteLabel = 'Delete',
}) => {
  const [refreshKey, setRefreshKey] = useState(0);
  const [frameLoading, setFrameLoading] = useState(false);

  const getEmbedPath = (path: string): string => {
    const sep = path.includes('?') ? '&' : '?';
    return `${path}${sep}embed=1`;
  };

  const frameSrc = useMemo(() => {
    if (!routePath) return null;
    const base = `${window.location.pathname}#${getEmbedPath(routePath)}`;
    const sep = base.includes('?') ? '&' : '?';
    return `${base}${sep}_rk=${refreshKey}`;
  }, [routePath, refreshKey]);

  React.useEffect(() => {
    if (isOpen && frameSrc) setFrameLoading(true);
    if (!isOpen) setFrameLoading(false);
  }, [isOpen, frameSrc]);

  const refresh = () => {
    setFrameLoading(true);
    setRefreshKey((prev) => prev + 1);
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={title} bodyScrollable={false} showTitle={false}>
      <div className="space-y-4">
        {frameSrc ? (
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0">
              {headerTitle ? <p className="text-base font-bold text-gray-900">{headerTitle}</p> : null}
              {headerSubtitle ? <p className="text-sm text-gray-600 truncate">{headerSubtitle}</p> : null}
            </div>
            <div className="flex items-center gap-2">
            {onDelete ? (
              <Button
                size="sm"
                variant="danger"
                onClick={() => void onDelete()}
              >
                {deleteLabel}
              </Button>
            ) : null}
            {onEdit ? (
              <Button
                size="sm"
                onClick={onEdit}
              >
                {editLabel}
              </Button>
            ) : null}
            <Button variant="outline" size="sm" icon={RefreshCw} onClick={refresh}>
              Refresh
            </Button>
            </div>
          </div>
        ) : null}

        {frameSrc ? (
          <div className="relative">
            {frameLoading ? <p className="mb-2 text-sm text-gray-600">Loading details...</p> : null}
            <iframe
              title={title}
              src={frameSrc}
              onLoad={() => setFrameLoading(false)}
              className="h-[62vh] w-full rounded-md border-0"
            />
          </div>
        ) : (
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <AlertCircle size={16} />
            No record selected.
          </div>
        )}
      </div>
    </Modal>
  );
};

export default RouteDetailsModal;

