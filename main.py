
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from koneksi import buat_koneksi, buat_tabel, isi_kategori_awal


# WARNA APLIKASI
BG = "#F4F6FA"
PRIMARY = "#6C63FF"
GREEN = "#16A085"
RED = "#E74C3C"
WHITE = "#FFFFFF"

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Login Aplikasi Keuangan")
        self.root.geometry("400x350")
        self.root.configure(bg=BG)

        tk.Label(
            root,
            text="LOGIN APLIKASI KEUANGAN",
            font=("Arial", 16, "bold"),
            bg=BG
        ).pack(pady=25)

        tk.Label(root, text="Username", bg=BG).pack()
        self.username = tk.Entry(root, width=30)
        self.username.pack(pady=5)

        tk.Label(root, text="Password", bg=BG).pack()
        self.password = tk.Entry(root, width=30, show="*")
        self.password.pack(pady=5)

        tk.Button(
            root,
            text="LOGIN",
            bg=PRIMARY,
            fg="white",
            width=20,
            command=self.login
        ).pack(pady=20)

        tk.Button(
            root,
            text="DAFTAR AKUN",
            bg=GREEN,
            fg="white",
            width=20,
            command=self.daftar
        ).pack(pady=5)

    def login(self):
        username = self.username.get()
        password = self.password.get()

        koneksi = buat_koneksi()

        if koneksi is None:
            messagebox.showerror("Error", "Database tidak terhubung!")
            return

        cursor = koneksi.cursor()
        cursor.execute(
            "SELECT id_pengguna, nama, role FROM pengguna "
            "WHERE username=%s AND password=%s",
            (username, password)
        )

        data = cursor.fetchone()
        cursor.close()
        koneksi.close()

        if data:
            self.root.destroy()
            root_baru = tk.Tk()
            AplikasiKeuangan(root_baru, data[0], data[1], data[2])
            root_baru.mainloop()
        else:
            messagebox.showerror(
                "Login Gagal",
                "Username atau password salah!"
            )

    def daftar(self):
        jendela = tk.Toplevel(self.root)
        jendela.title("Daftar Akun")
        jendela.geometry("350x350")
        jendela.configure(bg=BG)

        tk.Label(
            jendela,
            text="DAFTAR AKUN",
            font=("Arial", 16, "bold"),
            bg=BG
        ).pack(pady=15)

        tk.Label(jendela, text="Nama", bg=BG).pack()
        nama = tk.Entry(jendela, width=30)
        nama.pack(pady=5)

        tk.Label(jendela, text="Username", bg=BG).pack()
        username = tk.Entry(jendela, width=30)
        username.pack(pady=5)

        tk.Label(jendela, text="Password", bg=BG).pack()
        password = tk.Entry(jendela, width=30, show="*")
        password.pack(pady=5)

        def simpan_akun():
            n = nama.get().strip()
            u = username.get().strip()
            p = password.get()

            if not n or not u or not p:
                messagebox.showwarning(
                    "Peringatan", "Semua kolom harus diisi!"
                )
                return

            koneksi = buat_koneksi()
            if koneksi is None:
                messagebox.showerror("Error", "Database gagal terhubung!")
                return

            cursor = koneksi.cursor()
            try:
                cursor.execute(
                    "INSERT INTO pengguna "
                    "(nama, username, password, role) "
                    "VALUES (%s, %s, %s, 'Pengguna')",
                    (n, u, p)
                )
                koneksi.commit()
                messagebox.showinfo("Berhasil", "Akun berhasil dibuat!")
                jendela.destroy()

            except Exception:
                messagebox.showerror(
                    "Gagal",
                    "Username sudah digunakan atau terjadi kesalahan."
                )
            finally:
                cursor.close()
                koneksi.close()

        tk.Button(
            jendela,
            text="SIMPAN AKUN",
            bg=GREEN,
            fg="white",
            command=simpan_akun
        ).pack(pady=20)

