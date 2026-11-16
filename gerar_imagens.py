"""Gera a capa do LinkedIn e a imagem de prévia do site, no mesmo visual da página.

Saídas
    img/capa_linkedin.png  (1584 x 396)
    img/previa.png         (1200 x 630, usada nas etiquetas og:image)
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PASTA = Path(__file__).parent / "img"
FONTES = Path("C:/Windows/Fonts")
PRETA = str(FONTES / "seguibl.ttf")
MEDIA = str(FONTES / "seguisb.ttf")

LAVANDA = "#e6e1f5"
TINTA = "#111111"
CORES = ["#b02a6e", "#b5440e", "#106c47", "#5b3fd6"]


def faixas(d, x0, y0, x1, altura):
    largura = (x1 - x0) / len(CORES)
    for i, cor in enumerate(CORES):
        d.rectangle([x0 + i * largura, y0, x0 + (i + 1) * largura, y0 + altura], fill=cor)


def capa():
    w, h = 1584, 396
    im = Image.new("RGB", (w, h), LAVANDA)
    d = ImageDraw.Draw(im)
    # a foto do perfil cobre o canto inferior esquerdo, então o texto fica à direita
    titulo = ImageFont.truetype(PRETA, 74)
    sub = ImageFont.truetype(MEDIA, 30)
    margem = 80
    linhas = ["Pesquisa, dados", "e texto"]
    y = 70
    for linha in linhas:
        lw = d.textlength(linha, font=titulo)
        d.text((w - margem - lw, y), linha, font=titulo, fill=TINTA)
        y += 84
    texto = "Para times de dados, de pessoas e de comunicação"
    d.text((w - margem - d.textlength(texto, font=sub), y + 18), texto, font=sub, fill=TINTA)
    url = "eduardopagvieira.github.io"
    d.text((w - margem - d.textlength(url, font=sub), y + 62), url, font=sub, fill="#5b3fd6")
    faixas(d, 0, h - 18, w, 18)
    im.save(PASTA / "capa_linkedin.png")


def previa():
    w, h = 1200, 630
    im = Image.new("RGB", (w, h), LAVANDA)
    d = ImageDraw.Draw(im)
    nome = ImageFont.truetype(PRETA, 120)
    sub = ImageFont.truetype(MEDIA, 34)
    d.text((64, 70), "Eduardo", font=nome, fill=TINTA)
    d.text((64, 190), "Vieira", font=nome, fill=TINTA)
    linhas = ["Pesquisa, dados e texto para times", "de dados, de pessoas e de comunicação"]
    for i, linha in enumerate(linhas):
        d.text((64, 380 + i * 46), linha, font=sub, fill=TINTA)
    foto = Image.open(PASTA / "eduardo.png").convert("RGB").resize((300, 300))
    im.paste(foto, (w - 64 - 300, 80))
    faixas(d, 0, h - 24, w, 24)
    im.save(PASTA / "previa.png")


if __name__ == "__main__":
    capa()
    previa()
    print("ok")
