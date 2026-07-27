const express = require('express');
const axios = require('axios');
const { Pool } = require('pg');

const app = express();
const PORT = process.env.PORT || 3003;
const ACCOUNTS_URL = process.env.ACCOUNTS_SERVICE_URL || 'http://accounts:3002';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

app.use(express.json());

async function updateBalance(accountId, amount) {
  const { data } = await axios.patch(`${ACCOUNTS_URL}/accounts/${accountId}/balance`, { amount });
  return data;
}

async function getAccount(accountId) {
  const { data } = await axios.get(`${ACCOUNTS_URL}/accounts/${accountId}`);
  return data;
}

app.get('/health', async (_req, res) => {
  try {
    await pool.query('SELECT 1');
    res.json({ status: 'ok', service: 'transactions' });
  } catch {
    res.status(503).json({ status: 'error', service: 'transactions' });
  }
});

app.get('/transactions', async (_req, res) => {
  const { rows } = await pool.query('SELECT * FROM transactions ORDER BY created_at DESC');
  res.json(rows);
});

app.get('/transactions/account/:accountId', async (req, res) => {
  const { rows } = await pool.query(
    `SELECT * FROM transactions
     WHERE from_account_id = $1 OR to_account_id = $1
     ORDER BY created_at DESC`,
    [req.params.accountId]
  );
  res.json(rows);
});

app.post('/transactions/deposit', async (req, res, next) => {
  try {
  const { account_id, amount, description } = req.body;
  if (!account_id || !amount || amount <= 0) {
    return res.status(400).json({ error: 'account_id et amount (> 0) sont requis' });
  }

  await getAccount(account_id);
  const updated = await updateBalance(account_id, amount);

  const { rows } = await pool.query(
    `INSERT INTO transactions (type, to_account_id, amount, description)
     VALUES ('DEPOSIT', $1, $2, $3) RETURNING *`,
    [account_id, amount, description || 'Dépôt']
  );

  res.status(201).json({ transaction: rows[0], account: updated });
  } catch (err) { next(err); }
});

app.post('/transactions/withdraw', async (req, res, next) => {
  try {
  const { account_id, amount, description } = req.body;
  if (!account_id || !amount || amount <= 0) {
    return res.status(400).json({ error: 'account_id et amount (> 0) sont requis' });
  }

  const account = await getAccount(account_id);
  if (parseFloat(account.balance) < amount) {
    return res.status(400).json({ error: 'Solde insuffisant' });
  }

  const updated = await updateBalance(account_id, -amount);

  const { rows } = await pool.query(
    `INSERT INTO transactions (type, from_account_id, amount, description)
     VALUES ('WITHDRAW', $1, $2, $3) RETURNING *`,
    [account_id, amount, description || 'Retrait']
  );

  res.status(201).json({ transaction: rows[0], account: updated });
  } catch (err) { next(err); }
});

app.post('/transactions/transfer', async (req, res, next) => {
  try {
  const { from_account_id, to_account_id, amount, description } = req.body;
  if (!from_account_id || !to_account_id || !amount || amount <= 0) {
    return res.status(400).json({ error: 'from_account_id, to_account_id et amount (> 0) sont requis' });
  }
  if (from_account_id === to_account_id) {
    return res.status(400).json({ error: 'Les comptes source et destination doivent être différents' });
  }

  const fromAccount = await getAccount(from_account_id);
  if (parseFloat(fromAccount.balance) < amount) {
    return res.status(400).json({ error: 'Solde insuffisant sur le compte source' });
  }

  await getAccount(to_account_id);

  const fromUpdated = await updateBalance(from_account_id, -amount);
  const toUpdated = await updateBalance(to_account_id, amount);

  const { rows } = await pool.query(
    `INSERT INTO transactions (type, from_account_id, to_account_id, amount, description)
     VALUES ('TRANSFER', $1, $2, $3, $4) RETURNING *`,
    [from_account_id, to_account_id, amount, description || 'Virement']
  );

  res.status(201).json({
    transaction: rows[0],
    from_account: fromUpdated,
    to_account: toUpdated,
  });
  } catch (err) { next(err); }
});

app.use((err, _req, res, _next) => {
  const status = err.response?.status || 500;
  const message = err.response?.data?.error || err.message || 'Erreur interne';
  res.status(status).json({ error: message });
});

app.listen(PORT, () => console.log(`[transactions] Service démarré sur le port ${PORT}`));
