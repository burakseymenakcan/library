from nicegui import ui, app
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import os

# PostgreSQL Database setup
def init_db():
    # PostgreSQL bağlantı bilgileri
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'library')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
    
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                is_staff BOOLEAN DEFAULT FALSE,
                is_superuser BOOLEAN DEFAULT FALSE,
                is_banned BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # is_banned sütunu zaten tabloda tanımlı olduğu için kontrol etmeye gerek yok
        print("ℹ️ is_banned sütunu tabloda tanımlı")
        
        cursor.execute('''
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
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS loans (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                book_id INTEGER NOT NULL,
                borrowed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                due_date DATE,
                returned_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (book_id) REFERENCES books (id)
            )
        ''')
        
        # Create admin user if not exists
        cursor.execute('SELECT * FROM users WHERE username = %s', ('admin',))
        if not cursor.fetchone():
            import hashlib
            admin_password_hash = hashlib.sha256('admin'.encode()).hexdigest()
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, is_staff, is_superuser)
                VALUES (%s, %s, %s, %s, %s)
            ''', ('admin', 'admin@example.com', admin_password_hash, True, True))
        
        conn.commit()
        conn.close()
        print("✅ PostgreSQL veritabanı başarıyla başlatıldı!")
        
        # Kitap verilerini ekle
        add_sample_books()
        
    except psycopg2.OperationalError as e:
        print(f"❌ PostgreSQL bağlantı hatası: {e}")
        print("📝 Lütfen PostgreSQL'in çalıştığından ve bağlantı bilgilerinin doğru olduğundan emin olun.")
        print("🔧 Örnek bağlantı bilgileri:")
        print("   DB_HOST=localhost")
        print("   DB_PORT=5432") 
        print("   DB_NAME=library")
        print("   DB_USER=postgres")
        print("   DB_PASSWORD=your_password")
        print("🚀 PostgreSQL kurulumu için:")
        print("   sudo apt-get install postgresql postgresql-contrib")
        print("   sudo -u postgres createuser --interactive")
        print("   sudo -u postgres createdb library")
        print("   sudo -u postgres psql -c \"ALTER USER postgres PASSWORD 'password';\"")
        raise e

def get_db():
    # PostgreSQL bağlantı bilgileri
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'library')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
    
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.cursor_factory = RealDictCursor
        return conn
    except psycopg2.OperationalError as e:
        print(f"❌ PostgreSQL bağlantı hatası: {e}")
        print("🔧 PostgreSQL bağlantı ayarları:")
        print(f"   Host: {DB_HOST}")
        print(f"   Port: {DB_PORT}")
        print(f"   Database: {DB_NAME}")
        print(f"   User: {DB_USER}")
        print("🔧 Çözüm için:")
        print("   sudo systemctl restart postgresql")
        print("   sudo -u postgres psql -c \"ALTER USER postgres PASSWORD 'password';\"")
        raise e

# Global variables
current_user = None
is_admin = False

# Hash all existing passwords
def hash_all_passwords():
    """Tüm kullanıcıların şifrelerini hash'ler"""
    try:
        conn = get_db()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Tüm kullanıcıları al
        cursor.execute('SELECT id, username, password_hash FROM users')
        users = cursor.fetchall()
        
        updated_count = 0
        
        # Cursor türünden bağımsız güvenli okuma
        for user in users:
            try:
                # Mapping/dict benzeri satır
                user_id = user['id'] if isinstance(user, dict) else user[0]
                username_value = user['username'] if isinstance(user, dict) else user[1]
                password_hash_value = user['password_hash'] if isinstance(user, dict) else user[2]
            except Exception:
                # Beklenmeyen satır formatı
                continue
            
            # Geçersiz id'leri atla
            if not isinstance(user_id, int):
                continue
            
            # Eğer şifre zaten hash'li değilse (64 karakterden kısa ise)
            if isinstance(password_hash_value, str) and len(password_hash_value) < 64:
                # Şifreyi hash'le
                import hashlib
                new_hash = hashlib.sha256(password_hash_value.encode()).hexdigest()
                
                try:
                    # Veritabanını güncelle
                    cursor.execute('UPDATE users SET password_hash = %s WHERE id = %s', (new_hash, user_id))
                    print(f"✅ {username_value} kullanıcısının şifresi hash'lendi: {password_hash_value} → {new_hash[:20]}...")
                    updated_count += 1
                except Exception as e:
                    print(f"ℹ️ Şifre hash'leme atlandı (id={user_id}): {e}")
        
        conn.commit()
        conn.close()
        
        if updated_count > 0:
            print(f"🎉 Toplam {updated_count} kullanıcının şifresi hash'lendi!")
            
    except Exception as e:
        print(f"❌ Şifre hash'leme hatası: {e}")

def add_sample_books():
    """Örnek kitap verilerini ekler"""
    try:
        conn = get_db()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Mevcut kitap sayısını kontrol et
        cursor.execute('SELECT COUNT(*) FROM books')
        book_count = cursor.fetchone()['count']
        
        if book_count > 0:
            print(f"ℹ️ Zaten {book_count} kitap mevcut, örnek veriler eklenmedi.")
            conn.close()
            return
        
        # Örnek kitaplar
        sample_books = [
            {
                'title': 'Suç ve Ceza',
                'author': 'Fyodor Dostoyevski',
                'description': 'Psikolojik gerilim romanı, suç ve vicdan temalarını işler.',
                'published_year': 1866,
                'isbn': '978-975-0719-01-2',
                'category': 'Roman',
                'cover_url': 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=400',
                'total_copies': 3,
                'available_copies': 3
            },
            {
                'title': '1984',
                'author': 'George Orwell',
                'description': 'Distopik roman, totaliter rejimlerin tehlikelerini gösterir.',
                'published_year': 1949,
                'isbn': '978-975-0719-02-9',
                'category': 'Distopik',
                'cover_url': 'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=400',
                'total_copies': 2,
                'available_copies': 2
            },
            {
                'title': 'Küçük Prens',
                'author': 'Antoine de Saint-Exupéry',
                'description': 'Çocuklar için yazılmış ama her yaşa hitap eden felsefi masal.',
                'published_year': 1943,
                'isbn': '978-975-0719-03-6',
                'category': 'Çocuk',
                'cover_url': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400',
                'total_copies': 5,
                'available_copies': 5
            },
            {
                'title': 'Dönüşüm',
                'author': 'Franz Kafka',
                'description': 'Varoluşçu roman, insanın yabancılaşmasını konu alır.',
                'published_year': 1915,
                'isbn': '978-975-0719-04-3',
                'category': 'Roman',
                'cover_url': 'https://images.unsplash.com/photo-1512820790803-83ca734da794?w=400',
                'total_copies': 2,
                'available_copies': 2
            },
            {
                'title': 'Fareler ve İnsanlar',
                'author': 'John Steinbeck',
                'description': 'Büyük Buhran döneminde geçen dostluk hikayesi.',
                'published_year': 1937,
                'isbn': '978-975-0719-05-0',
                'category': 'Roman',
                'cover_url': 'https://images.unsplash.com/photo-1516979187457-637abb4f9353?w=400',
                'total_copies': 3,
                'available_copies': 3
            },
            {
                'title': 'Şeker Portakalı',
                'author': 'José Mauro de Vasconcelos',
                'description': 'Çocukluğun masumiyetini ve hayal gücünü anlatan roman.',
                'published_year': 1968,
                'isbn': '978-975-0719-06-7',
                'category': 'Roman',
                'cover_url': 'https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=400',
                'total_copies': 4,
                'available_copies': 4
            }
        ]
        
        # Kitapları veritabanına ekle
        for book in sample_books:
            cursor.execute('''
                INSERT INTO books (title, author, description, published_year, isbn, category, cover_url, total_copies, available_copies)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (book['title'], book['author'], book['description'], book['published_year'], 
                  book['isbn'], book['category'], book['cover_url'], book['total_copies'], book['available_copies']))
        
        conn.commit()
        conn.close()
        print(f"✅ {len(sample_books)} örnek kitap eklendi!")
        
    except Exception as e:
        print(f"❌ Örnek kitap ekleme hatası: {e}")

