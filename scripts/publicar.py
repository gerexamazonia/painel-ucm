# Cifra os dados do painel com a chave pública do repositório.
# Só quem tem a senha do painel consegue decifrar (no navegador).
#
# Uso diário (após agg.py):
#   python3 scripts/publicar.py sga <pasta_com_os_4_sga_json> <pasta_do_repositorio>
# Uso eventual (metas/contratos do Cronograma):
#   python3 scripts/publicar.py lotes <lotes.json> <pasta_do_repositorio>
#
# Gera data/sga.enc.json (ou data/lotes.enc.json) e, no modo sga, data/controle.json
# (apenas totais gerais, sem dados por contrato). Sai com código 2 se o total de
# cadastros (A3) cair mais de 20% em relação à publicação anterior.
import base64, json, os, sys
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

modo, origem, repo = sys.argv[1], sys.argv[2], sys.argv[3]
pub = serialization.load_pem_public_key(open(os.path.join(repo, 'chave_publica.pem'), 'rb').read())
b64 = lambda x: base64.b64encode(x).decode()


def cifrar(obj, destino):
    k = AESGCM.generate_key(bit_length=256)
    iv = os.urandom(12)
    ct = AESGCM(k).encrypt(iv, json.dumps(obj, ensure_ascii=False).encode('utf-8'), None)
    wk = pub.encrypt(k, padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
    json.dump({'alg': 'RSA-OAEP-256+A256GCM', 'k': b64(wk), 'iv': b64(iv), 'ct': b64(ct)}, open(destino, 'w'))


os.makedirs(os.path.join(repo, 'data'), exist_ok=True)
if modo == 'lotes':
    cifrar(json.load(open(origem)), os.path.join(repo, 'data', 'lotes.enc.json'))
    print('ok lotes')
    sys.exit(0)
if modo == 'cronograma':
    c = json.load(open(origem))
    if len({l['contrato'] for l in c.get('linhas', [])}) < 16:
        print('ERRO: cronograma com menos de 16 contratos; nada publicado'); sys.exit(2)
    cifrar(c, os.path.join(repo, 'data', 'cronograma.enc.json'))
    print('ok cronograma')
    sys.exit(0)

nomes = ['sga_contrato', 'sga_municipio', 'sga_semana', 'sga_atualizacao']
dados = {n: json.load(open(os.path.join(origem, n + '.json'))) for n in nomes}
if not dados['sga_contrato']:
    print('ERRO: sga_contrato vazio; nada publicado'); sys.exit(2)
a3 = sum(r['qtd'] for r in dados['sga_contrato'] if r['atividade'] == 'A3')
ctl_path = os.path.join(repo, 'data', 'controle.json')
anterior = json.load(open(ctl_path)) if os.path.exists(ctl_path) else None
if anterior and anterior.get('a3_total') and a3 < 0.8 * anterior['a3_total']:
    print(f"ERRO: cadastros A3 caíram de {anterior['a3_total']} para {a3}; nada publicado"); sys.exit(2)
cifrar(dados, os.path.join(repo, 'data', 'sga.enc.json'))
u = dados['sga_atualizacao'][0]
json.dump({'processado_em': u['processado_em'], 'arquivo_sga_modificado_em': u['arquivo_sga_modificado_em'],
           'registros_lidos': u['registros_lidos'], 'a3_total': a3}, open(ctl_path, 'w'), ensure_ascii=False, indent=1)
print('ok sga', 'a3_total', a3, 'anterior', anterior and anterior.get('a3_total'))
