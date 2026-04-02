import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import SubNavigation from '../SubNavigation';

const OrdersWrapper: React.FC = () => {
  const location = useLocation();
  const isEmbedded = new URLSearchParams(location.search).get('embed') === '1';
  const subNavItems = [
    { path: '/logistics/orders', label: 'Orders List', exact: true },
    { path: '/logistics/orders/dispatch-board', label: 'Dispatcher Board' },
  ];

  return (
    <div>
      {!isEmbedded ? <SubNavigation items={subNavItems} basePath="/logistics/orders" /> : null}
      <Outlet />
    </div>
  );
};

export default OrdersWrapper;
