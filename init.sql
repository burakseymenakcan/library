-- PostgreSQL Database Initialization Script
-- Bu script PostgreSQL container başlatıldığında otomatik çalışır

-- Users tablosu
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_staff BOOLEAN DEFAULT FALSE,
    is_superuser BOOLEAN DEFAULT FALSE,
    is_banned BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Books tablosu
CREATE TABLE IF NOT EXISTS books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    description TEXT,
    published_year INTEGER,
    isbn VARCHAR(50),
    category VARCHAR(100),
    cover_url TEXT,
    total_copies INTEGER DEFAULT 1,
    available_copies INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Loans tablosu
CREATE TABLE IF NOT EXISTS loans (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    borrowed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    due_date DATE,
    returned_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (book_id) REFERENCES books (id)
);

-- Admin kullanıcısını oluştur (şifre: admin)
INSERT INTO users (username, email, password_hash, is_staff, is_superuser) 
VALUES ('admin', 'admin@example.com', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', true, true)
ON CONFLICT (username) DO NOTHING;

-- Örnek kitaplar ekle
INSERT INTO books (title, author, description, published_year, isbn, category, total_copies, available_copies) VALUES
('A Game of Thrones', 'George R.R. Martin', 'The first book in the A Song of Ice and Fire series', 1996, '978-0553103540', 'Fantasy', 3, 3),
('A Clash of Kings', 'George R.R. Martin', 'The second book in the A Song of Ice and Fire series', 1998, '978-0553108033', 'Fantasy', 2, 2),
('A Storm of Swords', 'George R.R. Martin', 'The third book in the A Song of Ice and Fire series', 2000, '978-0553106633', 'Fantasy', 2, 2),
('A Feast for Crows', 'George R.R. Martin', 'The fourth book in the A Song of Ice and Fire series', 2005, '978-0553801507', 'Fantasy', 1, 1),
('A Dance with Dragons', 'George R.R. Martin', 'The fifth book in the A Song of Ice and Fire series', 2011, '978-0553801477', 'Fantasy', 1, 1)
ON CONFLICT DO NOTHING;

-- Veritabanı hazır mesajı
SELECT 'Library database initialized successfully!' as status;
