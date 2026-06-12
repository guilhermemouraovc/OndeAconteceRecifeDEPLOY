#!/usr/bin/env python3
"""Gera o relatório PDF do Ciclo 3 com evidências."""

from pathlib import Path
from datetime import date

OUT_DIR = Path(__file__).parent
PDF_PATH = OUT_DIR / "Relatorio-Ciclo3-OndeAconteceRecife.pdf"
HTML_PATH = OUT_DIR / "relatorio-ciclo3.html"

IMAGES = [
    ("01-moderacao-enviado-sem-flyer.png", "US20 — Cadastro manual enviado para moderação"),
    ("02-cadastro-flyer-preview.png", "US20 — Upload de flyer, preview e título sugerido pelo nome do arquivo"),
    ("03-moderacao-enviado-com-flyer.png", "US20 — Cadastro via flyer confirmado"),
    ("04-moderacao-fila-carregada.png", "US21 — Fila de moderação carregada com chave demo-moderador"),
    ("05-moderacao-detalhe-flyer.png", "US21 — Detalhe do evento pendente com preview do flyer"),
    ("06-moderacao-apos-acoes.png", "US21 — Aprovação e rejeição com motivo"),
    ("07-feed-evento-aprovado.png", "US23 — Evento aprovado visível no feed público"),
    ("08-chatbot-1.png", "US23 — Chatbot respondendo: eventos gratuitos"),
    ("08-chatbot-2.png", "US23 — Chatbot respondendo: o que tem em Boa Viagem?"),
    ("08-chatbot-3.png", "US23 — Chatbot respondendo: teatro no Recife"),
    ("09-swagger-endpoints.png", "API Ciclo 3 — endpoints documentados no Swagger"),
]

LINKS = [
    ("Feed público", "http://localhost:9300/"),
    ("Cadastro de eventos", "http://localhost:9300/cadastro"),
    ("Moderação", "http://localhost:9300/moderacao"),
    ("Swagger / Docs", "http://127.0.0.1:8010/docs"),
    ("API de eventos", "http://127.0.0.1:8010/events"),
    ("Repositório GitHub", "https://github.com/marinaghoffmann/OndeAconteceRecife"),
]

def img_tag(filename: str, caption: str) -> str:
    return f"""
    <figure class="evidence">
      <img src="{filename}" alt="{caption}" />
      <figcaption>{caption}</figcaption>
    </figure>
    """

