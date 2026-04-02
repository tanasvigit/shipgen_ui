import React from 'react';
import { Outlet } from 'react-router-dom';
import SubNavigation from '../SubNavigation';

const DashboardWrapper: React.FC = () => {
  const subNavItems = [
    { path: '/dashboard', label: 'Overview', exact: true }
  ];

  return (
    <div>
      <SubNavigation items={subNavItems} basePath="/dashboard" />
      <Outlet />
    </div>
  );
};

export default DashboardWrapper;