# Initialize database and hash passwords
print("🚀 Kütüphane Yönetim Sistemi başlatılıyor...")
print("📊 PostgreSQL bağlantısı bekleniyor...")
init_db()
print("🌐 NiceGUI uygulaması başlatılıyor...")
hash_all_passwords()

# Custom CSS for modern design
ui.add_head_html('''

<style>
    :root {
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --success-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        --warning-gradient: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        --danger-gradient: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
    }
    
    body {
        margin: 0;
        padding: 0;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        transition: all 0.3s ease;
    }
    
    body {
        background: #f8fafc;
        color: #1e293b;
        transition: all 0.3s ease;
    }
    
    .gradient-bg {
        background: var(--primary-gradient);
        min-height: 100vh;
    }
    
    .glass-card {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    .modern-input {
        background: rgba(255, 255, 255, 0.9);
        border: none;
        border-radius: 16px;
        padding: 16px 20px;
        font-size: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        color: #1e293b;
    }
    
    .modern-input:focus {
        background: white;
        box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.3), 0 8px 32px rgba(0, 0, 0, 0.15);
        transform: translateY(-2px);
        outline: none;
    }
    
    .modern-button {
        background: var(--primary-gradient);
        border: none;
        border-radius: 16px;
        padding: 16px 32px;
        color: white;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s ease;
        cursor: pointer;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
    }
    
    .modern-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.4);
    }
    
    .modern-button.bg-green {
        background: var(--success-gradient);
        box-shadow: 0 8px 32px rgba(79, 172, 254, 0.3);
    }
    
    .modern-button.bg-red {
        background: var(--danger-gradient);
        box-shadow: 0 8px 32px rgba(250, 112, 154, 0.3);
    }
    
    .modern-button.bg-blue {
        background: var(--primary-gradient);
    }
    
    .modern-button.bg-purple {
        background: var(--secondary-gradient);
        box-shadow: 0 8px 32px rgba(240, 147, 251, 0.3);
    }
    
    .modern-button.bg-orange {
        background: var(--warning-gradient);
        box-shadow: 0 8px 32px rgba(67, 233, 123, 0.3);
    }
    
    .modern-button.bg-teal {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .stats-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 24px;
        padding: 32px;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .stats-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 16px 48px rgba(0, 0, 0, 0.15);
    }
    
    .dark .stats-card {
        background: rgba(255, 255, 255, 0.1);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .book-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 20px;
        transition: all 0.3s ease;
        border: 1px solid rgba(0, 0, 0, 0.1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        min-height: 450px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: center;
        text-align: center;
    }
    
    .book-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 16px 48px rgba(0, 0, 0, 0.15);
    }
    
    .book-card img {
        border-radius: 12px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        width: 100%;
        height: 200px;
        object-fit: cover;
    }
    
    .dark .book-card {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .user-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 24px;
        transition: all 0.3s ease;
        border: 1px solid rgba(0, 0, 0, 0.1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    .user-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 16px 48px rgba(0, 0, 0, 0.15);
    }
    
    .loan-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 24px;
        transition: all 0.3s ease;
        border: 1px solid rgba(0, 0, 0, 0.1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    .loan-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 16px 48px rgba(0, 0, 0, 0.15);
    }
    
    .floating-card {
        animation: float 6s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    .pulse {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
</style>
''')

