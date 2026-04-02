import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';
import OrderForm from './forms/OrderForm';

const OrderCreate: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="space-y-6">
      <div className="rounded-xl border border-gray-200 bg-white p-6">
        <OrderForm mode="create" onCancel={() => navigate('/logistics/orders')} onSuccess={() => navigate('/logistics/orders')} />
      </div>
    </div>
  );
};

export default OrderCreate;
