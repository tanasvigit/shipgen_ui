import React from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import OrderForm from './forms/OrderForm';

const OrderEdit: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  return (
    <div className="space-y-6">
      <div className="rounded-xl border border-gray-200 bg-white p-6">
        <OrderForm mode="edit" orderId={id} onCancel={() => navigate('/logistics/orders')} onSuccess={() => navigate('/logistics/orders')} />
      </div>
    </div>
  );
};

export default OrderEdit;
