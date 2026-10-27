# Painel UcM · Acompanhamento da execução

Página estática (GitHub Pages) do Programa União com os Municípios (GEREX Amazônia/ANATER), protegida por senha.

Os dados ficam **cifrados** neste repositório; só quem tem a senha consegue vê-los no navegador.

- `index.html`: o painel (tela de senha + painel).
- `chave_publica.pem`: usada para cifrar os dados (não permite decifrar).
- `chave.json`: chave privada cifrada com a senha do painel (PBKDF2 + AES-GCM).
- `data/lotes.enc.json`: metas, valores e prazos por contrato (Cronograma UcM), cifrado.
- `data/sga.enc.json`: execução agregada do SGA, cifrada, atualizada nos dias úteis.
- `data/controle.json`: só totais gerais (data da atualização e total de cadastros), para conferência.
- `scripts/agg.py`: agrega a exportação CSV do SGA (sem dados pessoais).
- `scripts/publicar.py`: cifra os agregados com a chave pública.

Atualização: `python3 scripts/agg.py relatorio.csv out "<data>" && python3 scripts/publicar.py sga out .`

Trocar a senha não exige mudar a atualização diária: basta recifrar `chave.json`.

O CSV do SGA contém dados pessoais e **nunca** deve ser enviado a este repositório.
