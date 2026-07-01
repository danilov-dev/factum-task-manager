document.addEventListener('DOMContentLoaded', function () {
    const textarea = document.getElementById('id_about');
    const charCount = document.getElementById('char-count');
    const maxLength = parseInt(document.getElementById('char-max').textContent);

    function updateCounter() {
        const currentLength = textarea.value.length;
        charCount.textContent = currentLength;

        if (currentLength > maxLength) {
            charCount.style.color = 'red';
        } else {
            charCount.style.color = '';
        }
    }

    textarea.addEventListener('input', updateCounter);
    updateCounter();
});

document.addEventListener('DOMContentLoaded', function () {
    marked.setOptions({
        breaks: true,
        gfm: true
    });

    const textarea = document.querySelector("#id_description");
    const preview = document.getElementById('markdown-preview');

    // === Функция авто-высоты ===
    function autoResize() {
        textarea.style.height = 'auto';
        textarea.style.height = textarea.scrollHeight + 'px';

        const preview = document.querySelector('.markdown-editor__preview');
        if (preview) {
            preview.style.minHeight = textarea.scrollHeight + 'px';
        }
    }

    function updatePreview() {
        const markdown = textarea.value;
        if (markdown.trim() === '') {
            preview.innerHTML = '<p style="color: var(--text-secondary); font-style: italic;">Превью появится здесь...</p>';
        } else {
            const rawHtml = marked.parse(markdown);
            preview.innerHTML = DOMPurify.sanitize(rawHtml);
        }
    }

    textarea.addEventListener('input', function () {
        autoResize();
        updatePreview();
    });

    autoResize();
    updatePreview();

    window.addEventListener('resize', autoResize);
});