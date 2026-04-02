import React, { useEffect, useState } from 'react';
import { AlertCircle } from 'lucide-react';
import { issuesService } from '../../../services/issuesService';
import { formatMeta, parseMetaJson } from '../../../utils/contactHelpers';
import { formatTags, parseTags } from '../../../utils/issueHelpers';
import { PH } from '../../../constants/formPlaceholders';
import { useToast } from '../../ui/ToastProvider';
import { FormActions, FormContainer, FormField, FormSection, Input, Textarea } from '../../common/form';

interface IssueFormProps {
  mode: 'create' | 'edit';
  issueId?: string;
  onSuccess: () => Promise<void> | void;
  onCancel: () => void;
}

const IssueForm: React.FC<IssueFormProps> = ({ mode, issueId, onSuccess, onCancel }) => {
  const { showToast } = useToast();
  const [loading, setLoading] = useState(mode === 'edit');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    driver: '',
    location_json: '',
    category: '',
    type: '',
    report: '',
    priority: '',
    status: '',
    title: '',
    tags_csv: '',
    meta_json: '',
    resolved_at: '',
  });

  useEffect(() => {
    if (mode !== 'edit' || !issueId) return;
    const load = async () => {
      try {
        setLoading(true);
        setError(null);
        const i = await issuesService.getById(issueId);
        setFormData((prev) => ({
          ...prev,
          category: i.category ?? '',
          type: i.type ?? '',
          report: i.report ?? '',
          priority: i.priority ?? '',
          status: i.status ?? '',
          title: i.title ?? '',
          tags_csv: formatTags(i.tags),
          meta_json: formatMeta(i.meta),
          resolved_at: i.resolved_at ? i.resolved_at.slice(0, 16) : '',
        }));
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to load issue');
      } finally {
        setLoading(false);
      }
    };
    void load();
  }, [mode, issueId]);

  const field = (
    id: string,
    label: string,
    key: keyof typeof formData,
    multiline = false,
    datetime = false,
    placeholder?: string,
    fieldClassName?: string,
  ) => (
    <FormField label={label} htmlFor={id} className={fieldClassName}>
      {multiline ? (
        <Textarea
          id={id}
          rows={3}
          placeholder={placeholder}
          value={formData[key]}
          onChange={(e) => setFormData((p) => ({ ...p, [key]: e.target.value }))}
          className={key === 'meta_json' || key === 'location_json' ? 'font-mono text-sm' : undefined}
        />
      ) : (
        <Input
          id={id}
          type={datetime ? 'datetime-local' : 'text'}
          title={datetime ? PH.scheduledAtTitle : undefined}
          placeholder={placeholder}
          value={formData[key]}
          onChange={(e) => setFormData((p) => ({ ...p, [key]: e.target.value }))}
        />
      )}
    </FormField>
  );

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    let location: Record<string, unknown> | null = null;
    let meta: Record<string, unknown> | null = null;
    try {
      if (mode === 'create') {
        location = formData.location_json.trim() ? parseMetaJson(formData.location_json) : null;
      }
      meta = formData.meta_json.trim() ? parseMetaJson(formData.meta_json) : null;
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Invalid JSON');
      return;
    }

    try {
      setSaving(true);
      setError(null);
      if (mode === 'edit' && issueId) {
        await issuesService.updatePut(issueId, {
          category: formData.category.trim() || null,
          type: formData.type.trim() || null,
          report: formData.report.trim() || null,
          priority: formData.priority.trim() || null,
          status: formData.status.trim() || null,
          title: formData.title.trim() || null,
          tags: parseTags(formData.tags_csv),
          meta,
          resolved_at: formData.resolved_at ? new Date(formData.resolved_at).toISOString() : null,
        });
        showToast('Issue updated successfully', 'success');
      } else {
        await issuesService.create({
          driver: formData.driver.trim() || null,
          location,
          category: formData.category.trim() || null,
          type: formData.type.trim() || null,
          report: formData.report.trim() || null,
          priority: formData.priority.trim() || null,
          status: formData.status.trim() || null,
          title: formData.title.trim() || null,
          tags: parseTags(formData.tags_csv),
          meta,
        });
        showToast('Issue created successfully', 'success');
      }
      await onSuccess();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : `Failed to ${mode} issue`);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex h-40 items-center justify-center">
        <div className="h-10 w-10 animate-spin rounded-full border-b-2 border-blue-600" />
      </div>
    );
  }

  return (
    <FormContainer>
      <form onSubmit={submit} className="space-y-5">
        {error ? (
          <div className="flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        ) : null}
        <FormSection>
          {mode === 'create' ? (
            <p className="text-sm text-gray-500 md:col-span-2">OpenAPI IssueCreate has no required properties.</p>
          ) : null}
          {mode === 'create' ? field('issue-driver', 'driver', 'driver', false, false, PH.driverRefOptional) : null}
          {field('issue-category', 'category', 'category', false, false, PH.issueCategoryOptional)}
          {field('issue-type', 'type', 'type', false, false, PH.issueTypeOptional)}
          {field('issue-priority', 'priority', 'priority', false, false, PH.issuePriorityOptional)}
          {field('issue-status', 'status', 'status', false, false, PH.issueStatusOptional)}
          {field('issue-title', 'title', 'title', false, false, PH.issueTitleOptional, 'md:col-span-2')}
          {field('issue-report', 'report', 'report', true, false, PH.issueReportOptional, 'md:col-span-2')}
          {field('issue-tags', 'tags (comma separated)', 'tags_csv', false, false, PH.tagsCsvOptional)}
          {mode === 'create'
            ? field('issue-location', 'location (JSON object)', 'location_json', true, false, PH.jsonLocationOptional, 'md:col-span-2')
            : null}
          {field('issue-meta', 'meta (JSON object)', 'meta_json', true, false, PH.metaJsonOptional, 'md:col-span-2')}
          {mode === 'edit' ? field('issue-resolved', 'resolved_at', 'resolved_at', false, true, PH.isoStartOptional) : null}
        </FormSection>

        <FormActions
          onCancel={onCancel}
          saving={saving}
          submitLabel={mode === 'edit' ? 'Save (PUT)' : 'Create'}
        />
      </form>
    </FormContainer>
  );
};

export default IssueForm;
