import type { MockContact } from '../mocks/data/contacts';

/** Route param id: prefer uuid, else numeric id string */
export function getContactRouteId(contact: MockContact): string {
  if (contact.uuid) return contact.uuid;
  if (contact.id != null) return String(contact.id);
  return '';
}

export function formatMeta(meta: Record<string, unknown> | null): string {
  if (meta == null) return '';
  try {
    return JSON.stringify(meta, null, 2);
  } catch {
    return '';
  }
}

export function parseMetaJson(raw: string): Record<string, unknown> | null {
  const t = raw.trim();
  if (!t) return null;
  try {
    const v = JSON.parse(t) as unknown;
    if (v !== null && typeof v === 'object' && !Array.isArray(v)) {
      return v as Record<string, unknown>;
    }
    return null;
  } catch {
    throw new Error('meta must be valid JSON object');
  }
}
