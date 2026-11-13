function showLesson(id) {
    document.querySelectorAll('.lesson').forEach(item => {
        item.style.display = 'none';
    });

    const lesson = document.getElementById(id);
    lesson.style.display = 'block';

    lesson.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
    });
}

document.getElementById('search').addEventListener('input', function() {
    const value = this.value.trim().toLowerCase();

    document.querySelectorAll('.card').forEach(card => {
        card.style.display =
            card.innerText.toLowerCase().includes(value)
            ? 'block' : 'none';
    });
});
