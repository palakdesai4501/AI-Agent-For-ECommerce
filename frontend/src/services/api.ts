import type { ChatRequest, AgentResponse, AgentInfo } from '../types';

const API_BASE_URL = (import.meta.env?.VITE_API_BASE_URL as string | undefined) || 'http://localhost:5000/api';

export async function chatWithAgent(request: ChatRequest): Promise<AgentResponse> {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
}

export async function getAgentInfo(): Promise<AgentInfo> {
  const response = await fetch(`${API_BASE_URL}/agent/info`);

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
}

export async function explainProduct(productId: string, query: string): Promise<string> {
  const response = await fetch(`${API_BASE_URL}/explain/${productId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query }),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data = await response.json();
  return data.explanation;
}