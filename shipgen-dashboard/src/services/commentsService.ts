import { apiClient } from './apiClient';

type UnknownRecord = Record<string, unknown>;

export interface UiComment {
  id: string;
  body: string;
  user: string;
  created_at: string;
}

export interface CreateCommentInput {
  body: string;
  subject_uuid: string;
  subject_type: string;
}

const mapComment = (row: UnknownRecord): UiComment => ({
  id: String(row.uuid ?? row.public_id ?? row.id ?? ''),
  body: String(row.content ?? row.comment ?? row.body ?? row.message ?? ''),
  user: String(row.author_uuid ?? row.user_uuid ?? row.user ?? ''),
  created_at: String(row.created_at ?? ''),
});

class CommentsService {
  async list(params: { limit?: number; offset?: number } = {}): Promise<UiComment[]> {
    const payload = await apiClient.get<UnknownRecord[]>('/int/v1/comments/', {
      limit: params.limit ?? 100,
      offset: params.offset ?? 0,
    });
    return Array.isArray(payload) ? payload.map((x) => mapComment((x ?? {}) as UnknownRecord)) : [];
  }

  async create(input: CreateCommentInput): Promise<UiComment> {
    const payload = await apiClient.post<UnknownRecord>('/int/v1/comments/', {
      content: input.body,
      subject_uuid: input.subject_uuid,
      subject_type: input.subject_type,
    });
    return mapComment((payload ?? {}) as UnknownRecord);
  }

  async remove(id: string): Promise<void> {
    await apiClient.delete(`/int/v1/comments/${id}`);
  }
}

export const commentsService = new CommentsService();
