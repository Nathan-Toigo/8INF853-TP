const express = require('express');
const { Pool } = require('pg');

const app = express();
const PORT = process.env.PORT || 3001;

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

app.use(express.json());

app.get('/health', async (_req, res) => {
  try {
    await pool.query('SELECT 1');
    res.json({ status: 'ok', service: 'customers' });
  } catch {
    res.status(503).json({ status: 'error', service: 'customers' });
  }
});

app.get('/customers', async (_req, res) => {
  const { rows } = await pool.query('SELECT * FROM customers ORDER BY id');
  res.json(rows);
});

app.get('/customers/:id', async (req, res) => {
  const { rows } = await pool.query('SELECT * FROM customers WHERE id = $1', [req.params.id]);
  if (rows.length === 0) return res.status(404).json({ error: 'Client introuvable' });
  res.json(rows[0]);
});

app.post('/customers', async (req, res) => {
  const { first_name, last_name, email } = req.body;
  if (!first_name || !last_name || !email) {
    return res.status(400).json({ error: 'first_name, last_name et email sont requis' });
  }
  const { rows } = await pool.query(
    'INSERT INTO customers (first_name, last_name, email) VALUES ($1, $2, $3) RETURNING *',
    [first_name, last_name, email]
  );
  res.status(201).json(rows[0]);
});

app.put('/customers/:id', async (req, res) => {
  const { first_name, last_name, email } = req.body;
  const { rows } = await pool.query(
    'UPDATE customers SET first_name = COALESCE($1, first_name), last_name = COALESCE($2, last_name), email = COALESCE($3, email) WHERE id = $4 RETURNING *',
    [first_name, last_name, email, req.params.id]
  );
  if (rows.length === 0) return res.status(404).json({ error: 'Client introuvable' });
  res.json(rows[0]);
});

app.delete('/customers/:id', async (req, res) => {
  const { rowCount } = await pool.query('DELETE FROM customers WHERE id = $1', [req.params.id]);
  if (rowCount === 0) return res.status(404).json({ error: 'Client introuvable' });
  res.status(204).send();
});

app.listen(PORT, () => console.log(`[customers] Service démarré sur le port ${PORT}`));
