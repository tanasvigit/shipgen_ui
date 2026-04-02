import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import SubNavigation from '../SubNavigation';

const WarehouseWrapper: React.FC = () => {
  const location = useLocation();
  const isEmbedded = new URLSearchParams(location.search).get('embed') === '1';
  const subNavItems = [
    { path: '/warehouse/inventory', label: 'Inventory', exact: true },
    { path: '/warehouse/zones', label: 'Zones' },
    { path: '/warehouse/inventory/grn', label: 'Process GRN' }
  ];

  return (
    <div>
      {!isEmbedded ? <SubNavigation items={subNavItems} basePath="/warehouse" /> : null}
      <Outlet />
    </div>
  );
};

export default WarehouseWrapper;
