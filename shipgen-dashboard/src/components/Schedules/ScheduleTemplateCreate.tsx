import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import ScheduleTemplateForm from './forms/ScheduleTemplateForm';

const ScheduleTemplateCreate: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-3">
        <Link to="/analytics/schedule-templates" className="p-2 hover:bg-gray-100 rounded-lg transition">
          <ArrowLeft size={20} />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Create Schedule Template</h1>
          <p className="text-sm text-gray-600 mt-1">POST /int/v1/schedules-templates/</p>
        </div>
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-6">
        <ScheduleTemplateForm mode="create" onCancel={() => navigate('/analytics/schedule-templates')} onSuccess={() => navigate('/analytics/schedule-templates')} />
      </div>
    </div>
  );
};

export default ScheduleTemplateCreate;
