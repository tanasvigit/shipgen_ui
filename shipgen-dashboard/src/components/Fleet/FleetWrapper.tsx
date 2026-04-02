import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import SubNavigation from '../SubNavigation';

const FleetWrapper: React.FC = () => {
  const location = useLocation();
  const isEmbedded = new URLSearchParams(location.search).get('embed') === '1';
  const menuItems = [
    { path: '/fleet/vehicles', label: 'Vehicles' },
    { path: '/fleet/drivers', label: 'Drivers' },
    { path: '/fleet/fleets', label: 'Fleets' },
    { path: '/fleet/service-areas', label: 'Service Areas' },
    { path: '/fleet/zones', label: 'Zones' },
    { path: '/fleet/places', label: 'Places' },
    { path: '/fleet/tracking-numbers', label: 'Tracking Numbers' },
    { path: '/fleet/tracking-statuses', label: 'Tracking Statuses' },
    { path: '/fleet/entities', label: 'Entities' },
    { path: '/fleet/contacts', label: 'Contacts' },
    { path: '/fleet/vendors', label: 'Vendors' },
    { path: '/fleet/payloads', label: 'Payloads' },
    { path: '/fleet/issues', label: 'Issues' },
    { path: '/fleet/fuel-reports', label: 'Fuel Reports' },
  ];

  const getCurrentItem = () => {
    const current = menuItems.find(
      (item) =>
        location.pathname === item.path || location.pathname.startsWith(item.path + '/'),
    );
    return current || menuItems[0];
  };

  const currentItem = getCurrentItem();
  const listLabelByPath: Record<string, string> = {
    '/fleet/vehicles': 'Vehicles List',
    '/fleet/drivers': 'Drivers List',
    '/fleet/vendors': 'Vendors List',
    '/fleet/fleets': 'Fleets List',
    '/fleet/service-areas': 'Service Areas List',
    '/fleet/zones': 'Zones List',
    '/fleet/places': 'Places List',
    '/fleet/tracking-numbers': 'Tracking Numbers List',
    '/fleet/tracking-statuses': 'Tracking Statuses List',
    '/fleet/entities': 'Entities List',
    '/fleet/contacts': 'Contacts List',
    '/fleet/payloads': 'Payloads List',
    '/fleet/issues': 'Issues List',
    '/fleet/fuel-reports': 'Fuel Reports List',
  };
  const createTabByPath: Record<string, { path: string; label: string }> = {};
  const currentTabs = [
    {
      path: currentItem.path,
      label: listLabelByPath[currentItem.path] ?? `${currentItem.label} List`,
      exact: true,
    },
    ...(createTabByPath[currentItem.path] ? [createTabByPath[currentItem.path]] : []),
  ];

  return (
    <div>
      {!isEmbedded ? <SubNavigation items={currentTabs} basePath={currentItem.path} /> : null}
      <Outlet />
    </div>
  );
};

export default FleetWrapper;
