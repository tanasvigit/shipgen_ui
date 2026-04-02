import React from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import ScheduleItemForm from './forms/ScheduleItemForm';

const ScheduleItemEdit: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-3">
        <Link to="/analytics/schedule-items" className="p-2 hover:bg-gray-100 rounded-lg transition">
          <ArrowLeft size={20} />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Edit Schedule Item</h1>
          <p className="text-sm text-gray-600 mt-1">PATCH /int/v1/schedules-items/{'{id}'}</p>
        </div>
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-6">
        <ScheduleItemForm mode="edit" itemId={id} onCancel={() => navigate('/analytics/schedule-items')} onSuccess={() => navigate('/analytics/schedule-items')} />
      </div>
    </div>
  );
};

export default ScheduleItemEdit;