class AplikasiKeuangan:
    def __init__(self, root, id_pengguna, nama, role):
        self.root = root
        self.root.title("Aplikasi Keuangan Pribadi")
        self.root.geometry("1100x700")
        self.root.configure(bg=BG)

        buat_tabel()
        isi_kategori_awal()
    
        self.koneksi = buat_koneksi()

        if not self.koneksi:
            messagebox.showerror(
                "Error",
                "Database tidak dapat dihubungkan!"
            )
            root.destroy()
            return

        self.cursor = self.koneksi.cursor()

        self.id_pengguna = id_pengguna
        self.nama_pengguna = nama
        self.role = role

        self.buat_tampilan()
        self.muat_kategori()
        self.tampilkan_data()

    def buat_tampilan(self):

        # HEADER
        header = tk.Frame(
            self.root,
            bg=PRIMARY,
            height=75
        )
        header.pack(fill="x")

        tk.Label(
            header,
            text="KEUANGAN PRIBADI",
            font=("Arial", 22, "bold"),
            fg=WHITE,
            bg=PRIMARY
        ).pack(side="left", padx=25, pady=18)

        tk.Button(
            header,
            text="LOGOUT",
            bg=RED,
            fg=WHITE,
            font=("Arial", 10, "bold"),
            command=self.logout
        ).pack(side="right", padx=25, pady=18)

        # RINGKASAN SALDO
        ringkasan = tk.Frame(self.root, bg=BG)
        ringkasan.pack(fill="x", padx=20, pady=15)

        self.label_masuk = self.kartu(
            ringkasan, "TOTAL PEMASUKAN", GREEN
        )

        self.label_keluar = self.kartu(
            ringkasan, "TOTAL PENGELUARAN", RED
        )

        self.label_saldo = self.kartu(
            ringkasan, "SALDO SEKARANG", PRIMARY
        )

        # FORM TRANSAKSI
        form = tk.LabelFrame(
            self.root,
            text=" Input Transaksi ",
            font=("Arial", 12, "bold"),
            bg=WHITE,
            padx=15,
            pady=15
        )
        form.pack(fill="x", padx=20, pady=10)

        tk.Label(form, text="Jenis", bg=WHITE).grid(
            row=0, column=0, sticky="w"
        )

        self.jenis = ttk.Combobox(
            form,
            values=["Pemasukan", "Pengeluaran"],
            state="readonly",
            width=20
        )
        self.jenis.grid(row=1, column=0, padx=5, pady=5)
        self.jenis.set("Pemasukan")

        tk.Label(form, text="Kategori", bg=WHITE).grid(
            row=0, column=1, sticky="w"
        )

        self.kategori = ttk.Combobox(
            form,
            state="readonly",
            width=20
        )
        self.kategori.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form, text="Jumlah (Rp)", bg=WHITE).grid(
            row=0, column=2, sticky="w"
        )

        self.jumlah = tk.Entry(form, width=22)
        self.jumlah.grid(row=1, column=2, padx=5, pady=5)

        tk.Label(form, text="Keterangan", bg=WHITE).grid(
            row=0, column=3, sticky="w"
        )

        self.keterangan = tk.Entry(form, width=25)
        self.keterangan.grid(row=1, column=3, padx=5, pady=5)

        tk.Label(form, text="Tanggal (YYYY-MM-DD)", bg=WHITE).grid(
            row=0, column=4, sticky="w"
        )

        self.tanggal = tk.Entry(form, width=18)
        self.tanggal.grid(row=1, column=4, padx=5, pady=5)
        self.tanggal.insert(0, str(date.today()))

        # TOMBOL
        tombol = tk.Frame(self.root, bg=BG)
        tombol.pack(fill="x", padx=20, pady=5)

        self.tombol(
            tombol, "Simpan", GREEN, self.simpan
        )
        self.tombol(
            tombol, "Edit", PRIMARY, self.edit
        )
        self.tombol(
            tombol, "Hapus", RED, self.hapus
        )
        self.tombol(
            tombol, "Bersihkan", "#7F8C8D",
            self.bersihkan
        )
        self.tombol(
            tombol, "Grafik", "#E67E22",
            self.grafik
        )


        # TABEL DATA
        tabel_frame = tk.Frame(self.root, bg=WHITE)
        tabel_frame.pack(
            fill="both", expand=True,
            padx=20, pady=15
        )

        kolom = (
            "ID", "Jenis", "Kategori",
            "Jumlah", "Keterangan", "Tanggal"
        )

        self.tabel = ttk.Treeview(
            tabel_frame,
            columns=kolom,
            show="headings"
        )

        for nama in kolom:
            self.tabel.heading(nama, text=nama)
            self.tabel.column(nama, width=150)

        self.tabel.column("ID", width=50)
        self.tabel.pack(
            fill="both", expand=True, padx=10, pady=10
        )

        self.tabel.bind(
            "<<TreeviewSelect>>",
            self.pilih_data
        )

    def logout(self):
        konfirmasi = messagebox.askyesno(
            "Logout",
            "Apakah kamu yakin ingin keluar?"
        )

        if konfirmasi:
            self.root.destroy()
            root_baru = tk.Tk()
            LoginWindow(root_baru)
            root_baru.mainloop()

    def kartu(self, parent, judul, warna):
        frame = tk.Frame(
            parent, bg=WHITE,
            highlightbackground=warna,
            highlightthickness=2
        )
        frame.pack(
            side="left", fill="x",
            expand=True, padx=8
        )

        tk.Label(
            frame, text=judul,
            bg=WHITE, fg=warna,
            font=("Arial", 11, "bold")
        ).pack(pady=10)

        label = tk.Label(
            frame, text="Rp 0",
            bg=WHITE, fg="#222222",
            font=("Arial", 17, "bold")
        )
        label.pack(pady=10)

        return label

    def tombol(self, parent, teks, warna, perintah):
        tk.Button(
            parent,
            text=teks,
            bg=warna,
            fg=WHITE,
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=15,
            pady=9,
            command=perintah,
            cursor="hand2"
        ).pack(side="left", padx=5)

    def muat_kategori(self):
        self.cursor.execute(
            "SELECT nama_kategori FROM kategori "
            "WHERE jenis=%s",
            (self.jenis.get(),)
        )

        data = [baris[0] for baris in self.cursor.fetchall()]
        self.kategori["values"] = data

        if data:
            self.kategori.current(0)

        self.jenis.bind(
            "<<ComboboxSelected>>",
            lambda event: self.muat_kategori()
        )

    def tampilkan_data(self):
        for item in self.tabel.get_children():
            self.tabel.delete(item)

        self.cursor.execute("""
            SELECT t.id_transaksi, t.jenis,
                   k.nama_kategori, t.jumlah,
                   t.keterangan, t.tanggal
            FROM transaksi t
            JOIN kategori k
            ON t.id_kategori = k.id_kategori
            WHERE t.id_pengguna = %s
            ORDER BY t.tanggal DESC, t.id_transaksi DESC
        """, (self.id_pengguna,))

        for data in self.cursor.fetchall():
            self.tabel.insert("", "end", values=data)

        self.hitung_saldo()

    def hitung_saldo(self):
        self.cursor.execute("""
            SELECT jenis, SUM(jumlah)
            FROM transaksi
            WHERE id_pengguna=%s
            GROUP BY jenis
        """, (self.id_pengguna,))

        hasil = dict(self.cursor.fetchall())

        masuk = float(hasil.get("Pemasukan") or 0)
        keluar = float(hasil.get("Pengeluaran") or 0)
        saldo = masuk - keluar

        self.label_masuk.config(
            text=f"Rp {masuk:,.0f}"
        )
        self.label_keluar.config(
            text=f"Rp {keluar:,.0f}"
        )
        self.label_saldo.config(
            text=f"Rp {saldo:,.0f}"
        )

    def simpan(self):
        try:
            jenis = self.jenis.get()
            kategori = self.kategori.get()
            jumlah = float(self.jumlah.get())
            keterangan = self.keterangan.get()
            tanggal = self.tanggal.get()

            if not kategori or jumlah <= 0:
                raise ValueError()

            self.cursor.execute(
                "SELECT id_kategori FROM kategori "
                "WHERE nama_kategori=%s AND jenis=%s",
                (kategori, jenis)
            )
            id_kategori = self.cursor.fetchone()

            if not id_kategori:
                messagebox.showerror(
                    "Error", "Kategori tidak ditemukan!"
                )
                return

            self.cursor.execute("""
                INSERT INTO transaksi
                (id_pengguna, id_kategori, jenis,
                 jumlah, keterangan, tanggal)
                VALUES (%s,%s,%s,%s,%s,%s)
            """, (
                self.id_pengguna,
                id_kategori[0],
                jenis,
                jumlah,
                keterangan,
                tanggal
            ))

            self.koneksi.commit()
            messagebox.showinfo(
                "Berhasil", "Transaksi berhasil disimpan!"
            )
            self.bersihkan()
            self.tampilkan_data()

        except ValueError:
            messagebox.showerror(
                "Peringatan",
                "Isi jumlah dengan angka positif dan tanggal yang benar!"
            )
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def pilih_data(self, event):
        pilihan = self.tabel.selection()

        if pilihan:
            data = self.tabel.item(pilihan[0])["values"]

            self.id_pilihan = data[0]
            self.jenis.set(data[1])
            self.muat_kategori()
            self.kategori.set(data[2])

            self.jumlah.delete(0, tk.END)
            self.jumlah.insert(0, data[3])

            self.keterangan.delete(0, tk.END)
            self.keterangan.insert(0, data[4] or "")

            self.tanggal.delete(0, tk.END)
            self.tanggal.insert(0, data[5])

    def edit(self):
        if not hasattr(self, "id_pilihan"):
            messagebox.showwarning(
                "Peringatan", "Pilih transaksi terlebih dahulu!"
            )
            return

        try:
            self.cursor.execute(
                "SELECT id_kategori FROM kategori "
                "WHERE nama_kategori=%s AND jenis=%s",
                (self.kategori.get(), self.jenis.get())
            )
            kategori = self.cursor.fetchone()

            if not kategori:
                messagebox.showerror(
                    "Error", "Kategori tidak ditemukan!"
                )
                return

            self.cursor.execute("""
                UPDATE transaksi
                SET jenis=%s, id_kategori=%s,
                    jumlah=%s, keterangan=%s, tanggal=%s
                WHERE id_transaksi=%s AND id_pengguna=%s
            """, (
                self.jenis.get(),
                kategori[0],
                float(self.jumlah.get()),
                self.keterangan.get(),
                self.tanggal.get(),
                self.id_pilihan,
                self.id_pengguna
            ))

            self.koneksi.commit()
            self.bersihkan()
            self.tampilkan_data()

            messagebox.showinfo(
                "Berhasil", "Transaksi berhasil diedit!"
            )

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def hapus(self):
        if not hasattr(self, "id_pilihan"):
            messagebox.showwarning(
                "Peringatan", "Pilih transaksi terlebih dahulu!"
            )
            return

        if messagebox.askyesno(
            "Konfirmasi", "Hapus transaksi ini?"
        ):
            self.cursor.execute(
                "DELETE FROM transaksi "
                "WHERE id_transaksi=%s AND id_pengguna=%s",
                (self.id_pilihan, self.id_pengguna)
            )

            self.koneksi.commit()
            self.bersihkan()
            self.tampilkan_data()

    def bersihkan(self):
        self.jumlah.delete(0, tk.END)
        self.keterangan.delete(0, tk.END)
        self.tanggal.delete(0, tk.END)
        self.tanggal.insert(0, str(date.today()))

        if hasattr(self, "id_pilihan"):
            del self.id_pilihan

    def grafik(self):
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

        self.cursor.execute("""
            SELECT jenis, SUM(jumlah)
            FROM transaksi
            WHERE id_pengguna=%s
            GROUP BY jenis
        """, (self.id_pengguna,))

        data = dict(self.cursor.fetchall())

        masuk = float(data.get("Pemasukan") or 0)
        keluar = float(data.get("Pengeluaran") or 0)

        if masuk == 0 and keluar == 0:
            messagebox.showinfo(
                "Info", "Belum ada transaksi untuk dibuat grafik."
            )
            return

        jendela = tk.Toplevel(self.root)
        jendela.title("Grafik Keuangan")
        jendela.geometry("600x450")

        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)

        ax.bar(
            ["Pemasukan", "Pengeluaran"],
            [masuk, keluar],
            color=[GREEN, RED]
        )

        ax.set_title("Laporan Keuangan Pribadi")
        ax.set_ylabel("Jumlah Rupiah")

        canvas = FigureCanvasTkAgg(
            fig, master=jendela
        )
        canvas.draw()
        canvas.get_tk_widget().pack(
            fill="both", expand=True
        )


if __name__ == "__main__":
    buat_tabel()
    isi_kategori_awal()

    root = tk.Tk()
    app = LoginWindow(root)
    root.mainloop()
