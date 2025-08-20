import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.secret_key="supersecret123"

# Veritabanı bağlantısı (/tmp/ altına taşındı)
db_path = os.path.join("/tmp", "cafe.db")
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Masalar Modeli
class Masa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kat = db.Column(db.String(10))
    siparis_durum = db.Column(db.Integer, default=0)  # 0: boş, 1: dolu

# Ürünler Modeli
class Urun(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    isim = db.Column(db.String(100))
    fiyat = db.Column(db.Float)

# Siparişler Modeli
class Siparis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    masa_id = db.Column(db.Integer, db.ForeignKey('masa.id'))
    urun_id = db.Column(db.Integer, db.ForeignKey('urun.id'))
    adet = db.Column(db.Integer)
    
    # İlişkiler
    masa = db.relationship('Masa', backref='siparisler')
    urun = db.relationship('Urun', backref='siparisler')

# Satışlar Modeli (hesap kapatıldığında)
class Satis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    urun_isim = db.Column(db.String(100))
    adet = db.Column(db.Integer)
    fiyat = db.Column(db.Float)
    toplam = db.Column(db.Float)
    tarih = db.Column(db.DateTime, default=datetime.utcnow)

# YENİ: Envanter Modeli
class Envanter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    urun_id = db.Column(db.Integer, db.ForeignKey('urun.id'))
    baslangic_stok = db.Column(db.Integer)
    kalan_stok = db.Column(db.Integer)
    tarih = db.Column(db.DateTime, default=datetime.utcnow)
    
    # İlişki
    urun = db.relationship('Urun', backref='envanter')

# Veritabanı tablosunu oluştur ve örnek veri ekle
with app.app_context():
    db.create_all()
    
    # Örnek masalar ekle (eğer yoksa)
    if Masa.query.count() == 0:
        ornekler = [
            Masa(kat="1"), Masa(kat="1"), Masa(kat="1"), Masa(kat="1"),
            Masa(kat="2"), Masa(kat="2"), Masa(kat="2"), Masa(kat="2"),
            Masa(kat="Bahçe"), Masa(kat="Bahçe")
        ]
        for ornek in ornekler:
            db.session.add(ornek)
    
    # Örnek ürünler ekle (eğer yoksa)
    if Urun.query.count() == 0:
        ornekler = [
            Urun(isim="Çay", fiyat=5.0),
            Urun(isim="Türk Kahvesi", fiyat=12.0),
            Urun(isim="Filtre Kahve", fiyat=15.0),
            Urun(isim="Cappuccino", fiyat=18.0),
            Urun(isim="Latte", fiyat=20.0),
            Urun(isim="Su", fiyat=2.0),
            Urun(isim="Kola", fiyat=8.0),
            Urun(isim="Tost", fiyat=15.0),
            Urun(isim="Sandviç", fiyat=22.0),
            Urun(isim="Krep", fiyat=25.0)
        ]
        for ornek in ornekler:
            db.session.add(ornek)
    
    db.session.commit()

# Ana sayfa
@app.route('/')
def index():
    return redirect(url_for('management'))

# Yönetim Paneli Route
@app.route('/management')
def management():
    masalar = Masa.query.all()
    urunler = Urun.query.all()
    
    # Her masa için sipariş bilgilerini hesapla
    masa_bilgileri = []
    for masa in masalar:
        siparisler = Siparis.query.filter_by(masa_id=masa.id).all()
        toplam = sum(siparis.adet * siparis.urun.fiyat for siparis in siparisler)
        masa_bilgileri.append({
            'masa': masa,
            'siparisler': siparisler,
            'toplam': toplam,
            'siparis_sayisi': len(siparisler)
        })
    
    return render_template('management.html', masa_bilgileri=masa_bilgileri, urunler=urunler)

# Garson Paneli Route
@app.route('/worker')
def worker():
    masalar = Masa.query.all()
    urunler = Urun.query.all()
    
    # Her masa için sipariş bilgilerini hesapla
    masa_bilgileri = []
    for masa in masalar:
        siparisler = Siparis.query.filter_by(masa_id=masa.id).all()
        toplam = sum(siparis.adet * siparis.urun.fiyat for siparis in siparisler)
        masa_bilgileri.append({
            'masa': masa,
            'siparisler': siparisler,
            'toplam': toplam,
            'siparis_sayisi': len(siparisler)
        })
    
    return render_template('worker.html', masa_bilgileri=masa_bilgileri, urunler=urunler)

# Masa ekleme
@app.route('/add_masa', methods=['POST'])
def add_masa():
    kat = request.form['kat']
    if kat:
        yeni_masa = Masa(kat=kat)
        db.session.add(yeni_masa)
        db.session.commit()
        flash('Masa başarıyla eklendi!', 'success')
    else:
        flash('Kat bilgisi gerekli!', 'error')
    return redirect(url_for('management'))

# Masa silme
@app.route('/delete_masa/<int:masa_id>')
def delete_masa(masa_id):
    masa = Masa.query.get_or_404(masa_id)
    # Masada aktif sipariş var mı kontrol et
    siparisler = Siparis.query.filter_by(masa_id=masa_id).all()
    if siparisler:
        flash('Bu masada aktif siparişler bulunuyor!', 'error')
    else:
        db.session.delete(masa)
        db.session.commit()
        flash('Masa başarıyla silindi!', 'success')
    return redirect(url_for('management'))

# Ürün ekleme
@app.route('/add_urun', methods=['POST'])
def add_urun():
    isim = request.form['isim']
    fiyat = request.form['fiyat']
    if isim and fiyat:
        try:
            fiyat_float = float(fiyat)
            yeni_urun = Urun(isim=isim, fiyat=fiyat_float)
            db.session.add(yeni_urun)
            db.session.commit()
            flash('Ürün başarıyla eklendi!', 'success')
        except ValueError:
            flash('Geçersiz fiyat formatı!', 'error')
    else:
        flash('Ürün adı ve fiyat gerekli!', 'error')
    return redirect(url_for('management'))

# Ürün silme
@app.route('/delete_urun/<int:urun_id>')
def delete_urun(urun_id):
    urun = Urun.query.get_or_404(urun_id)
    # Ürün aktif siparişlerde kullanılıyor mu kontrol et
    siparisler = Siparis.query.filter_by(urun_id=urun_id).all()
    if siparisler:
        flash('Bu ürün aktif siparişlerde kullanılıyor!', 'error')
    else:
        db.session.delete(urun)
        db.session.commit()
        flash('Ürün başarıyla silindi!', 'success')
    return redirect(url_for('management'))

# Sipariş ekleme
@app.route('/add_order', methods=['POST'])
def add_order():
    masa_id = request.form['masa_id']
    urun_id = request.form['urun_id']
    adet = request.form['adet']
    
    if masa_id and urun_id and adet:
        try:
            adet_int = int(adet)
            if adet_int > 0:
                # Aynı masa ve ürün varsa adet artır, yoksa yeni sipariş ekle
                mevcut_siparis = Siparis.query.filter_by(masa_id=masa_id, urun_id=urun_id).first()
                if mevcut_siparis:
                    mevcut_siparis.adet += adet_int
                else:
                    yeni_siparis = Siparis(masa_id=masa_id, urun_id=urun_id, adet=adet_int)
                    db.session.add(yeni_siparis)
                
                # Masa durumunu güncelle
                masa = Masa.query.get(masa_id)
                masa.siparis_durum = 1
                
                db.session.commit()
                flash('Sipariş başarıyla eklendi!', 'success')
            else:
                flash('Adet 0\'dan büyük olmalı!', 'error')
        except ValueError:
            flash('Geçersiz adet formatı!', 'error')
    else:
        flash('Tüm alanlar doldurulmalı!', 'error')
    
    # Hangi sayfadan geldiğini kontrol et
    return redirect(request.referrer or url_for('management'))

# Sipariş silme
@app.route('/delete_order/<int:siparis_id>')
def delete_order(siparis_id):
    siparis = Siparis.query.get_or_404(siparis_id)
    masa_id = siparis.masa_id
    
    db.session.delete(siparis)
    
    # Masada başka sipariş var mı kontrol et
    kalan_siparisler = Siparis.query.filter_by(masa_id=masa_id).all()
    if not kalan_siparisler:
        masa = Masa.query.get(masa_id)
        masa.siparis_durum = 0
    
    db.session.commit()
    flash('Sipariş başarıyla silindi!', 'success')
    return redirect(request.referrer or url_for('management'))

# Hesap kapatma - GÜNCELLENMIŞ: Envanter güncelleme eklendi
@app.route('/close_bill/<int:masa_id>')
def close_bill(masa_id):
    masa = Masa.query.get_or_404(masa_id)
    siparisler = Siparis.query.filter_by(masa_id=masa_id).all()
    
    if not siparisler:
        flash('Bu masada kapatılacak sipariş yok!', 'error')
        return redirect(request.referrer or url_for('management'))
    
    # Satışlara kaydet ve envanteri güncelle
    toplam_tutar = 0
    for siparis in siparisler:
        tutar = siparis.adet * siparis.urun.fiyat
        satis = Satis(
            urun_isim=siparis.urun.isim,
            adet=siparis.adet,
            fiyat=siparis.urun.fiyat,
            toplam=tutar
        )
        db.session.add(satis)
        toplam_tutar += tutar
        
        # YENİ: Envanteri güncelle - stoktan düş
        envanter_item = Envanter.query.filter_by(urun_id=siparis.urun_id).first()
        if envanter_item:
            if envanter_item.kalan_stok >= siparis.adet:
                envanter_item.kalan_stok -= siparis.adet
            else:
                envanter_item.kalan_stok = 0  # Stok eksilere düşmesin
    
    # Siparişleri sil
    for siparis in siparisler:
        db.session.delete(siparis)
    
    # Masa durumunu güncelle
    masa.siparis_durum = 0
    
    db.session.commit()
    flash(f'Hesap kapatıldı! Toplam: {toplam_tutar:.2f} TL', 'success')
    return redirect(request.referrer or url_for('management'))

# API endpoint - masa detayları
@app.route('/api/masa/<int:masa_id>')
def api_masa_detay(masa_id):
    masa = Masa.query.get_or_404(masa_id)
    siparisler = Siparis.query.filter_by(masa_id=masa_id).all()
    
    siparis_listesi = []
    toplam = 0
    for siparis in siparisler:
        tutar = siparis.adet * siparis.urun.fiyat
        siparis_listesi.append({
            'id': siparis.id,
            'urun_isim': siparis.urun.isim,
            'adet': siparis.adet,
            'fiyat': siparis.urun.fiyat,
            'tutar': tutar
        })
        toplam += tutar
    
    return jsonify({
        'masa': {
            'id': masa.id,
            'kat': masa.kat,
            'siparis_durum': masa.siparis_durum
        },
        'siparisler': siparis_listesi,
        'toplam': toplam
    })

# Satış raporu - GÜNCELLENMIŞ: Envanter bilgileri eklendi
@app.route('/report')
def report():
    satislar = Satis.query.order_by(Satis.tarih.desc()).all()
    toplam_ciro = sum(satis.toplam for satis in satislar)
    urunler = Urun.query.all()
    envanter_listesi = Envanter.query.all()
    
    # Envanter bilgilerini hazırla
    envanter_bilgileri = []
    for envanter in envanter_listesi:
        # Bu ürün için toplam satış miktarını hesapla
        toplam_satis = sum(satis.adet for satis in satislar if satis.urun_isim == envanter.urun.isim)
        tüketilen = envanter.baslangic_stok - envanter.kalan_stok
        
        envanter_bilgileri.append({
            'envanter': envanter,
            'tüketilen': tüketilen,
            'yuzde': (tüketilen / envanter.baslangic_stok * 100) if envanter.baslangic_stok > 0 else 0
        })
    
    return render_template('report.html', 
                         satislar=satislar, 
                         toplam_ciro=toplam_ciro,
                         urunler=urunler,
                         envanter_bilgileri=envanter_bilgileri)

# YENİ: Envanter ekleme
@app.route('/add_envanter', methods=['POST'])
def add_envanter():
    urun_id = request.form['urun_id']
    stok_miktari = request.form['stok_miktari']
    
    if urun_id and stok_miktari:
        try:
            stok_int = int(stok_miktari)
            if stok_int >= 0:
                # Aynı ürün varsa güncelle, yoksa yeni ekle
                mevcut_envanter = Envanter.query.filter_by(urun_id=urun_id).first()
                if mevcut_envanter:
                    mevcut_envanter.baslangic_stok = stok_int
                    mevcut_envanter.kalan_stok = stok_int
                    mevcut_envanter.tarih = datetime.utcnow()
                else:
                    yeni_envanter = Envanter(
                        urun_id=urun_id,
                        baslangic_stok=stok_int,
                        kalan_stok=stok_int
                    )
                    db.session.add(yeni_envanter)
                
                db.session.commit()
                flash('Envanter başarıyla eklendi/güncellendi!', 'success')
            else:
                flash('Stok miktarı 0 veya pozitif olmalı!', 'error')
        except ValueError:
            flash('Geçersiz stok miktarı formatı!', 'error')
    else:
        flash('Ürün ve stok miktarı gerekli!', 'error')
    
    return redirect(url_for('report'))

# YENİ: Envanter silme
@app.route('/delete_envanter/<int:envanter_id>')
def delete_envanter(envanter_id):
    envanter = Envanter.query.get_or_404(envanter_id)
    db.session.delete(envanter)
    db.session.commit()
    flash('Envanter kaydı başarıyla silindi!', 'success')
    return redirect(url_for('report'))

# Satış verilerini temizle
@app.route('/clear_sales', methods=['POST'])
def clear_sales():
    try:
        Satis.query.delete()
        db.session.commit()
        flash('Tüm satış verileri başarıyla temizlendi!', 'success')
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        flash('Veriler temizlenirken hata oluştu!', 'error')
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run()

