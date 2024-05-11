window.onload = function() {
    if (document.querySelector('.error-container')) {
        document.querySelector('.error-container').style.display = 'block';
    }
}

document.querySelector('.error__close').onclick = function() {
    document.querySelector('.error-container').style.display = 'none';
}