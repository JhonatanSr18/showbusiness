console.log("JS carregou");

const secoes = document.querySelectorAll("section");
const botoes = document.querySelectorAll(".btns-header a");

window.addEventListener("scroll", () => {
  let secaoAtual = "";

  secoes.forEach((secao) => {
    const topoSecao = secao.offsetTop;
    const alturaSecao = secao.offsetHeight;

    if (window.scrollY >= topoSecao - alturaSecao / 3) {
      secaoAtual = secao.id;
    }
  });

  botoes.forEach((botao) => {
    botao.classList.remove("ativo");

    if (botao.getAttribute("href") === `#${secaoAtual}`) {
      botao.classList.add("ativo");
    }
  });
});

const slides = document.querySelectorAll(".slide");
const indicadores = document.querySelectorAll(".indicador");

let slideAtual = 0;

function mostrarSlide(index) {
  slides.forEach((slide) => {
    slide.classList.remove("ativo");
  });

  indicadores.forEach((indicador) => {
    indicador.classList.remove("ativo");
  });

  slides[index].classList.add("ativo");
  indicadores[index].classList.add("ativo");

  slideAtual = index;
}

function proximoSlide() {
  let proximo = slideAtual + 1;

  if (proximo >= slides.length) {
    proximo = 0;
  }

  mostrarSlide(proximo);
}

setInterval(proximoSlide, 4000);

indicadores.forEach((indicador, index) => {
  indicador.addEventListener("click", () => {
    mostrarSlide(index);
  });
});