# Login page
@ui.page('/')
def login_page():
    with ui.card().classes('absolute-center w-96 glass-card floating-card'):
        ui.label('📚 Kütüphane').classes('text-h4 text-center q-mb-lg font-bold')
        
        username = ui.input('👤 Kullanıcı Adı').classes('w-full modern-input q-mb-md')
        password = ui.input('🔒 Şifre', password=True).classes('w-full modern-input q-mb-md')
        
        def login():
            try:
                print(f"🔍 Login attempt for user: {username.value}")
                global current_user, is_admin
                
                if not username.value or not password.value:
                    ui.notify('❌ Kullanıcı adı ve şifre gerekli!', type='negative')
                    return
                
                conn = get_db()
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute('SELECT id, username, password_hash, is_staff, is_banned FROM users WHERE username = %s', (username.value,))
                row = cursor.fetchone()
                conn.close()
                
                # Şifreyi hash'le ve karşılaştır
                import hashlib
                password_hash = hashlib.sha256(password.value.encode()).hexdigest()
                
                print(f"🔐 Password hash: {password_hash[:20]}...")
                
                # Hem dict hem tuple sonuçlar için uyum
                if row:
                    if isinstance(row, dict):
                        user = row
                    else:
                        user = {
                            'id': row[0],
                            'username': row[1],
                            'password_hash': row[2],
                            'is_staff': row[3],
                            'is_banned': row[4] if len(row) > 4 else False,
                        }
                    print(f"👤 User found: {user['username']}")
                else:
                    user = None
                    print("❌ User not found")

                if user and user['password_hash'] == password_hash:
                    # Check if user is banned
                    if user['is_banned'] if 'is_banned' in user.keys() else False:
                        ui.notify('🚫 Hesabınız banlanmış! Lütfen yönetici ile iletişime geçin.', type='negative')
                        return
                    
                    current_user = user
                    is_admin = user['is_staff']
                    print(f"✅ Login successful for {user['username']}")
                    ui.notify('🎉 Giriş başarılı!', type='positive')
                    ui.navigate.to('/dashboard')
                else:
                    print("❌ Invalid credentials")
                    ui.notify('❌ Geçersiz kullanıcı adı veya şifre', type='negative')
            except Exception as e:
                print(f"❌ Login error: {e}")
                ui.notify(f'❌ Giriş hatası: {str(e)}', type='negative')
        
        # Login button
        login_btn = ui.button('🚀 GİRİŞ YAP', on_click=login).classes('w-full modern-button q-mb-md pulse')
        
        # Register button
        ui.button('📝 Kayıt Ol', on_click=lambda: ui.navigate.to('/register')).classes('w-full modern-button bg-green')
        
        # Add Enter key support using NiceGUI's built-in method
        def handle_enter():
            login()
        
        username.on('keydown.enter', handle_enter)
        password.on('keydown.enter', handle_enter)

# Register page
@ui.page('/register')
def register_page():
    with ui.card().classes('absolute-center w-96 glass-card floating-card'):
        ui.label('📝 Yeni Hesap Oluştur').classes('text-h4 text-center q-mb-lg font-bold')
        
        username = ui.input('👤 Kullanıcı Adı').classes('w-full modern-input q-mb-md')
        email = ui.input('📧 E-posta').classes('w-full modern-input q-mb-md')
        password = ui.input('🔒 Şifre', password=True).classes('w-full modern-input q-mb-md')
        password2 = ui.input('🔒 Şifre Tekrar', password=True).classes('w-full modern-input q-mb-md')
        
        def register():
            if password.value != password2.value:
                ui.notify('❌ Şifreler eşleşmiyor!', type='negative')
                return
            
            # Şifreyi hash'le
            import hashlib
            password_hash = hashlib.sha256(password.value.encode()).hexdigest()
            
            conn = get_db()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            try:
                cursor.execute('''
                    INSERT INTO users (username, email, password_hash)
                    VALUES (%s, %s, %s)
                ''', (username.value, email.value, password_hash))
                conn.commit()
                conn.close()
                
                ui.notify('✅ Hesabınız başarıyla oluşturuldu!', type='positive')
                ui.navigate.to('/')
            except psycopg2.errors.IntegrityError:
                conn.close()
                ui.notify('❌ Bu kullanıcı adı veya email zaten kullanılıyor!', type='negative')
        
        # Add Enter key support
        username.on('keydown.enter', register)
        email.on('keydown.enter', register)
        password.on('keydown.enter', register)
        password2.on('keydown.enter', register)
        
        ui.button('✅ Kayıt Ol', on_click=register).classes('w-full modern-button q-mt-md')
        
        with ui.row().classes('w-full justify-center q-mt-md'):
            ui.button('← Geri Dön', on_click=lambda: ui.navigate.to('/')).classes('modern-button bg-grey')

