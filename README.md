<div align="center">
  <img src="asset\readme\allmember.png" width="100%" />
  <h1> 🧮Interactive Maths🧮</h1>

  [![Github Commit](https://img.shields.io/github/commit-activity/m/RamonR122140078/uas_tekmul_numeruno)](#)
  [![Github Contributors](https://img.shields.io/badge/all_contributors-3-blue.svg)](#)
</div>

## **🧮Daftar Isi**
[Deskripsi Proyek](#deskripsi-proyek)

[Anggota Tim](#anggota-tim)

[Teknologi aplikasi](#teknologi-applikasi)

[Instruksi Instalasi ](#instruksi-instalasi)

[Instruksi & Aturan Permaianan ](#instruksi-&-aturan-permainan)

[Logbook Mingguan](#logbook-mingguan)

[Laporan](#laporan)

[Demo Program](#demo-program)

## **🧮Deskripsi Proyek**
Interactive Maths adalah aplikasi interaktif yang menggabungkan pembelajaran matematika dasar dengan teknologi deteksi gestur tangan dan audio. Pengguna akan diberikan **lima soal acak** tentang penjumlahan, pengurangan, perkalian, atau pembagian secara bergantian. Jawaban diberikan dengan **menunjukkan jumlah jari tangan** sesuai hasil perhitungan.  

Sistem akan:  
1. Mendeteksi jumlah jari dari gestur tangan pengguna menggunakan kamera.  
2. Mengonversi gestur ke angka melalui audio (misal: "Lima").  
3. Memeriksa kebenaran jawaban dan memberikan umpan balik suara:  
   - "Anda Benar!" jika jawaban tepat.  
   - "Anda Salah, jika jawaban salah.  

Cocok untuk anak-anak dan siapa pun yang ingin belajar matematika dengan cara menyenangkan!

## **🧮Anggota Tim**
| [<img src="asset\readme\ramon.png" width="100px;"/><br /><sub><b>Ramon Riping</b></sub>](https://github.com/RamonR122140078)<br />122140078 <br /> | [<img src="asset\readme\desty.png" width="100px;"/><br /><sub><b>Desty Ananta Purba</b></sub>](https://github.com/destyananta)<br />122140076 <br /> | [<img src="asset\readme\fauzan.png" width="100px;"/><br /><sub><b>Muhammad Fauzan As Shabierin</b></sub>](https://github.com/Mfauzanasshabierin)<br />122140074 <br /> |
|--|--|--|

## **🧮Teknologi Aplikasi**
<div align="left">

| Name | Description |
| :---: | :---: |
| **Python** | Bahasa pemrograman utama yang digunakan dalam pengembangan aplikasi. |
| **MediaPipe** | Digunakan untuk melacak jumlah jari tangan secara real-time dengan akurasi tinggi. |
| **CV2 (OpenCV)** | Menangkap video dari webcam dan memprosesnya untuk digunakan oleh MediaPipe. |
| **NumPy** | Digunakan untuk pengolahan data numerik seperti koordinat jari dan logika evaluasi jawaban. |

</div>

## **🧮Instruksi Instalasi**
1. **Clone repositori**:  
```bash
git clone https://github.com/RamonR122140078/uas_tekmul_numeruno.git
cd uas-tekmul-numeruno
```

2. **Instal semua dependensi yang diperlukan**:
```bash
pip install -r requirements.txt
```

3. **Jalankan program**:
```bash
python main.py
```
## **🧮Instruksi & Aturan Permaianan**


## **🧮Logbook Mingguan**
| Minggu | Topik | Progress |
|--------|-------|----------|
| **Minggu 1** | Setup Proyek & Ide | - Menentukan konsep aplikasi<br>- Membuat repositori GitHub |
| **Minggu 2** | Mastering Github dan Inisiasi Fitur | - Membuat branch masing - masing<br>- Membuat desain dan asset proyek<br>- Membuat code untuk UI Menu<br> - Menerapkan MediaPipe Hand Landmarks |
| **Minggu 3** | Pembuatan Menu dan Permainan | - Menggabungkan Menu dan Hand Landmarks<br> - Mengatur Waktu Menjawab Per Pertanyaan |
| **Minggu 4** |                    |                            |
| **Minggu 5** |                    |                            |

## **🧮Laporan**
Laporan akhir proyek dapat diakses melalui:  
[Laporan](https://www.overleaf.com/read/krbpfdtybsws#f35f54)

## **🧮Demo Program**
Berikut adalah video demonstrasi dari program Interactive Maths:

<a href="https://youtu.be/yourdemoid" target="_blank">
  <img src="https://i.ytimg.com/vi/yourdemoid/maxresdefault.jpg" alt="Presentation Video">
</a>