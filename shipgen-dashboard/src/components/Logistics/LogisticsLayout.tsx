import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import SubNavigation from '../SubNavigation';

const LogisticsLayout: React.FC = () => {
  const location = useLocation();
  const isEmbedded = new URLSearchParams(location.search).get('embed') === '1';
  const subNavItems = [
    {
      path: '/logistics/orders/dispatch-board',
      label: 'Dispatcher Board',
      match: (p: string) => p.startsWith('/logistics/orders/dispatch-board'),
    },
    { path: '/logistics/customers', label: 'Customers', exact: true },
    {
      path: '/logistics/orders',
      label: 'Orders List',
      match: (p: string) =>
        p === '/logistics/orders' ||
        (p.startsWith('/logistics/orders/') && !p.startsWith('/logistics/orders/dispatch-board')),
    },
  ];
  const contentGutter = 'px-4 sm:px-5 lg:px-8';

  return (
    <div
      className={
        isEmbedded
          ? 'min-w-0 w-full'
          : 'min-w-0 w-[calc(100%+2rem)] max-w-none -mx-4 lg:w-[calc(100%+4rem)] lg:-mx-8'
      }
    >
      {!isEmbedded ? (
        <div className={contentGutter}>
          <SubNavigation items={subNavItems} basePath="/logistics" />
        </div>
      ) : null}
      <Outlet />
    </div>
  );
};

export default LogisticsLayout;
