const buscaEvento = document.getElementById("buscaEvento");
const filtroCidade = document.getElementById("filtroCidade");
const cards = document.querySelectorAll(".evento-card");

function filtrarEventos() {
  const textoBusca = buscaEvento.value.toLowerCase().trim();

  const cidadeSelecionada = filtroCidade.value;

  cards.forEach((card) => {
    const textoCard = card.textContent.toLowerCase();

    const cidadeCard = card.dataset.cidade;

    const nomeCorresponde = textoCard.includes(textoBusca);

    const cidadeCorresponde =
      cidadeSelecionada === "todos" || cidadeCard === cidadeSelecionada;

    if (nomeCorresponde && cidadeCorresponde) {
      card.style.display = "flex";
    } else {
      card.style.display = "none";
    }
  });
}

buscaEvento.addEventListener("input", filtrarEventos);

filtroCidade.addEventListener("change", filtrarEventos);
