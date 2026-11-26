
import mysql.connector
from mysql.connector import Error


def buat_koneksi():
    try:
        koneksi = mysql.connector.connect(
            host="localhost",
            user="root",
            password=""
        )

        if koneksi.is_connected():
            cursor = koneksi.cursor()
            cursor.execute(
                "CREATE DATABASE IF NOT EXISTS keuangan_pribadi"
            )
            cursor.close()
            koneksi.database = "keuangan_pribadi"

            print("Database berhasil terhubung!")
            return koneksi

    except Error as e:
        print("Koneksi gagal:", e)
        return None


def buat_tabel():
    koneksi = buat_koneksi()

    if koneksi is None:
        return

    cursor = koneksi.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pengguna (
            id_pengguna INT AUTO_INCREMENT PRIMARY KEY,
            nama VARCHAR(100) NOT NULL,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            role ENUM('Admin','Pengguna')
                NOT NULL DEFAULT 'Pengguna'
        )
    """)

    cursor.execute("""
        INSERT IGNORE INTO pengguna
        (nama, username, password, role)
        VALUES ('Admin', 'admin', 'admin', 'Admin')
    """)

    # Menambahkan kolom role jika tabel lama belum memilikinya
    cursor.execute("SHOW COLUMNS FROM pengguna LIKE 'role'")

    if cursor.fetchone() is None:
        cursor.execute("""
            ALTER TABLE pengguna
            ADD COLUMN role ENUM('Admin','Pengguna')
            NOT NULL DEFAULT 'Pengguna'
        """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kategori (
            id_kategori INT AUTO_INCREMENT PRIMARY KEY,
            nama_kategori VARCHAR(100) NOT NULL,
            jenis ENUM('Pemasukan','Pengeluaran') NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transaksi (
            id_transaksi INT AUTO_INCREMENT PRIMARY KEY,
            id_pengguna INT NOT NULL,
            id_kategori INT NOT NULL,
            jenis ENUM('Pemasukan','Pengeluaran') NOT NULL,
            jumlah DECIMAL(15,2) NOT NULL,
            keterangan TEXT,
            tanggal DATE NOT NULL,
            FOREIGN KEY (id_pengguna)
                REFERENCES pengguna(id_pengguna),
            FOREIGN KEY (id_kategori)
                REFERENCES kategori(id_kategori)
        )
    """)

    # Akun admin awal
    cursor.execute("""
        INSERT IGNORE INTO pengguna
        (nama, username, password, role)
        VALUES ('Admin', 'admin', 'admin', 'Admin')
    """)

    cursor.execute("""
        UPDATE pengguna
        SET role='Admin'
        WHERE username='admin'
    """)

    koneksi.commit()
    cursor.close()
    koneksi.close()

    print("Semua tabel berhasil dibuat!")


def isi_kategori_awal():
    koneksi = buat_koneksi()

    if koneksi is None:
        return

    cursor = koneksi.cursor()

    data = [
        ("Gaji", "Pemasukan"),
        ("Uang Saku", "Pemasukan"),
        ("Bonus", "Pemasukan"),
        ("Makanan", "Pengeluaran"),
        ("Transportasi", "Pengeluaran"),
        ("Belanja", "Pengeluaran"),
        ("Pendidikan", "Pengeluaran"),
        ("Lainnya", "Pengeluaran")
    ]

    for nama, jenis in data:
        cursor.execute(
            "SELECT id_kategori FROM kategori "
            "WHERE nama_kategori=%s AND jenis=%s",
            (nama, jenis)
        )

        if cursor.fetchone() is None:
            cursor.execute(
                "INSERT INTO kategori "
                "(nama_kategori, jenis) VALUES (%s, %s)",
                (nama, jenis)
            )

    koneksi.commit()
    cursor.close()
    koneksi.close()

    print("Kategori berhasil ditambahkan!")
