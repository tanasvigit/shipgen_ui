import React, { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import RouteDetailsModal from './RouteDetailsModal';

interface EntityLinkProps {
  id?: string | null;
  label?: string | null;
  to: string;
  title?: string;
  className?: string;
}

const EntityLink: React.FC<EntityLinkProps> = ({ id, label, to, title, className }) => {
  const value = (id ?? '').toString().trim();
  const text = (label ?? '').toString().trim() || value;
  const [isModalOpen, setIsModalOpen] = useState(false);
  const isDriverOrVehicleDetails = to === '/fleet/drivers' || to === '/fleet/vehicles';
  const modalTitle = to === '/fleet/drivers' ? 'Driver Details' : 'Vehicle Details';
  const routePath = useMemo(
    () => (isDriverOrVehicleDetails && value ? `${to}/${encodeURIComponent(value)}` : null),
    [isDriverOrVehicleDetails, to, value],
  );

  if (!value) {
    return <span className="text-gray-500">—</span>;
  }

  if (isDriverOrVehicleDetails) {
    return (
      <>
        <button
          type="button"
          onClick={() => setIsModalOpen(true)}
          title={title}
          className={className ?? 'text-blue-600 hover:underline cursor-pointer'}
        >
          {text}
        </button>
        <RouteDetailsModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          title={modalTitle}
          routePath={routePath}
          headerTitle={modalTitle}
          headerSubtitle={text}
        />
      </>
    );
  }

  return (
    <Link
      to={`${to}/${encodeURIComponent(value)}`}
      title={title}
      className={className ?? 'text-blue-600 hover:underline cursor-pointer'}
    >
      {text}
    </Link>
  );
};

export default EntityLink;
