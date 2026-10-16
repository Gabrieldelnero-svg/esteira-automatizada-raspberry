
import sqlite3

from flask import Flask, jsonify, render_template_string

import config

app = Flask(__name__)


def consultar(sql, args=()):
    try:
        con = sqlite3.connect(f"file:{config.DB_PATH}?mode=ro", uri=True, timeout=5)
        con.row_factory = sqlite3.Row
        try:
            return [dict(r) for r in con.execute(sql, args)]
        finally:
            con.close()
    except sqlite3.Error:
        return []  # banco ainda não existe ou está ocupado


@app.route("/api/resumo")
def resumo():
    total = {1: 0, 2: 0}
    hoje = {1: 0, 2: 0}
    for r in consultar("SELECT saida, COUNT(*) n FROM contagens GROUP BY saida"):
        total[r["saida"]] = r["n"]
    for r in consultar("SELECT saida, COUNT(*) n FROM contagens "
                       "WHERE date(ts) = date('now','localtime') GROUP BY saida"):
        hoje[r["saida"]] = r["n"]
    return jsonify(
        total=total, hoje=hoje,
        por_produto=consultar("SELECT produto, COUNT(*) n FROM leituras GROUP BY produto ORDER BY n DESC"),
        leituras=consultar("SELECT ts, qr, cor, produto, saida_prevista FROM leituras ORDER BY id DESC LIMIT 10"),
        contagens=consultar("SELECT ts, saida FROM contagens ORDER BY id DESC LIMIT 10"),
    )


PAGINA = """<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Dashboard da Esteira</title>
<style>
body{font-family:Calibri,Arial,sans-serif;margin:0;background:#f3f6fa;color:#1f2937}
header{background:#1f2937;color:#fff;padding:16px 24px;font-size:22px;font-weight:bold}
main{padding:20px 24px;max-width:1100px;margin:auto}
.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.card{background:#fff;border:1px solid #cbd5e1;border-radius:10px;padding:16px}
.card h3{margin:0 0 6px;font-size:15px;color:#6b7280}.num{font-size:48px;font-weight:bold}
.s1 .num{color:#2a9d4f}.s2 .num{color:#1d6fd6}.small{font-size:13px;color:#6b7280}
h2{font-size:18px;margin:24px 0 8px}
table{width:100%;border-collapse:collapse;background:#fff;border:1px solid #cbd5e1;border-radius:10px}
th,td{padding:8px 10px;text-align:left;border-bottom:1px solid #e5e7eb;font-size:14px}
th{background:#1f2937;color:#fff}.grid2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.bar{background:#e5e7eb;border-radius:6px;height:14px}.bar>div{background:#2a9d4f;height:14px;border-radius:6px}
@media(max-width:700px){.cards,.grid2{grid-template-columns:1fr}}
</style></head><body>
<header>Esteira automatizada — Dashboard</header>
<main>
<div class="cards">
 <div class="card s1"><h3>Saída 1 (reta)</h3><div class="num" id="t1">0</div><div class="small">hoje: <span id="h1">0</span></div></div>
 <div class="card s2"><h3>Saída 2 (lateral)</h3><div class="num" id="t2">0</div><div class="small">hoje: <span id="h2">0</span></div></div>
 <div class="card"><h3>Total de caixas contadas</h3><div class="num" id="tt">0</div><div class="small">atualiza a cada 2 s</div></div>
</div>
<h2>Caixas por produto (identificadas pela câmera)</h2>
<div class="card" id="produtos"></div>
<div class="grid2">
 <div><h2>Últimas identificações</h2><table><thead><tr><th>Hora</th><th>Produto</th><th>Cor</th><th>Saída prevista</th></tr></thead><tbody id="leituras"></tbody></table></div>
 <div><h2>Últimas contagens (barreira óptica)</h2><table><thead><tr><th>Hora</th><th>Saída</th></tr></thead><tbody id="contagens"></tbody></table></div>
</div>
</main>
<script>
function linha(tb, cols){const tr=document.createElement('tr');cols.forEach(c=>{const td=document.createElement('td');td.textContent=c;tr.appendChild(td)});tb.appendChild(tr)}
async function atualizar(){
 try{
  const d=await (await fetch('/api/resumo')).json();
  document.getElementById('t1').textContent=d.total[1];document.getElementById('t2').textContent=d.total[2];
  document.getElementById('h1').textContent=d.hoje[1];document.getElementById('h2').textContent=d.hoje[2];
  document.getElementById('tt').textContent=d.total[1]+d.total[2];
  const p=document.getElementById('produtos');p.textContent='';
  const max=Math.max(1,...d.por_produto.map(x=>x.n));
  if(!d.por_produto.length){p.textContent='Nenhuma identificação ainda.'}
  d.por_produto.forEach(x=>{const r=document.createElement('div');r.style.margin='6px 0';
   const t=document.createElement('div');t.textContent=x.produto+' — '+x.n;
   const b=document.createElement('div');b.className='bar';const i=document.createElement('div');i.style.width=(100*x.n/max)+'%';b.appendChild(i);
   r.appendChild(t);r.appendChild(b);p.appendChild(r)});
  const L=document.getElementById('leituras');L.textContent='';d.leituras.forEach(x=>linha(L,[x.ts.slice(11),x.produto,x.cor,x.saida_prevista]));
  const C=document.getElementById('contagens');C.textContent='';d.contagens.forEach(x=>linha(C,[x.ts.slice(11),'Saída '+x.saida]));
 }catch(e){}
}
atualizar();setInterval(atualizar,2000);
</script></body></html>"""


@app.route("/")
def index():
    return render_template_string(PAGINA)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
