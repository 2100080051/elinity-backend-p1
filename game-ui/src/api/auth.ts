import { apiClient } from './client';

export async function login(email: string, password: string): Promise<any> {
    const res = await apiClient.post('/auth/login', { email, password });
    return res.data;
}

export async function register(email: string, password: string, phone: string = ""): Promise<any> {
    const res = await apiClient.post('/auth/register', { email, password, phone });
    return res.data;
}
