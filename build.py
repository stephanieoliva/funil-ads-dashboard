#!/usr/bin/env python3
"""
Gera o index.html do Funil ADS Dashboard a partir de um CSV baixado do Drive.

Uso:
  python3 scripts/build.py <caminho_csv_bruto> [--tz-offset -3]

Espera que o CSV bruto (baixado via mcp__Google_Drive__download_file_content,
exportMimeType=text/csv, fileId=1AImQDaQ6dmJ5W2fX6Y1gVx0sqis8XLJ_MviizWwCFD8)
já exista em disco. Escreve index.html na raiz do repo.
"""
import csv
import sys
import base64
import os
from datetime import datetime, timezone, timedelta

KEEP = [
    'data lead', 'origem do lead', 'semana lead', 'mês lead',
    'data cadastro', 'semana cadastro', 'mês cadastro',
    'data ativação vendido', 'semana ativação vendido', 'mês ativação vendido',
    'data ativação entregue', 'semana ativação entregue', 'mês ativação entregue',
    'vendedor ativação', 'SDR',
]

def main():
    if len(sys.argv) < 2:
        print("uso: build.py <csv_bruto>", file=sys.stderr)
        sys.exit(1)
    csv_path = sys.argv[1]

    repo_root = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(repo_root, 'index_template.html')
    out_path = os.path.join(repo_root, 'index.html')

    rows = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append([r.get(k, '') for k in KEEP])

    from io import StringIO
    buf = StringIO()
    w = csv.writer(buf)
    w.writerow(KEEP)
    w.writerows(rows)
    trimmed_csv = buf.getvalue()
    csv_b64 = base64.b64encode(trimmed_csv.encode('utf-8')).decode('ascii')

    # Horário de Fortaleza (UTC-3), fixo (não usa DST no Brasil atualmente)
    tz = timezone(timedelta(hours=-3))
    now = datetime.now(tz)
    build_time = now.strftime('%d/%m/%Y %H:%M') + ' (horário de Fortaleza)'

    with open(template_path, encoding='utf-8') as f:
        template = f.read()

    out = template.replace('__CSV_B64__', csv_b64).replace('__BUILD_TIME__', build_time)

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(out)

    print(f"OK: {len(rows)} linhas, index.html gerado ({os.path.getsize(out_path)} bytes), build_time={build_time}")

if __name__ == '__main__':
    main()
