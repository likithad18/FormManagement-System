import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

export interface Submission {
  id: number;
  full_name: string;
  email: string;
  phone_number: string;
  age: number;
  address?: string;
  preferred_contact: 'Email' | 'Phone' | 'Both';
  created_at: string;
  updated_at: string;
}

export interface SubmissionInput {
  full_name: string;
  email: string;
  phone_number: string;
  age: number;
  address?: string;
  preferred_contact: 'Email' | 'Phone' | 'Both';
}

export interface PaginatedSubmissions {
  total: number;
  items: Submission[];
}

export async function getSubmissions(params?: Record<string, any>) {
  const res = await axios.get<PaginatedSubmissions>(`${API_BASE}/api/submissions/`, { params });
  return res.data;
}

export async function getSubmission(id: number) {
  const res = await axios.get<Submission>(`${API_BASE}/api/submissions/${id}`);
  return res.data;
}

export async function createSubmission(data: SubmissionInput) {
  const res = await axios.post<Submission>(`${API_BASE}/api/submissions/`, data);
  return res.data;
}

export async function updateSubmission(id: number, data: SubmissionInput) {
  const res = await axios.put<Submission>(`${API_BASE}/api/submissions/${id}`, data);
  return res.data;
}

export async function deleteSubmission(id: number) {
  await axios.delete(`${API_BASE}/api/submissions/${id}`);
} 