<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Abu Bakra Masjid - Gallery</title>
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            background: #f2f2f2;
            text-align: center;
            padding: 20px;
        }
        h1 {
            font-family: 'Noto Nastaliq Urdu', serif;
            font-size: 36px;
            margin-bottom: 40px;
        }
        .slider {
            position: relative;
            max-width: 600px;
            margin: auto;
            overflow: hidden;
            border-radius: 12px;
            box-shadow: 0 0 15px rgba(0, 0, 0, 0.2);
        }
        .slides {
            display: flex;
            transition: transform 0.5s ease-in-out;
        }
        .slides img {
            width: 100%;
            border-radius: 12px;
        }
        .nav-btn {
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            background-color: rgba(0,0,0,0.6);
            color: white;
            border: none;
            padding: 12px;
            cursor: pointer;
            border-radius: 50%;
            font-size: 18px;
            z-index: 1000;
        }
        .prev {
            left: 10px;
        }
        .next {
            right: 10px;
        }
    </style>
    <!-- Urdu Font -->
    <link href="https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu&display=swap" rel="stylesheet">
</head>
<body>
    <h1>ابو بکرہ مسجد</h1>

    <div class="slider">
        <div class="slides" id="slides">
            <img src="{{ url_for('static', filename='assets/mosque_images/old_mosque.jpg') }}" alt="Old Mosque">
            <img src="{{ url_for('static', filename='assets/mosque_images/mosque1.jpg') }}" alt="Mosque 1">
            <img src="{{ url_for('static', filename='assets/mosque_images/mosque2.jpg') }}" alt="Mosque 2">
        </div>
        <button class="nav-btn prev" onclick="prevSlide()">&#10094;</button>
        <button class="nav-btn next" onclick="nextSlide()">&#10095;</button>
    </div>

    <script>
        let currentIndex = 0;
        const slides = document.getElementById("slides");
        const totalSlides = slides.children.length;

        function updateSlide() {
            slides.style.transform = `translateX(-${currentIndex * 100}%)`;
        }

        function nextSlide() {
            currentIndex = (currentIndex + 1) % totalSlides;
            updateSlide();
        }

        function prevSlide() {
            currentIndex = (currentIndex - 1 + totalSlides) % totalSlides;
            updateSlide();
        }
    </script>
</body>
</html>
