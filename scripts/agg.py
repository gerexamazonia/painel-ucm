# Agrega o CSV do SGA (relatorio_atividades_por_projeto_47) em tabelas sem dados pessoais.
import csv, io, json, sys, collections, datetime as dt
src, outdir, fonte_mod = sys.argv[1], sys.argv[2], (sys.argv[3] if len(sys.argv) > 3 else '')
raw = open(src, 'rb').read()
try: txt = raw.decode('utf-8')
except UnicodeDecodeError: txt = raw.decode('latin-1')
rows = list(csv.DictReader(io.StringIO(txt)))
def ativ(desc):
    d = desc.lower()
    if 'entidades locais' in d: return 'A1'
    if 'mobiliza' in d: return 'A2'
    if 'cadastro e diagn' in d: return 'A3'
    if 'diagn' in d and 't0' in d: return 'T0'
    if 'plano de a' in d: return 'A4'
    if 'gov.br' in d: return 'A5'
    return 'OUTRA'
ST = {'3': 'Aprovada', '2': 'Devolvida para ajuste', '0': 'Reprovada', '': 'Aguardando análise', '1': 'Registrada'}
def iso(s):
    try: return dt.datetime.strptime(s.strip(), '%d/%m/%Y').date()
    except Exception: return None
by_ct = collections.Counter(); by_mun = collections.Counter(); by_wk = collections.Counter()
seen = set()
for r in rows:
    a = ativ(r.get('descricao', ''))
    st = ST.get((r.get('avaliacao') or '').strip(), 'Outro')
    c = (r.get('numero_contrato') or '').strip()
    key = (c, a, r.get('cod_identificador'), r.get('codigo_atividade'))
    if key in seen: continue
    seen.add(key)
    by_ct[(c, a, st)] += 1
    if a in ('A3', 'T0', 'A4') and r.get('municipio'):
        by_mun[(c, (r.get('uf') or '').strip(), r['municipio'].strip().title(), a, st)] += 1
    d = iso(r.get('data_execucao', ''))
    if d and a in ('A3', 'T0'):
        wk = d - dt.timedelta(days=d.weekday())
        by_wk[(wk.isoformat(), c, a)] += 1
def dump(name, data):
    json.dump(data, open(f'{outdir}/{name}.json', 'w'), ensure_ascii=False)
dump('sga_contrato', [{'chave': f'{c}|{a}|{s}', 'contrato': c, 'atividade': a, 'status': s, 'qtd': n} for (c, a, s), n in sorted(by_ct.items())])
dump('sga_municipio', [{'chave': f'{c}|{m}|{a}|{s}', 'contrato': c, 'uf': u, 'municipio': m, 'atividade': a, 'status': s, 'qtd': n} for (c, u, m, a, s), n in sorted(by_mun.items())])
dump('sga_semana', [{'chave': f'{w}|{c}|{a}', 'semana': w, 'contrato': c, 'atividade': a, 'qtd': n} for (w, c, a), n in sorted(by_wk.items())])
agora = dt.datetime.now(dt.timezone(dt.timedelta(hours=-3))).strftime('%Y-%m-%dT%H:%M:%S-03:00')
dump('sga_atualizacao', [{'item': 'atualizacao', 'arquivo_sga_modificado_em': fonte_mod, 'processado_em': agora, 'registros_lidos': len(rows), 'registros_unicos': len(seen)}])
print('ok', len(rows), len(seen), len(by_ct), len(by_mun), len(by_wk))
