export const colors = ['#a93f36', '#34658a', '#8a681d', '#67508e', '#347268'];
export const colorNames = ['Rosso', 'Blu', 'Ocra', 'Viola', 'Verde'];
export const names = ['Volpe', 'Falco', 'Lince', 'Cobra', 'Lupo'];
export async function api(path, options = {}) {
  let response;
  try {
    response = await fetch(`/api${path}`, {
      ...options,
      headers: { 'Content-Type': 'application/json', ...options.headers }
    });
  } catch {
    throw new Error('Connessione interrotta. Controlla la rete e riprova.');
  }
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = new Error(
      typeof data.detail === 'string'
        ? data.detail
        : 'Controlla i valori inseriti e riprova.'
    );
    error.status = response.status;
    throw error;
  }
  return data;
}
export const storage = {
  get(key) {
    try {
      return localStorage.getItem(key) || '';
    } catch {
      return '';
    }
  },
  set(key, value) {
    try {
      localStorage.setItem(key, value);
    } catch {
      /* Private mode: credentials remain usable in the current session. */
    }
  }
};
