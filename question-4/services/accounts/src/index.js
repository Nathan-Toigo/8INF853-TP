const express = require('express');
const { Pool } = require('pg');

const app = express();
const PORT = process.env.PORT || 3002;

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

app.use(express.json());

app.get('/health', async (_req, res) => {
  try {
    await pool.query('SELECT 1');
    res.json({ status: 'ok', service: 'accounts' });
  } catch {
    res.status(503).json({ status: 'error', service: 'accounts' });
  }
});

app.get('/accounts', async (_req, res) => {
  const { rows } = await pool.query('SELECT * FROM accounts ORDER BY id');
  res.json(rows);
});

app.get('/accounts/customer/:customerId', async (req, res) => {
  const { rows } = await pool.query(
    'SELECT * FROM accounts WHERE customer_id = $1 ORDER BY id',
    [req.params.customerId]
  );
  res.json(rows);
});

app.get('/accounts/:id', async (req, res) => {
  const { rows } = await pool.query('SELECT * FROM accounts WHERE id = $1', [req.params.id]);
  if (rows.length === 0) return res.status(404).json({ error: 'Compte introuvable' });
  res.json(rows[0]);
});

app.post('/accounts', async (req, res) => {
  const { customer_id, account_number, balance = 0, currency = 'EUR' } = req.body;
  if (!customer_id || !account_number) {
    return res.status(400).json({ error: 'customer_id et account_number sont requis' });
  }
  const { rows } = await pool.query(
    'INSERT INTO accounts (customer_id, account_number, balance, currency) VALUES ($1, $2, $3, $4) RETURNING *',
    [customer_id, account_number, balance, currency]
  );
  res.status(201).json(rows[0]);
});

app.patch('/accounts/:id/balance', async (req, res) => {
  const { amount } = req.body;
  if (amount === undefined) return res.status(400).json({ error: 'amount est requis' });

  const { rows: current } = await pool.query('SELECT * FROM accounts WHERE id = $1', [req.params.id]);
  if (current.length === 0) return res.status(404).json({ error: 'Compte introuvable' });

  const newBalance = parseFloat(current[0].balance) + parseFloat(amount);
  if (newBalance < 0) return res.status(400).json({ error: 'Solde insuffisant' });

  const { rows } = await pool.query(
    'UPDATE accounts SET balance = $1 WHERE id = $2 RETURNING *',
    [newBalance, req.params.id]
  );
  res.json(rows[0]);
});

app.listen(PORT, () => console.log(`[accounts] Service démarré sur le port ${PORT}`));
