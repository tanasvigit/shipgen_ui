import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import ScheduleAvailabilityForm from './forms/ScheduleAvailabilityForm';

const ScheduleAvailabilityCreate: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-3">
        <Link to="/analytics/schedule-availability" className="p-2 hover:bg-gray-100 rounded-lg transition">
          <ArrowLeft size={20} />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Create Schedule Availability</h1>
          <p className="text-sm text-gray-600 mt-1">POST /int/v1/schedules-availability/</p>
        </div>
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-6">
        <ScheduleAvailabilityForm mode="create" onCancel={() => navigate('/analytics/schedule-availability')} onSuccess={() => navigate('/analytics/schedule-availability')} />
      </div>
    </div>
  );
};

export default ScheduleAvailabilityCreate;