# Dashboard page
@ui.page('/dashboard')
def dashboard():
    if not current_user:
        ui.navigate.to('/')
        return
    
    with ui.column().classes('w-full p-6 gradient-bg min-h-screen'):
        # Header with dark mode toggle
        with ui.row().classes('w-full justify-between items-center q-mb-lg'):
            with ui.row().classes('items-center'):
                ui.label(f'🎉 Hoş geldiniz, {current_user["username"]}!').classes('text-h4 font-bold text-white')
            
            with ui.row().classes('items-center gap-4'):
                ui.button('🚪 Çıkış', on_click=lambda: ui.navigate.to('/')).classes('modern-button bg-red')
        
        # Stats cards
        conn = get_db()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute('SELECT COUNT(*) FROM books')
        books_total = cursor.fetchone()['count']
        
        # Get loans count based on user role
        if is_admin:
            # Admin sees all active loans
            cursor.execute('SELECT COUNT(*) FROM loans WHERE returned_at IS NULL')
            loans_active = cursor.fetchone()['count']
            loans_label = 'Aktif Ödünç Alınanlar'
        else:
            # Normal users see only their own active loans
            cursor.execute('SELECT COUNT(*) FROM loans WHERE user_id = %s AND returned_at IS NULL', (current_user['id'],))
            loans_active = cursor.fetchone()['count']
            loans_label = 'Aktif Ödünç Aldıklarım'
        
        # Only show user count for admins
        users_total = 0
        if is_admin:
            cursor.execute('SELECT COUNT(*) FROM users')
            users_total = cursor.fetchone()['count']
        
        conn.close()
        
        with ui.row().classes('w-full q-mb-lg gap-4'):
            with ui.card().classes('flex-1 stats-card'):
                ui.label('📚').classes('text-h2')
                ui.label('Toplam Kitap').classes('text-caption q-mt-sm')
                ui.label(str(books_total)).classes('text-h3 font-bold text-primary')
            
            with ui.card().classes('flex-1 stats-card'):
                ui.label('📖').classes('text-h2')
                ui.label(loans_label).classes('text-caption q-mt-sm')
                ui.label(str(loans_active)).classes('text-h3 font-bold text-primary')
            
            # Only show user count for admins
            if is_admin:
                with ui.card().classes('flex-1 stats-card'):
                    ui.label('👥').classes('text-h2')
                    ui.label('Toplam Kullanıcı').classes('text-caption q-mt-sm')
                    ui.label(str(users_total)).classes('text-h3 font-bold text-primary')
        
        # Navigation buttons
        with ui.row().classes('w-full q-mb-lg gap-4 flex-wrap'):
            ui.button('📚 KİTAP KATALOĞU', on_click=lambda: ui.navigate.to('/catalog')).classes('modern-button bg-blue flex-1')
            ui.button('📖 Ödünç Aldıklarım', on_click=lambda: ui.navigate.to('/my-loans')).classes('modern-button bg-green flex-1')
            
            if is_admin:
                ui.button('👥 Kullanıcı Yönetimi', on_click=lambda: ui.navigate.to('/admin/users')).classes('modern-button bg-purple flex-1')
                ui.button('📊 Ödünç Alınanlar', on_click=lambda: ui.navigate.to('/admin/loans')).classes('modern-button bg-orange flex-1')
                ui.button('➕ KİTAP EKLE', on_click=lambda: ui.navigate.to('/admin/book/add')).classes('modern-button bg-teal flex-1')

