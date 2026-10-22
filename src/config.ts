const MARKETING_API_BASE = import.meta.env.VITE_MARKETING_API ?? 'http://localhost:8080';
const VENTAS_API_BASE = import.meta.env.VITE_VENTAS_API ?? 'http://localhost:8080';

export const API = {
  marketing: {
    base: MARKETING_API_BASE,
    campanias: `${MARKETING_API_BASE}/api/campanias`,
    leads: `${MARKETING_API_BASE}/api/leads`,
    empresas: `${MARKETING_API_BASE}/api/empresas`,
    productos: `${MARKETING_API_BASE}/api/productos`,
    canales: `${MARKETING_API_BASE}/api/canales`,
  },
  ventas: {
    base: VENTAS_API_BASE,
    oportunidades: `${VENTAS_API_BASE}/oportunidades`,
    clientes: `${VENTAS_API_BASE}/clientes`,
    empresas: `${VENTAS_API_BASE}/empresas`,
    productos: `${VENTAS_API_BASE}/productos`,
  },
} as const;