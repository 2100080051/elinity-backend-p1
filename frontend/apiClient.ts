/*
 * Clean, well-structured TypeScript API client stub.
 * - Central request helper with error handling
 * - Minimal, clear types that map to backend schemas (expand as needed)
 * - Designed to be a tidy starting point for frontend developers
 */

/* ----------------------------- Types ----------------------------- */
export type Token = { access_token: string; refresh_token: string; token_type: string };

export type PersonalInfo = { first_name?: string; last_name?: string; age?: number | any; gender?: string; location?: string };

export type User = { id: string; email?: string | null; phone?: string | null; role?: string; last_login?: string | null; personal_info?: PersonalInfo | null };

export type JournalCreate = { title?: string; body?: string };
export type JournalResponse = JournalCreate & { id: string; tenant: string; created_at?: string };

export type ChatCreate = { message: string; receiver?: string; group?: string };
export type Chat = ChatCreate & { id: string; sender: string };

export type GroupCreate = { name: string; description?: string; type?: string; asset_url?: string };
export type Group = GroupCreate & { id: string; tenant: string };

export type QuestionCard = { id: string; question: string; choices?: string[] };
export type RecommendedUser = { tenant: User; score: number; ai_insight?: string };

/* ------------------------ Utility / Helpers ---------------------- */
async function handleResponse<T>(res: Response): Promise<T> {
  if (res.ok) return (await res.json()) as T;
  const text = await res.text();
  let message = `Request failed: ${res.status}`;
  try {
    const body = JSON.parse(text);
    message = body.detail || body.message || JSON.stringify(body);
  } catch {
    if (text) message = text;
  }
  throw new Error(message);
}

function jsonHeaders(token?: string): HeadersInit {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  return headers;
}

/* ----------------------------- Client --------------------------- */
export class ApiClient {
  baseUrl: string;
  getToken?: () => string | undefined | Promise<string | undefined>;

  constructor(baseUrl = '', getToken?: () => string | undefined | Promise<string | undefined>) {
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this.getToken = getToken;
  }

  private async tokenValue(): Promise<string | undefined> {
    if (!this.getToken) return undefined;
    const t = this.getToken();
    return t instanceof Promise ? await t : t;
  }

  private async requestJson<T>(path: string, opts: RequestInit = {}): Promise<T> {
    const token = await this.tokenValue();
    opts.headers = Object.assign({}, opts.headers || {}, token ? { Authorization: `Bearer ${token}` } : {});
    const res = await fetch(this.baseUrl + path, opts);
    return handleResponse<T>(res);
  }

  // --------- Auth ---------
  async loginForm(username: string, password: string): Promise<Token> {
    const body = new URLSearchParams();
    body.append('username', username);
    body.append('password', password);
    const res = await fetch(`${this.baseUrl}/auth/token`, { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: body.toString() });
    return handleResponse<Token>(res);
  }

  async loginJson(emailOrPhone: string, password: string): Promise<Token> {
    return this.requestJson<Token>('/auth/login', { method: 'POST', body: JSON.stringify({ email: emailOrPhone, password }), headers: jsonHeaders() });
  }

  async register(email?: string, phone?: string, password?: string): Promise<Token> {
    return this.requestJson<Token>('/auth/register', { method: 'POST', body: JSON.stringify({ email, phone, password }), headers: jsonHeaders() });
  }

  async refresh(refresh_token: string): Promise<Token> {
    return this.requestJson<Token>('/auth/refresh', { method: 'POST', body: JSON.stringify({ refresh_token }), headers: jsonHeaders() });
  }

  // --------- Profile / Me ---------
  async getMe(): Promise<User> {
    return this.requestJson<User>('/me');
  }

  async updatePersonalInfo(payload: PersonalInfo): Promise<PersonalInfo> {
    return this.requestJson<PersonalInfo>('/me/personal-info/', { method: 'PUT', body: JSON.stringify(payload), headers: jsonHeaders(await this.tokenValue()) });
  }

  async getUserById(userId: string): Promise<User> {
    return this.requestJson<User>(`/${encodeURIComponent(userId)}`);
  }

  // --------- Journals ---------
  async getJournals(): Promise<JournalResponse[]> {
    return this.requestJson<JournalResponse[]>('/');
  }

  async createJournal(payload: JournalCreate): Promise<JournalResponse> {
    return this.requestJson<JournalResponse>('/', { method: 'POST', body: JSON.stringify(payload), headers: jsonHeaders(await this.tokenValue()) });
  }

  // --------- Chats ---------
  async getChats(): Promise<Chat[]> {
    return this.requestJson<Chat[]>('/chats/');
  }

  async createChat(payload: ChatCreate): Promise<Chat> {
    return this.requestJson<Chat>('/chats/', { method: 'POST', body: JSON.stringify(payload), headers: jsonHeaders(await this.tokenValue()) });
  }

  // --------- Groups ---------
  async getGroups(): Promise<Group[]> {
    return this.requestJson<Group[]>('/groups/');
  }

  async createGroup(payload: GroupCreate): Promise<Group> {
    return this.requestJson<Group>('/groups/', { method: 'POST', body: JSON.stringify(payload), headers: jsonHeaders(await this.tokenValue()) });
  }

  // --------- Uploads (multipart) ---------
  async uploadFile(file: File): Promise<{ url: string }> {
    const token = await this.tokenValue();
    const form = new FormData();
    form.append('file', file);
    const res = await fetch(`${this.baseUrl}/upload-file/`, { method: 'POST', headers: token ? { Authorization: `Bearer ${token}` } : {}, body: form });
    return handleResponse<{ url: string }>(res);
  }

  // --------- Voice onboarding ---------
  async startVoiceOnboarding(): Promise<{ tenant_id: string; message: string; audio_filename?: string }> {
    return this.requestJson('/voice/start', { method: 'POST' });
  }

  async continueVoiceOnboardingWithText(text: string) {
    return this.requestJson('/voice/continue', { method: 'PUT', body: JSON.stringify({ text }), headers: jsonHeaders(await this.tokenValue()) });
  }

  async continueVoiceOnboardingWithFile(file: File) {
    const token = await this.tokenValue();
    const form = new FormData();
    form.append('file', file);
    const res = await fetch(`${this.baseUrl}/voice/continue`, { method: 'PUT', headers: token ? { Authorization: `Bearer ${token}` } : {}, body: form });
    return handleResponse(res);
  }

  // --------- Question cards ---------
  async generateCards(count = 5): Promise<QuestionCard[]> {
    return this.requestJson<QuestionCard[]>(`/cards/?count=${count}`);
  }

  // --------- Recommendations ---------
  async getRecommendationsSearch(query: string): Promise<RecommendedUser[]> {
    return this.requestJson<RecommendedUser[]>(`/recommendations/search?query=${encodeURIComponent(query)}`);
  }
}

export default ApiClient;