def build_html() -> str:
    today = date.today().strftime("%d/%m/%Y")
    images_html = "\n".join(img_tag(f, c) for f, c in IMAGES)
    links_html = "\n".join(
        f'<li><a href="{url}">{label}</a> — <code>{url}</code></li>' for label, url in LINKS
    )

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <title>Relatório Ciclo 3 — Onde Acontece Recife</title>
  <style>
    @page {{ margin: 18mm 14mm; }}
    * {{ box-sizing: border-box; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      color: #0f172a;
      line-height: 1.55;
      margin: 0;
      padding: 24px;
      background: #fff;
    }}
    h1, h2, h3 {{ color: #0b3b4a; margin-top: 1.4em; }}
    h1 {{ font-size: 1.8rem; margin-top: 0; border-bottom: 3px solid #14b8a6; padding-bottom: 8px; }}
    h2 {{ font-size: 1.25rem; border-left: 4px solid #14b8a6; padding-left: 10px; }}
    .meta {{ color: #475569; margin-bottom: 24px; }}
    .epic {{
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 10px;
      padding: 14px 16px;
      margin: 12px 0 20px;
      page-break-inside: avoid;
    }}
    .epic h3 {{ margin-top: 0; color: #0f766e; }}
    ul {{ padding-left: 1.2rem; }}
    li {{ margin: 4px 0; }}
    code {{ background: #f1f5f9; padding: 2px 6px; border-radius: 4px; font-size: 0.9em; }}
    a {{ color: #0d9488; text-decoration: none; }}
    .evidence {{
      margin: 0 0 8px;
      page-break-before: always;
      page-break-inside: avoid;
      break-inside: avoid;
    }}
    .evidence:first-of-type {{
      page-break-before: auto;
    }}
    .evidence img {{
      display: block;
      width: 100%;
      max-height: 680px;
      object-fit: contain;
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      background: #f8fafc;
    }}
    .evidence figcaption {{
      margin-top: 8px;
      font-size: 0.92rem;
      color: #334155;
      font-weight: 600;
    }}
    .stack {{ margin-top: 28px; }}
    .footer {{
      margin-top: 36px;
      padding-top: 12px;
      border-top: 1px solid #e2e8f0;
      font-size: 0.85rem;
      color: #64748b;
    }}
  </style>
</head>
<body>
  <h1>Relatório Semanal — Ciclo 3</h1>
  <p class="meta">
    <strong>Projeto:</strong> Onde Acontece Recife<br />
    <strong>Instituição:</strong> CESAR School · 2026<br />
    <strong>Data do relatório:</strong> {today}<br />
    <strong>Versão da API:</strong> 0.5.0-ciclo3
  </p>

  <h2>Resumo da semana</h2>
  <p>
    Neste ciclo foram finalizadas <strong>3 histórias épicas em média fidelidade</strong>,
    com backend (FastAPI) e frontend (Vue 3 + Quasar) integrados. O foco foi permitir que
    produtores culturais cadastrem eventos, que moderadores aprovem ou rejeitem submissões
    antes da publicação, e que o público consulte a agenda aprovada por meio de um chatbot
    simples no feed.
  </p>

  <h2>Histórias épicas entregues</h2>

  <div class="epic">
    <h3>US20 — Cadastro de eventos por produtores</h3>
    <ul>
      <li>Tela <code>/cadastro</code> com formulário manual e upload opcional de flyer.</li>
      <li>Endpoint <code>POST /events</code> para cadastro manual.</li>
      <li>Endpoints <code>POST /events/flyer/preview</code> e <code>POST /events/flyer/submit</code>.</li>
      <li>Preview da imagem e sugestão de campos a partir do nome do arquivo.</li>
      <li>Eventos entram com status <code>pendente</code> e não aparecem no feed público.</li>
    </ul>
  </div>

  <div class="epic">
    <h3>US21 — Moderação de eventos</h3>
    <ul>
      <li>Tela <code>/moderacao</code> com autenticação por chave de moderador.</li>
      <li>Endpoints <code>GET /moderacao/pendentes</code>, <code>PATCH .../aprovar</code> e <code>PATCH .../rejeitar</code>.</li>
      <li>Listagem de pendentes, visualização de dados e preview do flyer.</li>
      <li>Aprovação publica o evento; rejeição remove da fila e impede exibição no feed.</li>
    </ul>
  </div>

  <div class="epic">
    <h3>US23 — Assistente de agenda (chatbot)</h3>
    <ul>
      <li>Botão flutuante no layout principal com painel lateral de chat.</li>
      <li>Endpoint <code>POST /chat</code> com busca em eventos aprovados.</li>
      <li>Respostas citam eventos com links <code>/evento/...</code>.</li>
      <li>Fallback quando nenhum evento aprovado corresponde à pergunta.</li>
    </ul>
  </div>

  <h2>Stack e arquivos principais</h2>
  <ul>
    <li><strong>Backend:</strong> <code>backend/main.py</code>, <code>backend/chat/</code></li>
    <li><strong>Frontend:</strong> <code>CadastroProdutorPage.vue</code>, <code>ModeracaoPage.vue</code>, <code>ChatbotPanel.vue</code></li>
    <li><strong>Composables:</strong> <code>useModerationApi.js</code>, <code>useChatbot.js</code></li>
  </ul>

  <h2>Links para visualização</h2>
  <ul>
    {links_html}
  </ul>
  <p><em>Obs.: links locais exigem backend e frontend em execução na máquina de desenvolvimento.</em></p>

  <h2>Evidências (prints)</h2>
  <div class="stack">
    {images_html}
  </div>

  <div class="footer">
    Relatório gerado automaticamente a partir dos testes US20 → US21 → US23.
    Evidências em <code>test-evidence/</code>.
  </div>
</body>
</html>
"""

def main():
    html = build_html()
    HTML_PATH.write_text(html, encoding="utf-8")
    print(f"HTML: {HTML_PATH}")

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright não disponível. Instale com: pip install playwright && playwright install chromium")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(HTML_PATH.as_uri(), wait_until="networkidle")
        page.pdf(
            path=str(PDF_PATH),
            format="A4",
            print_background=True,
            margin={"top": "14mm", "bottom": "14mm", "left": "12mm", "right": "12mm"},
        )
        browser.close()

    print(f"PDF: {PDF_PATH}")


if __name__ == "__main__":
    main()
