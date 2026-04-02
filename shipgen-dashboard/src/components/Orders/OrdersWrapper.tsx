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

  /** Same horizontal inset as `PageContainer flushHorizontal` on list/board pages — keeps sub-nav aligned with cards. */
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
          <SubNavigation items={subNavItems} basePath="/logistics/orders" />
        </div>
      ) : null}
      <Outlet />
    </div>
  );
};

export default OrdersWrapper;
