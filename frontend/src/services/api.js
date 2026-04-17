// API service for user data persistence
const API_BASE_URL = 'http://127.0.0.1:8000'; // FastAPI backend

const getHeaders = (withAuth = true) => {
  const headers = { 'Content-Type': 'application/json' };
  if (withAuth) {
    const token = localStorage.getItem('knowyourrights_token');
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }
  }
  return headers;
};

export const api = {
  async signup(payload) {
    const response = await fetch(`${API_BASE_URL}/auth/signup`, {
      method: 'POST',
      headers: getHeaders(false),
      body: JSON.stringify(payload)
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Signup failed');
    }
    return response.json();
  },

  async login(payload) {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: getHeaders(false),
      body: JSON.stringify(payload)
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Login failed');
    }
    return response.json();
  },

  async getCurrentUser() {
    const response = await fetch(`${API_BASE_URL}/users/me`, {
      headers: getHeaders(true)
    });
    if (!response.ok) throw new Error('Failed to load user');
    return response.json();
  },

  async updateUserStats(stats) {
    const response = await fetch(`${API_BASE_URL}/api/user/stats`, {
      method: 'PUT',
      headers: getHeaders(true),
      body: JSON.stringify(stats)
    });
    return response.json();
  },

  async addCompletedScenario(scenario) {
    const response = await fetch(`${API_BASE_URL}/api/user/completed-scenarios`, {
      method: 'POST',
      headers: getHeaders(true),
      body: JSON.stringify(scenario)
    });
    return response.json();
  },

  async addXPEntry(entry) {
    const response = await fetch(`${API_BASE_URL}/api/user/xp-history`, {
      method: 'POST',
      headers: getHeaders(true),
      body: JSON.stringify(entry)
    });
    return response.json();
  },

  async getUserProgress() {
    const response = await fetch(`${API_BASE_URL}/api/user/progress`, {
      headers: getHeaders(true)
    });
    return response.json();
  },

  async getQuestions(domain = '', difficulty = '') {
    const params = new URLSearchParams();
    if (domain) params.append('domain', domain);
    if (difficulty) params.append('difficulty', difficulty);

    const response = await fetch(`${API_BASE_URL}/questions?${params}`);
    return response.json();
  },

  logout() {
    localStorage.removeItem('authToken');
  }
};