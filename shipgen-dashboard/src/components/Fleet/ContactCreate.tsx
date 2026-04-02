import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import ContactForm from './forms/ContactForm';

const ContactCreate: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <Link to="/fleet/contacts" className="p-2 hover:bg-gray-100 rounded-lg transition">
          <ArrowLeft size={20} />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Create Contact</h1>
          <p className="text-sm text-gray-600 mt-1">POST /fleetops/v1/contacts — body: ContactCreate</p>
        </div>
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-6">
        <ContactForm mode="create" onCancel={() => navigate('/fleet/contacts')} onSuccess={() => navigate('/fleet/contacts')} />
      </div>
    </div>
  );
};

export default ContactCreate;
