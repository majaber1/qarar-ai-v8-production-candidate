// Mirrors backend/app/main.py's _security_check(): a development convenience credential must
// never silently work outside development. NODE_ENV==='production' always wins over the env var.
export function devAutoLoginKey(): string {
  if (process.env.NODE_ENV === 'production') {
    if (process.env.QARAR_DEV_AUTO_LOGIN_KEY) {
      // eslint-disable-next-line no-console
      console.error('[qarar] QARAR_DEV_AUTO_LOGIN_KEY is set in a production build and is being ignored. Remove it from the environment.');
    }
    return '';
  }
  return process.env.QARAR_DEV_AUTO_LOGIN_KEY || '';
}
