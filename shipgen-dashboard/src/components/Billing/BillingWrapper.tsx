import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import SubNavigation from '../SubNavigation';

const BillingWrapper: React.FC = () => {
  const location = useLocation();
  const isEmbedded = new URLSearchParams(location.search).get('embed') === '1';
  const subNavItems = [
    { path: '/billing/invoices', label: 'Invoices', exact: true },
    { path: '/billing/payments', label: 'Payments' },
    { path: '/billing/invoices/generate', label: 'Generate Invoice' }
  ];

  return (
    <div>
      {!isEmbedded ? <SubNavigation items={subNavItems} basePath="/billing" /> : null}
      <Outlet />
    </div>
  );
};

export default BillingWrapper;
