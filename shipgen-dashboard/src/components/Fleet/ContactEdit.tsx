import React from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import ContactForm from './forms/ContactForm';

const ContactEdit: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <Link to={`/fleet/contacts/${id}`} className="p-2 hover:bg-gray-100 rounded-lg transition">
          <ArrowLeft size={20} />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Edit Contact</h1>
          <p className="text-sm text-gray-600 mt-1">PATCH /fleetops/v1/contacts/&#123;id&#125; — body: ContactUpdate</p>
        </div>
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-6">
        <ContactForm mode="edit" contactId={id} onCancel={() => navigate('/fleet/contacts')} onSuccess={() => navigate('/fleet/contacts')} />
      </div>
    </div>
  );
};

export default ContactEdit;
