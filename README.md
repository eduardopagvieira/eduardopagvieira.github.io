# Site pessoal de Eduardo Vieira

Site estático em HTML, sem dependências, com duas páginas.

- `index.html` apresenta o que posso fazer por uma equipe, os projetos de dados abertos, a pesquisa e as publicações.
- `painel.html` é um painel interativo com os três projetos (Consumidor.gov.br, BNDES e Lei Rouanet). Cada aba tem filtros, indicadores e gráficos que respondem a uma pergunta de negócio.

O painel lê `dados/painel.js`, um arquivo pequeno com tabelas já agregadas. Ele é gerado por `gerar_dados.py`, que lê as bases tratadas nas pastas vizinhas do portfólio (rouanet, consumidor e bndes). Para atualizar os números, rode os projetos e depois

```
python gerar_dados.py
```

Para ver no computador, rode `python -m http.server` nesta pasta e abra http://localhost:8000.

Para publicar no GitHub Pages, este repositório deve se chamar `eduardopagvieira.github.io`. O site passa a responder nesse endereço. Pages em repositório privado exige plano pago, então o repositório fica público quando o site for ao ar.

Antes de publicar, falta tornar públicos este repositório e os repositórios rouanet, consumidor e bndes, para o site ir ao ar e os links de código funcionarem.
