import React, { useEffect, useState } from 'react';
import { Link, useLocation, useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, BookUser, AlertCircle, Pencil, Trash2 } from 'lucide-react';
import { contactsService } from '../../services/contactsService';
import type { MockContact } from '../../mocks/data/contacts';
import { formatMeta } from '../../utils/contactHelpers';

const ContactDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  const isEmbedded = new URLSearchParams(location.search).get('embed') === '1';
  const [contact, setContact] = useState<MockContact | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) loadContact();
  }, [id]);

  const loadContact = async () => {
    try {
      setLoading(true);
      const response = await contactsService.getById(id as string);
      setContact(response);
      setLoading(false);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load contact';
      setError(message);
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!id) return;
    if (!window.confirm('Delete this contact? This cannot be undone.')) return;
    try {
      await contactsService.remove(id);
      navigate('/fleet/contacts');
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to delete contact';
      setError(message);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
      </div>
    );
  }

  if (error || !contact) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center space-x-2">
        <AlertCircle size={20} />
        <span>{error || 'Contact not found'}</span>
      </div>
    );
  }

  const row = (label: string, value: React.ReactNode) => (
    <div>
      <div className="text-xs font-medium text-gray-500 uppercase">{label}</div>
      <div className="text-sm text-gray-900 mt-1 break-all">{value ?? '—'}</div>
    </div>
  );

  return (
    <div className="space-y-6">
      {!isEmbedded ? (
        <div className="flex items-center justify-between flex-wrap gap-4">
        <div className="flex items-center space-x-4">
          <Link to="/fleet/contacts" className="p-2 hover:bg-gray-100 rounded-lg transition">
            <ArrowLeft size={20} />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <BookUser size={24} className="text-blue-600" />
              Contact
            </h1>
            <p className="text-sm text-gray-600 mt-1">GET /fleetops/v1/contacts/&#123;id&#125;</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          {!isEmbedded ? (
            <Link
              to="/fleet/contacts"
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              <Pencil size={18} />
              <span>Open List To Edit</span>
            </Link>
          ) : null}
          <button
            type="button"
            onClick={handleDelete}
            className="flex items-center space-x-2 px-4 py-2 border border-red-200 text-red-700 rounded-lg hover:bg-red-50 transition"
          >
            <Trash2 size={18} />
            <span>Delete</span>
          </button>
        </div>
        </div>
      ) : null}

      <div className="bg-white rounded-xl border border-gray-200 p-6 space-y-6">
        <h2 className="text-lg font-semibold text-gray-900">ContactOut fields</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {row('uuid', contact.uuid)}
          {row('public_id', contact.public_id)}
          {row('company_uuid', contact.company_uuid)}
          {row('user_uuid', contact.user_uuid)}
          {row('name', contact.name)}
          {row('title', contact.title)}
          {row('email', contact.email)}
          {row('phone', contact.phone)}
          {row('type', contact.type)}
          {row('slug', contact.slug)}
          {row('id', contact.id)}
          {row('created_at', contact.created_at)}
          {row('updated_at', contact.updated_at)}
        </div>
        <div>
          <div className="text-xs font-medium text-gray-500 uppercase mb-1">meta</div>
          <pre className="text-sm bg-gray-50 border border-gray-100 rounded-lg p-4 overflow-x-auto whitespace-pre-wrap">
            {contact.meta == null ? '—' : formatMeta(contact.meta)}
          </pre>
        </div>
      </div>
    </div>
  );
};

export default ContactDetail;
