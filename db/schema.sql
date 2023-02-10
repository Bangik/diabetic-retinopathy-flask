DROP TABLE IF EXISTS posts;

CREATE TABLE retina (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  path TEXT NOT NULL,
  name TEXT NOT NULL,
  result TEXT NOT NULL,
  probability TEXT NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT (datetime('now','localtime'))
);