# Catalog page
@ui.page('/catalog')
def catalog():
    if not current_user:
        ui.navigate.to('/')
        return
    
    with ui.column().classes('w-full p-6 gradient-bg min-h-screen'):
        # Header
        with ui.row().classes('w-full justify-between items-center q-mb-lg'):
            ui.label('📚 KİTAP KATALOĞU').classes('text-h4 font-bold text-white')
            ui.button('← Geri', on_click=lambda: ui.navigate.to('/dashboard')).classes('modern-button bg-grey')
        
        # Search
        search_input = ui.input('🔍 Kitap ara...').classes('w-full modern-input q-mb-md')
        
        # Books grid
        books_container = ui.column().classes('w-full')
        
        def load_books():
            books_container.clear()
            conn = get_db()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            search_term = search_input.value
            if search_term:
                cursor.execute('''
                    SELECT * FROM books 
                    WHERE title LIKE %s OR author LIKE %s OR description LIKE %s
                    ORDER BY created_at DESC
                ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
            else:
                cursor.execute('SELECT * FROM books ORDER BY created_at DESC')
            
            books = cursor.fetchall()
            conn.close()
            
            with books_container:
                with ui.grid().classes('w-full gap-6').style('grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));'):
                    for book in books:
                        with ui.card().classes('book-card flex flex-col items-center'):
                            # Kitap kapağı - Gerçek resim veya placeholder
                            if book['cover_url']:
                                ui.html(f'<div style="display: flex; justify-content: center; align-items: center; width: 100%; height: 200px; margin-bottom: 16px;"><img src="{book["cover_url"]}" alt="{book["title"]}" style="width: 100%; height: 200px; object-fit: cover; border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.1);" onerror="this.style.display=\'none\'; this.parentElement.nextElementSibling.style.display=\'flex\';" /></div>')
                                # Fallback placeholder (başlangıçta gizli)
                                cover_colors = {
                                    'A Game of Thrones': 'bg-blue-5',
                                    'A Clash of Kings': 'bg-green-5', 
                                    'A Storm of Swords': 'bg-orange-5',
                                    'A Feast for Crows': 'bg-purple-5',
                                    'A Dance with Dragons': 'bg-red-5'
                                }
                                cover_color = cover_colors.get(book['title'], 'bg-grey-3')
                                with ui.row().classes(f'w-full h-48 {cover_color} rounded-lg q-mb-md items-center justify-center').style('display: none;'):
                                    with ui.column().classes('text-center'):
                                        ui.label('📚').classes('text-h2 text-white q-mb-sm')
                                        ui.label(book['title'][:15] + '...' if len(book['title']) > 15 else book['title']).classes('text-caption text-white font-bold')
                            else:
                                # Sadece placeholder
                                cover_colors = {
                                    'A Game of Thrones': 'bg-blue-5',
                                    'A Clash of Kings': 'bg-green-5', 
                                    'A Storm of Swords': 'bg-orange-5',
                                    'A Feast for Crows': 'bg-purple-5',
                                    'A Dance with Dragons': 'bg-red-5'
                                }
                                cover_color = cover_colors.get(book['title'], 'bg-grey-3')
                                with ui.row().classes(f'w-full h-48 {cover_color} rounded-lg q-mb-md items-center justify-center'):
                                    with ui.column().classes('text-center'):
                                        ui.label('📚').classes('text-h2 text-white q-mb-sm')
                                        ui.label(book['title'][:15] + '...' if len(book['title']) > 15 else book['title']).classes('text-caption text-white font-bold')
                            
                            # Kitap bilgileri - ortalanmış
                            with ui.column().classes('w-full items-center text-center'):
                                ui.label(book['title']).classes('text-h6 font-bold text-center')
                                ui.label(f"✍️ {book['author']}").classes('text-caption q-mb-sm text-center')
                                if book['category']:
                                    ui.label(f"📂 {book['category']}").classes('text-caption q-mb-sm text-center')
                                ui.label(f"📦 Mevcut: {book['available_copies']}/{book['total_copies']}").classes('text-caption q-mb-sm text-center')
                            
                            # Butonlar - ortalanmış
                            with ui.row().classes('gap-2 justify-center w-full'):
                                if book['available_copies'] > 0:
                                    ui.button('📖 Ödünç Al', on_click=lambda b=book: borrow_book(b['id'])).classes('modern-button bg-green text-xs')
                                else:
                                    ui.button('❌ Mevcut Değil', disabled=True).classes('modern-button bg-grey text-xs')
                                
                                if is_admin:
                                    ui.button('✏️', on_click=lambda b=book: ui.navigate.to(f'/admin/book/edit/{b["id"]}')).classes('modern-button bg-blue text-xs')
                                    ui.button('🗑️', on_click=lambda b=book: delete_book(b['id'])).classes('modern-button bg-red text-xs')
        
        # Arama fonksiyonunu her karakter yazıldığında çalıştır
        def on_search_input():
            load_books()
        
        search_input.on('input', on_search_input)
        search_input.on('keyup', on_search_input)
        search_input.on('change', on_search_input)
        
        # İlk yükleme
        load_books()

def borrow_book(book_id):
    conn = get_db()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute('SELECT * FROM books WHERE id = %s', (book_id,))
    book = cursor.fetchone()
    
    if book and book['available_copies'] > 0:
        due_date = datetime.now().date() + timedelta(days=14)
        cursor.execute('''
            INSERT INTO loans (user_id, book_id, due_date)
            VALUES (%s, %s, %s)
        ''', (current_user['id'], book_id, due_date))
        
        cursor.execute('''
            UPDATE books 
            SET available_copies = available_copies - 1 
            WHERE id = %s
        ''', (book_id,))
        
        conn.commit()
        conn.close()
        
        ui.notify(f'📖 Kitap ödünç alındı! Son teslim tarihi: {due_date.strftime("%d.%m.%Y")}', type='positive')
        ui.navigate.to('/catalog')
    else:
        conn.close()
        ui.notify('❌ Bu kitap şu anda mevcut değil.', type='negative')

def delete_book(book_id):
    conn = get_db()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute('DELETE FROM books WHERE id = %s', (book_id,))
    conn.commit()
    conn.close()
    
    ui.notify('🗑️ Kitap silindi!', type='positive')
    ui.navigate.to('/catalog')

# My loans page
@ui.page('/my-loans')
def my_loans():
    if not current_user:
        ui.navigate.to('/')
        return
    
    with ui.column().classes('w-full p-6 gradient-bg min-h-screen'):
        # Header
        with ui.row().classes('w-full justify-between items-center q-mb-lg'):
            ui.label('📖 Ödünç Aldıklarım').classes('text-h4 font-bold text-white')
            ui.button('← Geri', on_click=lambda: ui.navigate.to('/dashboard')).classes('modern-button bg-grey')
        
        # Loans list
        conn = get_db()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute('''
            SELECT l.*, b.title, b.author 
            FROM loans l 
            JOIN books b ON l.book_id = b.id 
            WHERE l.user_id = %s 
            ORDER BY l.borrowed_at DESC
        ''', (current_user['id'],))
        loans = cursor.fetchall()
        conn.close()
        
        with ui.column().classes('w-full gap-4'):
            for loan in loans:
                with ui.card().classes('book-card'):
                    with ui.row().classes('w-full justify-between items-center'):
                        with ui.column().classes('flex-1'):
                            ui.label(loan['title']).classes('text-h6 font-bold')
                            ui.label(f"✍️ {loan['author']}").classes('text-caption')
                            # Tarih formatını düzenle
                            borrowed_at = loan['borrowed_at']
                            if borrowed_at:
                                try:
                                    if isinstance(borrowed_at, str):
                                        borrowed_at = borrowed_at.split('.')[0]  # Mikrosaniyeleri kaldır
                                except:
                                    borrowed_at = str(borrowed_at)
                            
                            due_date = loan['due_date']
                            if due_date:
                                try:
                                    if isinstance(due_date, str):
                                        due_date = due_date.split(' ')[0]  # Sadece tarih kısmını al
                                except:
                                    due_date = str(due_date)
                            
                            ui.label(f"📅 Alış: {borrowed_at or '—'}").classes('text-caption')
                            if due_date:
                                ui.label(f"⏰ Son teslim: {due_date}").classes('text-caption')
                        
                        if loan['returned_at'] is None:
                            ui.button('📤 İade Et', on_click=lambda l=loan: return_book(l['id'])).classes('modern-button bg-red')
                        else:
                            ui.label('✅ İade edildi').classes('text-caption text-grey')

def return_book(loan_id):
    conn = get_db()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute('SELECT * FROM loans WHERE id = %s', (loan_id,))
    loan = cursor.fetchone()
    
    if loan and loan['returned_at'] is None:
        cursor.execute('''
            UPDATE loans 
            SET returned_at = CURRENT_TIMESTAMP 
            WHERE id = %s
        ''', (loan_id,))
        
        cursor.execute('''
            UPDATE books 
            SET available_copies = available_copies + 1 
            WHERE id = %s
        ''', (loan['book_id'],))
        
        conn.commit()
        conn.close()
        
        ui.notify('📤 Kitap iade edildi!', type='positive')
        ui.navigate.to('/my-loans')
    else:
        conn.close()
        ui.notify('❌ Bu ödünç kaydı bulunamadı.', type='negative')

# Admin users page
@ui.page('/admin/users')
def admin_users():
    if not current_user or not is_admin:
        ui.navigate.to('/')
        return
    

    
    with ui.column().classes('w-full p-6 gradient-bg min-h-screen'):
        # Header
        with ui.row().classes('w-full justify-between items-center q-mb-lg'):
            ui.label('👥 Kullanıcı Yönetimi').classes('text-h4 font-bold text-white')
            ui.button('← Geri', on_click=lambda: ui.navigate.to('/dashboard')).classes('modern-button bg-grey')
        
        # Users table
        conn = get_db()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM users ORDER BY id')
        users = cursor.fetchall()
        conn.close()
        
        # Display users in cards instead of table
        if not users:
            ui.label('📭 Henüz kullanıcı bulunmuyor').classes('text-h6 text-center text-grey q-mt-lg')
        else:
            with ui.grid().classes('w-full gap-4'):
                for user in users:
                    with ui.card().classes('user-card glass-card'):
                        with ui.row().classes('w-full justify-between items-center'):
                            with ui.column().classes('flex-1'):
                                ui.label(f"👤 {user['username']}").classes('text-h6 font-bold')
                                ui.label(f"📧 {user['email']}").classes('text-caption q-mb-sm')
                                ui.label(f"🆔 ID: {user['id']}").classes('text-caption q-mb-sm')
                                
                                # Şifre hash'ini göster
                                password_hash = user['password_hash']
                                ui.label(f"🔐 Şifre: {password_hash}").classes('text-caption q-mb-sm text-grey-6')
                            
                            with ui.column().classes('text-right'):
                                ui.label('👑 Yönetici' if user['is_staff'] else '👤 Normal Kullanıcı').classes('text-caption font-bold')
                                # Ban durumu
                                if user['is_banned'] if 'is_banned' in user.keys() else False:
                                    ui.label('🚫 BANLI').classes('text-caption font-bold text-red')
                                else:
                                    ui.label('✅ Aktif').classes('text-caption font-bold text-green')
                        
                        # Butonlar
                        with ui.row().classes('w-full justify-end q-mt-md gap-2'):
                            def button_click():
                                ui.navigate.to(f'/admin/change-password/{user["id"]}')
                            ui.button('🔑 Şifre Değiştir', on_click=button_click).classes('modern-button bg-blue text-white')
                            
                            # Banlama butonu - Admin kendini banlayamaz
                            if user['id'] != current_user['id']:  # Sadece diğer kullanıcılar için
                                # Ban durumunu kontrol et
                                is_banned = user['is_banned'] if 'is_banned' in user.keys() else False
                                
                                if is_banned:
                                    # Unban butonu
                                    def unban_user():
                                        conn = get_db()
                                        cursor = conn.cursor(cursor_factory=RealDictCursor)
                                        cursor.execute('UPDATE users SET is_banned = FALSE WHERE id = %s', (user['id'],))
                                        conn.commit()
                                        conn.close()
                                        ui.notify(f'✅ {user["username"]} kullanıcısının banı kaldırıldı!', type='positive')
                                        # Sayfayı yenile
                                        ui.navigate.to('/admin/users')
                                    
                                    ui.button('✅ Banı Kaldır', on_click=unban_user).classes('modern-button bg-green text-white')
                                else:
                                    # Ban butonu
                                    def ban_user():
                                        conn = get_db()
                                        cursor = conn.cursor(cursor_factory=RealDictCursor)
                                        cursor.execute('UPDATE users SET is_banned = TRUE WHERE id = %s', (user['id'],))
                                        conn.commit()
                                        conn.close()
                                        ui.notify(f'🚫 {user["username"]} kullanıcısı banlandı!', type='warning')
                                        # Sayfayı yenile
                                        ui.navigate.to('/admin/users')
                                    
                                    ui.button('🚫 Banla', on_click=ban_user).classes('modern-button bg-red text-white')
                            else:
                                # Admin kendisi için özel mesaj
                                ui.label('👑 Kendinizi banlayamazsınız').classes('text-caption text-grey-6 italic')

# Şifre değiştirme sayfası
@ui.page('/admin/change-password/{user_id}')
def change_password_page(user_id: int):
    if not current_user or not is_admin:
        ui.navigate.to('/')
        return
    
    # Kullanıcı bilgilerini al
    conn = get_db()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        ui.notify('❌ Kullanıcı bulunamadı!', type='negative')
        ui.navigate.to('/admin/users')
        return
    
    with ui.column().classes('w-full p-6 gradient-bg min-h-screen items-center justify-center'):
        # Form container - ortalanmış
        with ui.column().classes('w-full max-w-md items-center'):
            # Header
            with ui.row().classes('w-full justify-between items-center q-mb-lg'):
                ui.label(f'🔑 {user["username"]} Kullanıcısının Şifresini Değiştir').classes('text-h4 font-bold text-white')
                ui.button('← Geri', on_click=lambda: ui.navigate.to('/admin/users')).classes('modern-button bg-grey')
            
            # Form
            with ui.card().classes('w-full glass-card'):
                ui.label(f'👤 Kullanıcı: {user["username"]}').classes('text-h6 font-bold q-mb-md')
                ui.label(f'📧 E-posta: {user["email"]}').classes('text-caption q-mb-md')
                
                new_password = ui.input('🔐 Yeni Şifre', password=True).classes('w-full modern-input q-mb-md')
                confirm_password = ui.input('🔐 Şifreyi Tekrarla', password=True).classes('w-full modern-input q-mb-md')
                
                def save_password():
                    if new_password.value != confirm_password.value:
                        ui.notify('❌ Şifreler eşleşmiyor!', type='negative')
                        return
                    
                    if len(new_password.value) < 3:
                        ui.notify('❌ Şifre en az 3 karakter olmalıdır!', type='negative')
                        return
                    
                    # Şifreyi hash'le
                    import hashlib
                    password_hash = hashlib.sha256(new_password.value.encode()).hexdigest()
                    
                    conn = get_db()
                    cursor = conn.cursor(cursor_factory=RealDictCursor)
                    cursor.execute('UPDATE users SET password_hash = %s WHERE id = %s', (password_hash, user_id))
                    conn.commit()
                    conn.close()
                    
                    ui.notify(f'✅ {user["username"]} kullanıcısının şifresi başarıyla değiştirildi!', type='positive')
                    ui.navigate.to('/admin/users')
                
                with ui.row().classes('w-full justify-end gap-2 q-mt-md'):
                    ui.button('❌ İptal', on_click=lambda: ui.navigate.to('/admin/users')).classes('modern-button bg-grey')
                    ui.button('💾 Değiştir', on_click=save_password).classes('modern-button bg-green')

# Admin loans page
@ui.page('/admin/loans')
def admin_loans():
    if not current_user or not is_admin:
        ui.navigate.to('/')
        return
    
    with ui.column().classes('w-full p-6 gradient-bg min-h-screen'):
        # Header
        with ui.row().classes('w-full justify-between items-center q-mb-lg'):
            ui.label('📊 Ödünç Alınanlar').classes('text-h4 font-bold text-white')
            ui.button('← Geri', on_click=lambda: ui.navigate.to('/dashboard')).classes('modern-button bg-grey')
        
        # Loans table
        conn = get_db()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute('''
            SELECT l.*, u.username, b.title 
            FROM loans l 
            JOIN users u ON l.user_id = u.id 
            JOIN books b ON l.book_id = b.id 
            ORDER BY l.borrowed_at DESC
        ''')
        loans = cursor.fetchall()
        conn.close()
        
        # Display loans in cards instead of table
        if not loans:
            ui.label('📭 Henüz ödünç kaydı bulunmuyor').classes('text-h6 text-center text-grey q-mt-lg')
        else:
            with ui.grid().classes('w-full gap-4'):
                for loan in loans:
                    status = '🟢 Aktif' if loan['returned_at'] is None else '✅ İade edildi'
                    
                    # Tarih formatını düzenle
                    borrowed_at = loan['borrowed_at']
                    if borrowed_at:
                        try:
                            if isinstance(borrowed_at, str):
                                borrowed_at = borrowed_at.split('.')[0]  # Mikrosaniyeleri kaldır
                        except:
                            borrowed_at = str(borrowed_at)
                    
                    due_date = loan['due_date']
                    due_date_display = due_date
                    if due_date:
                        try:
                            if isinstance(due_date, str):
                                due_date_display = due_date.split(' ')[0]  # Sadece tarih kısmını al
                            else:
                                due_date_display = str(due_date)
                        except:
                            due_date_display = str(due_date)
                    
                    returned_at = loan['returned_at']
                    if returned_at:
                        try:
                            if isinstance(returned_at, str):
                                returned_at = returned_at.split('.')[0]  # Mikrosaniyeleri kaldır
                        except:
                            returned_at = str(returned_at)
                    
                    with ui.card().classes('loan-card glass-card'):
                        with ui.row().classes('w-full justify-between items-center'):
                            with ui.column().classes('flex-1'):
                                ui.label(f"📖 {loan['title']}").classes('text-h6 font-bold')
                                ui.label(f"👤 {loan['username']}").classes('text-caption q-mb-sm')
                                ui.label(f"📅 Alış: {borrowed_at or '—'}").classes('text-caption q-mb-sm')
                                if due_date:
                                    ui.label(f"⏰ Son Teslim: {due_date_display}").classes('text-caption q-mb-sm')
                                if returned_at:
                                    ui.label(f"📤 İade: {returned_at}").classes('text-caption q-mb-sm')
                            
                            with ui.column().classes('text-right'):
                                ui.label(status).classes('text-caption font-bold')
                                if loan['returned_at'] is None:
                                    ui.label('🟡 Gecikmiş' if due_date and due_date < datetime.now().date() else '🟢 Zamanında').classes('text-caption')

# Add book page
@ui.page('/admin/book/add')
def add_book():
    if not current_user or not is_admin:
        ui.navigate.to('/')
        return
    
    with ui.column().classes('w-full p-6 gradient-bg min-h-screen'):
        # Header
        with ui.row().classes('w-full justify-between items-center q-mb-lg'):
            ui.label('➕ Yeni KİTAP EKLE').classes('text-h4 font-bold text-white')
            ui.button('← Geri', on_click=lambda: ui.navigate.to('/dashboard')).classes('modern-button bg-grey')
        
        # Form
        with ui.card().classes('w-full max-w-2xl glass-card'):
            title = ui.input('📖 Kitap Başlığı').classes('w-full modern-input q-mb-md')
            author = ui.input('✍️ Yazar').classes('w-full modern-input q-mb-md')
            description = ui.textarea('📝 Açıklama').classes('w-full modern-input q-mb-md')
            published_year = ui.number('📅 Yayın Yılı', min=1000, max=2100).classes('w-full modern-input q-mb-md')
            isbn = ui.input('🏷️ ISBN').classes('w-full modern-input q-mb-md')
            category = ui.input('📂 Kategori').classes('w-full modern-input q-mb-md')
            cover_url = ui.input('🖼️ Kapak Fotoğrafı URL').classes('w-full modern-input q-mb-md')
            total_copies = ui.number('📦 Toplam Kopya Sayısı', min=1, value=1).classes('w-full modern-input q-mb-md')
            
            def save_book():
                conn = get_db()
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                
                cursor.execute('''
                    INSERT INTO books (title, author, description, published_year, isbn, category, cover_url, total_copies, available_copies)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (title.value, author.value, description.value, published_year.value, isbn.value, category.value, cover_url.value, total_copies.value, total_copies.value))
                
                conn.commit()
                conn.close()
                
                ui.notify('✅ Kitap başarıyla eklendi!', type='positive')
                ui.navigate.to('/catalog')
            
            ui.button('💾 Kaydet', on_click=save_book).classes('modern-button bg-green q-mt-md')

