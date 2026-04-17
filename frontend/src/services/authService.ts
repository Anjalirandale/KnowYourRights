import { api } from './api';

const SESSION_KEY = 'knowyourrights_session';
const TOKEN_KEY = 'knowyourrights_token';

export const getCurrentUser = () => {
  try {
    const stored = localStorage.getItem(SESSION_KEY);
    return stored ? (JSON.parse(stored) as { name: string; email: string }) : null;
  } catch {
    return null;
  }
};

export const isAuthenticated = () => Boolean(localStorage.getItem(TOKEN_KEY));

const saveSession = (name: string, email: string, token: string) => {
  localStorage.setItem(SESSION_KEY, JSON.stringify({ name, email }));
  localStorage.setItem(TOKEN_KEY, token);
};

export const registerUser = async (name: string, email: string, password: string) => {
  const tokenResponse = await api.signup({ name, email, password });
  saveSession(name, email, tokenResponse.access_token);
  return { name, email };
};

export const loginUser = async (email: string, password: string) => {
  const tokenResponse = await api.login({ email, password });
  localStorage.setItem(TOKEN_KEY, tokenResponse.access_token);
  const user = await api.getCurrentUser();
  saveSession(user.name, user.email, tokenResponse.access_token);
  return user;
};

export const logoutUser = () => {
  localStorage.removeItem(SESSION_KEY);
  localStorage.removeItem(TOKEN_KEY);
  api.logout();
};
