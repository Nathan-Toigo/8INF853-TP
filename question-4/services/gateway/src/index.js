const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');

const app = express();
const PORT = process.env.PORT || 3000;

const CUSTOMERS_URL = process.env.CUSTOMERS_SERVICE_URL || 'http://customers:3001';
const ACCOUNTS_URL = process.env.ACCOUNTS_SERVICE_URL || 'http://accounts:3002';
const TRANSACTIONS_URL = process.env.TRANSACTIONS_SERVICE_URL || 'http://transactions:3003';

app.get('/health', (_req, res) => {
  res.json({ status: 'ok', service: 'gateway' });
});

app.get('/', (_req, res) => {
  res.json({
    name: 'BanqueExpress API Gateway',
    version: '1.0.0',
    endpoints: {
      customers: '/api/customers',
      accounts: '/api/accounts',
      transactions: '/api/transactions',
    },
  });
});

app.use(
  createProxyMiddleware({
    target: CUSTOMERS_URL,
    changeOrigin: true,
    pathFilter: '/api/customers',
    pathRewrite: { '^/api/customers': '/customers' },
  })
);

app.use(
  createProxyMiddleware({
    target: ACCOUNTS_URL,
    changeOrigin: true,
    pathFilter: '/api/accounts',
    pathRewrite: { '^/api/accounts': '/accounts' },
  })
);

app.use(
  createProxyMiddleware({
    target: TRANSACTIONS_URL,
    changeOrigin: true,
    pathFilter: '/api/transactions',
    pathRewrite: { '^/api/transactions': '/transactions' },
  })
);

app.listen(PORT, () => console.log(`[gateway] API Gateway démarrée sur le port ${PORT}`));