# Edit book page
@ui.page('/admin/book/edit/{book_id}')
def edit_book(book_id: int):
    if not current_user or not is_admin:
        ui.navigate.to('/')
        return
    
    conn = get_db()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM books WHERE id = %s', (book_id,))
    book = cursor.fetchone()
    conn.close()
    
    if not book:
        ui.notify('❌ Kitap bulunamadı!', type='negative')
        ui.navigate.to('/catalog')
        return
    
    with ui.column().classes('w-full p-6 gradient-bg min-h-screen'):
        # Header
        with ui.row().classes('w-full justify-between items-center q-mb-lg'):
            ui.label('✏️ Kitap Düzenle').classes('text-h4 font-bold text-white')
            ui.button('← Geri', on_click=lambda: ui.navigate.to('/catalog')).classes('modern-button bg-grey')
        
        # Form
        with ui.card().classes('w-full max-w-2xl glass-card'):
            title = ui.input('📖 Kitap Başlığı', value=book['title']).classes('w-full modern-input q-mb-md')
            author = ui.input('✍️ Yazar', value=book['author']).classes('w-full modern-input q-mb-md')
            description = ui.textarea('📝 Açıklama', value=book['description'] or '').classes('w-full modern-input q-mb-md')
            published_year = ui.number('📅 Yayın Yılı', min=1000, max=2100, value=book['published_year']).classes('w-full modern-input q-mb-md')
            isbn = ui.input('🏷️ ISBN', value=book['isbn'] or '').classes('w-full modern-input q-mb-md')
            category = ui.input('📂 Kategori', value=book['category'] or '').classes('w-full modern-input q-mb-md')
            cover_url = ui.input('🖼️ Kapak Fotoğrafı URL', value=book['cover_url'] or '').classes('w-full modern-input q-mb-md')
            total_copies = ui.number('📦 Toplam Kopya Sayısı', min=1, value=book['total_copies']).classes('w-full modern-input q-mb-md')
            
            def save_book():
                conn = get_db()
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                
                cursor.execute('''
                    UPDATE books 
                    SET title=%s, author=%s, description=%s, published_year=%s, isbn=%s, category=%s, cover_url=%s, total_copies=%s
                    WHERE id=%s
                ''', (title.value, author.value, description.value, published_year.value, isbn.value, category.value, cover_url.value, total_copies.value, book_id))
                
                conn.commit()
                conn.close()
                
                ui.notify('✅ Kitap başarıyla güncellendi!', type='positive')
                ui.navigate.to('/catalog')
            
            ui.button('💾 Kaydet', on_click=save_book).classes('modern-button bg-green q-mt-md')



# Run the app
if __name__ == '__main__':
    ui.run(
        title='📚 Kütüphane Yönetim Sistemi',
        port=8080,
        host='0.0.0.0',  # Docker için tüm interface'leri dinle
        reload=False,
        show=False,  # Docker'da GUI gösterme
        websocket_ping_interval=30,  # WebSocket ping aralığı
        websocket_ping_timeout=10,   # WebSocket ping timeout
        favicon='📚',  # Favicon
        dark=False,  # Light mode
        storage_secret='library_secret_key_2024'  # Session storage secret
    )
