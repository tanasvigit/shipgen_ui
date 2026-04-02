import type { MockIssue } from '../mocks/data/issues';

export function getIssueRouteId(issue: MockIssue): string {
  if (issue.uuid) return issue.uuid;
  if (issue.id != null) return String(issue.id);
  return '';
}

export function parseTags(raw: string): string[] | null {
  const parts = raw
    .split(',')
    .map((x) => x.trim())
    .filter((x) => x.length > 0);
  return parts.length ? parts : null;
}

export function formatTags(tags: string[] | null): string {
  if (!tags || tags.length === 0) return '';
  return tags.join(', ');
}
