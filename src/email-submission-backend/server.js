const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const sqlite3 = require('sqlite3').verbose();

const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors());


// Enable CORS for all requests
app.use(cors({
  origin: 'http://localhost:3000',
  methods: 'GET,POST,PUT,DELETE',
  credentials: true,
}));

// Use body-parser to parse JSON bodies into JS objects
app.use(bodyParser.json());

// Connect to SQLite database
const db = new sqlite3.Database('./emails.db', (err) => {
  if (err) {
    console.error('Could not connect to database', err);
  } else {
    console.log('Connected to the SQLite database.');
  }
});

// Create emails table if it doesn't exist
db.run('CREATE TABLE IF NOT EXISTS emails(id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT)', (err) => {
  if (err) {
    console.error('Could not create table', err);
  }
});

// API endpoint to handle email submissions
app.post('/api/subscribe', (req, res) => {
  const { email } = req.body;

  if (!email) {
    return res.status(400).json({ message: 'Email is required' });
  }

  db.run('INSERT INTO emails(email) VALUES(?)', [email], function (err) {
    if (err) {
      console.error('Error storing email:', err);
      return res.status(500).json({ message: 'Failed to store email' });
    }
    res.status(200).json({ message: 'Email stored successfully' });
  });
});

// Start the server
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
