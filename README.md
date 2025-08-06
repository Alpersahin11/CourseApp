# CourseApp

CourseApp, online eğitim platformlarının temel işlevlerini keşfetmek ve Django becerilerimi pekiştirmek amacıyla geliştirdiğim bir web uygulamasıdır. BTK Akademi'deki Sadık Turan hocamın eğitiminden ilham alarak, öğretmen ve öğrenci rolleriyle dinamik bir eğitim platformu oluşturmayı hedeflemektedir. Uygulama, yerel geliştirme ortamında tam işlevselliğe sahip bir prototip olarak çalışmaktadır.

## Özellikler

- **Rol Tabanlı Kullanıcı Yönetimi**  
- **İçerik Yönetim Modülü (CMS):** Öğretmenlerin içeriklerini yönetmesine olanak tanır  
- **Etkileşim ve Gelişim Takibi:** Öğrencilerin videoları takip edip not almalarını sağlar  
- **Başvuru Sistemi:** Öğretmen adaylarının başvurularını ilettiği mekanizma  
- **Duyarlı (Responsive) Tasarım:** Bootstrap 5 ile modern ve mobil uyumlu arayüz  

## Kullanılan Teknolojiler

- **Back-end:** Python, Django  
- **Front-end:** HTML5, CSS, JavaScript, Bootstrap 5  
- **Veritabanı:** SQLite  

## Kurulum ve Çalıştırma

1. Depoyu klonlayın:

```bash
git clone https://github.com/Alpersahin11/CourseApp.git
cd CourseApp
```

2. Sanal ortam oluşturun ve etkinleştirin:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```
3. Gerekli bağımlılıkları yükleyin:
```bash
pip install -r requirements.txt 
```
4. Veritabanını hazırlayın:
```bash
python manage.py migrate
python manage.py createsuperuser
```
5. Projeyi başlatın:
```bash
python manage.py runserver
```




