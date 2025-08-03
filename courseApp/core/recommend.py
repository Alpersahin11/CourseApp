from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.db.models import Count
from courses.models import Course

def recommend_similar_courses(base_course, top_n=5):
    # Tüm aktif kursları al (base_course dahil)
    all_courses = Course.objects.filter(is_active=True).annotate(
        student_count=Count('enrolled_students')
    )

    # Açıklamaları ve id’leri listele
    course_ids = []
    course_texts = []
    course_category_ids = []

    for course in all_courses:
        course_ids.append(course.id)
        course_texts.append(course.description or "")  # açıklama boşsa ""
        course_category_ids.append([cat.id for cat in course.category.all()])

    # TF-IDF vektörlerini oluştur
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(course_texts)

    # Base course’un index'ini bul
    try:
        base_index = course_ids.index(base_course.id)
    except ValueError:
        return []

    # Açıklama benzerliklerini hesapla
    similarities = cosine_similarity(tfidf_matrix[base_index], tfidf_matrix).flatten()

    # Ağırlıklı skor hesaplama
    course_scores = []

    for i, course in enumerate(all_courses):
        if course.id == base_course.id:
            continue

        # 1. Açıklama benzerliği (0–1)
        desc_score = similarities[i]

        # 2. Kategori benzerliği
        shared_categories = set([c.id for c in base_course.category.all()]) & set(course_category_ids[i])
        category_score = len(shared_categories) / max(len(course_category_ids[i]), 1)

        # 3. Öğrenci sayısı skoru (normalize edilmemiş ama yine etkili)
        popularity_score = course.student_count / 1000  # 1000’e bölüp küçültüyoruz

        # Ağırlıklı toplam
        total_score = (desc_score * 0.4) + (category_score * 0.4) + (popularity_score * 0.2)

        course_scores.append((course, total_score))

    # Skora göre sırala
    sorted_courses = sorted(course_scores, key=lambda x: x[1], reverse=True)

    # İlk n tanesini döndür
    return sorted_courses
