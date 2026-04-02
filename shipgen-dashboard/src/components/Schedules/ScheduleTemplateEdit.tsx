import React from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import ScheduleTemplateForm from './forms/ScheduleTemplateForm';

const ScheduleTemplateEdit: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-3">
        <Link to="/analytics/schedule-templates" className="p-2 hover:bg-gray-100 rounded-lg transition">
          <ArrowLeft size={20} />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Edit Schedule Template</h1>
          <p className="text-sm text-gray-600 mt-1">PATCH /int/v1/schedules-templates/{'{id}'}</p>
        </div>
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-6">
        <ScheduleTemplateForm mode="edit" templateId={id} onCancel={() => navigate('/analytics/schedule-templates')} onSuccess={() => navigate('/analytics/schedule-templates')} />
      </div>
    </div>
  );
};

export default ScheduleTemplateEdit;
