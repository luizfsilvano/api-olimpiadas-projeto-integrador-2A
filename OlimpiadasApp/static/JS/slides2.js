let indiceSlide = 1;
    exibirSlides(indiceSlide);

    function slideAtual(n) {
        exibirSlides(indiceSlide = n);
    }

    function exibirSlides(n) {
        let i;
        const slides = document.getElementsByClassName("apresentacao");
        const pontos = document.getElementsByClassName("ponto");
        if (n > slides.length) {indiceSlide = 1}
        if (n < 1) {indiceSlide = slides.length}
        for (i = 0; i < slides.length; i++) {
            slides[i].style.display = "none";
        }
        for (i = 0; i < pontos.length; i++) {
            pontos[i].className = pontos[i].className.replace(" ativo", "");
        }
        slides[indiceSlide-1].style.display = "block";
        pontos[indiceSlide-1].className += " ativo";
    }

    // Avança automaticamente os slides a cada 5 segundos
    setInterval(() => {
        exibirSlides(indiceSlide += 1);
    }, 5000);