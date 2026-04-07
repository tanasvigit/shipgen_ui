import React from 'react';
import { Outlet } from 'react-router-dom';

/** Order routes only; shared logistics chrome lives in `LogisticsLayout`. */
const OrdersWrapper: React.FC = () => <Outlet />;

export default OrdersWrapper;
