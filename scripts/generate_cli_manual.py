"""Generate the practical yt-dlp and Demucs CLI manual as a DOCX file."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile

from generate_public_manual import (
    ASSETS,
    CONTENT_TYPES,
    NUMBERING,
    ROOT_RELS,
    STYLES,
    bullet,
    callout,
    h,
    image,
    p,
    page_break,
    table,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "AudioLabEditor_Manual_PowerShell_WinGet.docx"


def code(command: str) -> str:
    """Render a copy-friendly command block."""
    paragraphs = []
    for line in command.splitlines() or [""]:
        paragraphs.append(
            '<w:p><w:pPr><w:spacing w:before="0" w:after="0" w:line="240" w:lineRule="auto"/></w:pPr>'
            '<w:r><w:rPr><w:rFonts w:ascii="Cascadia Mono" w:hAnsi="Cascadia Mono"/>'
            '<w:color w:val="EAF2FB"/><w:sz w:val="18"/><w:noProof/></w:rPr>'
            f'<w:t xml:space="preserve">{escape(line)}</w:t></w:r></w:p>'
        )
    return (
        '<w:tbl><w:tblPr><w:tblW w:w="9000" w:type="dxa"/><w:tblCellMar>'
        '<w:top w:w="150" w:type="dxa"/><w:left w:w="180" w:type="dxa"/>'
        '<w:bottom w:w="150" w:type="dxa"/><w:right w:w="180" w:type="dxa"/>'
        '</w:tblCellMar></w:tblPr><w:tr><w:trPr><w:cantSplit/></w:trPr><w:tc>'
        '<w:tcPr><w:shd w:fill="091321"/><w:tcW w:w="9000" w:type="dxa"/></w:tcPr>'
        + "".join(paragraphs)
        + "</w:tc></w:tr></w:tbl>"
        + p()
    )


def command(title: str, value: str, *, level: int = 3) -> list[str]:
    return [h(title, level=level), code(value)]


def build_document() -> str:
    body: list[str] = [
        p("MANUAL PRÁTICO DE CLI", style="Title"),
        p("yt-dlp e Demucs", style="ProductTitle"),
        p("Captura responsável, preparação de áudio e separação de stems", style="Subtitle"),
        image("logo", "rId3", width_inches=1.65),
        p("Comandos diretos para PowerShell — sem variáveis de projeto", style="CoverNote", center=True),
        p("Revisão 2026.06 • AudioLab Editor", center=True, italic=True, color="5B6573"),
        page_break(),
        h("Objetivo e limites deste manual"),
        p(
            "Este guia reúne comandos úteis para pessoas que desejam compreender e demonstrar fluxos de captura "
            "de mídia e separação de fontes sonoras. Os exemplos usam caminhos explícitos e podem ser executados "
            "em qualquer pasta existente."
        ),
        callout(
            "Importante:",
            "RLLabs é apenas o nome da pasta usada em uma demonstração. Não é requisito, configuração padrão "
            "nem estrutura obrigatória. Substitua os caminhos pelos locais existentes no seu computador.",
            kind="info",
        ),
        callout(
            "Uso responsável:",
            "trabalhe somente com conteúdo próprio, autorizado, licenciado ou permitido pela origem. Este manual "
            "não ensina a contornar DRM, autenticação, bloqueios regionais ou restrições de acesso e não substitui "
            "orientação jurídica sobre direitos autorais ou termos de serviço.",
            kind="warning",
        ),
        h("O que estas técnicas não substituem", level=2),
        p(
            "Aprender yt-dlp, FFmpeg e Demucs amplia autonomia, diagnóstico e capacidade de automação. Isso não "
            "substitui plataformas gerenciadas, como Moises, nem seus aplicativos, serviços em nuvem, experiência "
            "integrada, modelos próprios, suporte, armazenamento ou recursos oferecidos em cada plano."
        ),
        p(
            "Use as duas abordagens de forma complementar: CLI para estudo, controle local, repetibilidade e "
            "integrações; plataformas gerenciadas quando conveniência, fluxo pronto ou recursos específicos forem "
            "mais importantes. Consulte sempre os recursos, preços, limites e termos atuais da plataforma escolhida."
        ),
        h("1. Preparação segura"),
        table(
            ["Componente", "Função", "Verificação"],
            [
                ["PowerShell", "Executar os comandos no Windows", "$PSVersionTable.PSVersion"],
                ["yt-dlp", "Analisar e capturar mídia compatível", "yt-dlp --version"],
                ["FFmpeg", "Mesclar, cortar e converter mídia", "ffmpeg -version"],
                ["ffprobe", "Inspecionar arquivos", "ffprobe -version"],
                ["Demucs CLI", "Separar vocais e instrumentos", "demucs --help"],
            ],
            [1900, 3800, 3300],
        ),
        h("Instalar yt-dlp e FFmpeg com WinGet", level=2),
        code(
            "winget search yt-dlp\n"
            "winget show --id yt-dlp.yt-dlp --exact\n"
            "winget install --id yt-dlp.yt-dlp --exact --source winget\n\n"
            "winget search ffmpeg\n"
            "winget show --id Gyan.FFmpeg --exact\n"
            "winget install --id Gyan.FFmpeg --exact --source winget"
        ),
        p("Feche e reabra o PowerShell depois da instalação para atualizar o PATH."),
        *command(
            "Verificar todos os comandos",
            "Get-Command yt-dlp,ffmpeg,ffprobe,demucs -ErrorAction SilentlyContinue\n"
            "yt-dlp --version\nffmpeg -version\ndemucs --help",
            level=2,
        ),
        callout(
            "Demucs como CLI:",
            "os exemplos usam somente o comando global demucs. O programa ainda depende internamente de um runtime "
            "e de bibliotecas de IA; essa complexidade apenas não aparece no comando diário.",
            kind="info",
        ),
        h("Escolher uma pasta", level=2),
        p("Use uma destas formas. Nenhum comando cria um projeto obrigatório:"),
        code(
            'Set-Location "C:\\Users\\SeuUsuario\\Desktop\\RLLabs"\n'
            'Set-Location "$HOME\\Downloads"\n'
            'Set-Location "D:\\Midia"'
        ),
        page_break(),
        h("2. yt-dlp — captura de mídia"),
        p(
            "yt-dlp é um downloader de linha de comando. FFmpeg é necessário para mesclar vídeo e áudio, extrair "
            "formatos de áudio e processar capítulos ou intervalos. Sites podem mudar sem aviso; mantenha a ferramenta "
            "atualizada e confirme o resultado antes de iniciar fluxos longos."
        ),
        h("2.1 Analisar antes de baixar", level=2),
        *command("Exibir título, duração e canal", 'yt-dlp --print "Título: %(title)s" --print "Duração: %(duration_string)s" --print "Canal: %(uploader)s" "COLE_A_URL_AQUI"'),
        *command("Listar formatos disponíveis", 'yt-dlp --list-formats "COLE_A_URL_AQUI"'),
        *command("Atualizar o executável oficial", "yt-dlp -U"),
        *command(
            "Listar capítulos",
            'yt-dlp --dump-single-json --skip-download "COLE_A_URL_AQUI" | ConvertFrom-Json | Select-Object -ExpandProperty chapters | Format-Table start_time,end_time,title -AutoSize',
        ),
        h("2.2 Vídeo completo", level=2),
        *command(
            "Melhor vídeo com áudio",
            'yt-dlp --no-playlist -f "bv*+ba/b" --merge-output-format mp4 -o "%(title).180s.%(ext)s" "COLE_A_URL_AQUI"',
        ),
        *command(
            "Somente vídeo, sem áudio",
            'yt-dlp --no-playlist -f "bv*[ext=mp4]/bv*" -o "%(title).180s-video.%(ext)s" "COLE_A_URL_AQUI"',
        ),
        h("2.3 Áudio completo", level=2),
        *command("MP3", 'yt-dlp --no-playlist -x --audio-format mp3 --audio-quality 0 -o "%(title).180s.%(ext)s" "COLE_A_URL_AQUI"'),
        *command("WAV", 'yt-dlp --no-playlist -x --audio-format wav -o "%(title).180s.%(ext)s" "COLE_A_URL_AQUI"'),
        *command("FLAC", 'yt-dlp --no-playlist -x --audio-format flac -o "%(title).180s.%(ext)s" "COLE_A_URL_AQUI"'),
        *command("M4A", 'yt-dlp --no-playlist -x --audio-format m4a -o "%(title).180s.%(ext)s" "COLE_A_URL_AQUI"'),
        *command("Opus", 'yt-dlp --no-playlist -x --audio-format opus -o "%(title).180s.%(ext)s" "COLE_A_URL_AQUI"'),
        callout(
            "Escolha prática:",
            "WAV ou FLAC para edição e Demucs; MP3, M4A ou Opus para escuta e compartilhamento. Converter um arquivo "
            "com perdas para WAV não recupera qualidade perdida.",
            kind="tip",
        ),
        h("2.4 Capítulos", level=2),
        *command(
            "Vídeo com áudio por título do capítulo",
            'yt-dlp --download-sections "*NOME EXATO DO CAPÍTULO" --force-keyframes-at-cuts -f "bv*+ba/b" --merge-output-format mp4 -o "capitulo.%(ext)s" "COLE_A_URL_AQUI"',
        ),
        *command(
            "Capítulo como FLAC",
            'yt-dlp --download-sections "*NOME EXATO DO CAPÍTULO" --force-keyframes-at-cuts -x --audio-format flac -o "capitulo.%(ext)s" "COLE_A_URL_AQUI"',
        ),
        *command(
            "Dividir todos os capítulos",
            'yt-dlp --split-chapters -f "bv*+ba/b" --merge-output-format mp4 -o "chapter:%(title).120s - %(section_title).100s.%(ext)s" "COLE_A_URL_AQUI"',
        ),
        h("2.5 Intervalo de tempo", level=2),
        *command(
            "Vídeo com áudio entre 05:10 e 08:25",
            'yt-dlp --download-sections "*00:05:10-00:08:25" --force-keyframes-at-cuts -f "bv*+ba/b" --merge-output-format mp4 -o "trecho.%(ext)s" "COLE_A_URL_AQUI"',
        ),
        *command(
            "Intervalo como WAV",
            'yt-dlp --download-sections "*00:05:10-00:08:25" --force-keyframes-at-cuts -x --audio-format wav -o "trecho.%(ext)s" "COLE_A_URL_AQUI"',
        ),
        h("2.6 Pasta de saída", level=2),
        *command("Salvar em qualquer pasta existente", 'yt-dlp -P "D:\\Midia" -x --audio-format flac "COLE_A_URL_AQUI"'),
        page_break(),
        h("3. Cuidados importantes com yt-dlp"),
        bullet("Confirme autoria, licença, autorização e termos da plataforma antes de baixar."),
        bullet("Use --no-playlist quando a intenção for baixar apenas um item."),
        bullet("Não compartilhe cookies, tokens, URLs privadas ou logs que contenham dados de sessão."),
        bullet("Não use opções inseguras, scripts desconhecidos ou executáveis de fontes não verificadas."),
        bullet("Evite repetição agressiva após erros 403 ou 429; aguarde e verifique a causa."),
        bullet("Confira espaço em disco antes de baixar vídeo de alta resolução ou converter para WAV."),
        bullet("Preserve o arquivo original e gere saídas com nomes diferentes."),
        bullet("Uma URL com marca de tempo não garante recorte; use --download-sections explicitamente."),
        h("3.1 Tratamento de erros do yt-dlp", level=2),
        table(
            ["Mensagem ou sintoma", "Ação útil"],
            [
                ["yt-dlp não reconhecido", "Confirme a instalação e reabra o PowerShell para atualizar o PATH."],
                ["ffmpeg não encontrado", "Instale o binário FFmpeg, reabra o terminal e execute ffmpeg -version."],
                ["URL inválida ou vídeo indisponível", "Copie novamente a URL e confirme no navegador se o conteúdo continua acessível."],
                ["HTTP 403 ou 429", "Atualize yt-dlp, reduza tentativas e aguarde. Não tente contornar controles de acesso."],
                ["Requested format is not available", "Execute --list-formats e escolha um formato realmente listado."],
                ["Capítulo não encontrado", "Liste os capítulos e copie o título exato; se não houver capítulos, use um intervalo."],
                ["Falha ao mesclar ou converter", "Confirme FFmpeg, espaço livre, permissões e integridade dos arquivos temporários."],
                ["Download interrompido", "Preserve os arquivos parciais, estabilize a conexão e tente novamente sem sobrescrever o original."],
                ["Caminho ou nome inválido", "Use aspas em caminhos com espaços e escolha uma pasta existente com permissão de escrita."],
            ],
            [3000, 6000],
        ),
        *command("Coletar diagnóstico", 'yt-dlp --verbose "COLE_A_URL_AQUI"'),
        callout(
            "Privacidade do diagnóstico:",
            "revise o log antes de enviá-lo a terceiros. Remova cookies, tokens, identificadores pessoais e URLs privadas.",
            kind="warning",
        ),
        page_break(),
        h("4. Demucs CLI — separação de stems"),
        p(
            "Demucs estima fontes sonoras a partir de uma mixagem pronta. O resultado não equivale às gravações "
            "multitrack originais: vazamentos, reverberação compartilhada e artefatos podem permanecer."
        ),
        h("4.1 Quantidade de stems", level=2),
        table(
            ["Modo", "Saídas", "Uso"],
            [
                ["2 stems", "Fonte escolhida + restante", "Karaokê, estudo ou isolamento rápido."],
                ["4 stems", "vocals, drums, bass, other", "Uso geral e melhor equilíbrio de qualidade."],
                ["6 stems", "4 stems + guitar + piano", "Análise adicional; modelo experimental."],
            ],
            [1700, 3600, 3700],
        ),
        callout(
            "Limite atual:",
            "o modelo oficial de seis fontes adiciona guitarra e piano. Piano pode apresentar mais vazamento e "
            "artefatos. Não há uma opção simples para criar stems confiáveis de saxofone, metais ou cordas; isso "
            "exige outros modelos, treinamento especializado ou plataformas que ofereçam esses recursos.",
            kind="warning",
        ),
        h("4.2 Comandos de separação", level=2),
        *command("Vocais e acompanhamento", 'demucs --two-stems vocals -o ".\\stems" ".\\musica.flac"'),
        *command("Bateria e acompanhamento", 'demucs --two-stems drums -o ".\\stems" ".\\musica.wav"'),
        *command("Baixo e acompanhamento", 'demucs --two-stems bass -o ".\\stems" ".\\musica.wav"'),
        *command("Quatro stems", 'demucs -n htdemucs -o ".\\stems" ".\\musica.flac"'),
        *command("Seis stems", 'demucs -n htdemucs_6s -o ".\\stems" ".\\musica.flac"'),
        *command("Guitarra e acompanhamento", 'demucs -n htdemucs_6s --two-stems guitar -o ".\\stems" ".\\musica.wav"'),
        *command("Piano e acompanhamento", 'demucs -n htdemucs_6s --two-stems piano -o ".\\stems" ".\\musica.wav"'),
        p(
            "O modo --two-stems ainda executa a separação completa internamente e combina as demais fontes. Portanto, "
            "não é necessariamente mais rápido nem usa menos memória."
        ),
        h("4.3 Formatos de entrada", level=2),
        p(
            "Com FFmpeg disponível, o Demucs pode receber WAV, FLAC, MP3, M4A, AAC, OGG/Vorbis, Opus, AIFF e "
            "outros formatos decodificáveis. Para trabalho de edição, prefira WAV ou FLAC."
        ),
        *command("Entrada M4A", 'demucs -n htdemucs -o ".\\stems" ".\\musica.m4a"'),
        *command("Processar vários arquivos", 'demucs -n htdemucs -o ".\\stems" ".\\faixa-01.flac" ".\\faixa-02.wav"'),
        h("4.4 Formatos de saída nativos", level=2),
        *command("WAV 16-bit — padrão", 'demucs -n htdemucs -o ".\\stems" ".\\musica.flac"'),
        *command("WAV 24-bit", 'demucs -n htdemucs --int24 -o ".\\stems" ".\\musica.flac"'),
        *command("WAV float32", 'demucs -n htdemucs --float32 -o ".\\stems" ".\\musica.flac"'),
        *command("FLAC", 'demucs -n htdemucs --flac -o ".\\stems" ".\\musica.wav"'),
        *command("MP3 320 kbps", 'demucs -n htdemucs --mp3 --mp3-bitrate 320 -o ".\\stems" ".\\musica.wav"'),
        callout(
            "Formatos nativos:",
            "o CLI entrega WAV, FLAC ou MP3. Para OGG, Opus, AAC ou M4A, gere WAV/FLAC primeiro e converta uma "
            "cópia com FFmpeg.",
            kind="info",
        ),
        h("4.5 Converter uma stem", level=2),
        *command("OGG/Vorbis", 'ffmpeg -i ".\\stems\\htdemucs\\musica\\vocals.wav" -c:a libvorbis -q:a 6 ".\\vocals.ogg"'),
        *command("Opus", 'ffmpeg -i ".\\stems\\htdemucs\\musica\\vocals.wav" -c:a libopus -b:a 192k ".\\vocals.opus"'),
        *command("AAC", 'ffmpeg -i ".\\stems\\htdemucs\\musica\\vocals.wav" -c:a aac -b:a 256k ".\\vocals.aac"'),
        *command("M4A", 'ffmpeg -i ".\\stems\\htdemucs\\musica\\vocals.wav" -c:a aac -b:a 256k ".\\vocals.m4a"'),
        h("4.6 Qualidade e desempenho", level=2),
        *command("Modelo refinado — melhor qualidade, mais lento", 'demucs -n htdemucs_ft -o ".\\stems" ".\\musica.flac"'),
        *command("Forçar CPU", 'demucs -n htdemucs -d cpu -o ".\\stems" ".\\musica.flac"'),
        *command("Reduzir memória por segmento", 'demucs -n htdemucs --segment 7 -o ".\\stems" ".\\musica.flac"'),
        *command("Mais estabilização — mais lento", 'demucs -n htdemucs --shifts 5 -o ".\\stems" ".\\musica.flac"'),
        page_break(),
        h("5. Cuidados importantes com Demucs"),
        bullet("Preserve o áudio original; grave stems em uma pasta diferente."),
        bullet("Não descreva as stems como faixas originais de estúdio. Elas são estimativas geradas por IA."),
        bullet("Escute todas as saídas antes de publicar, remixar, transcrever ou usar em apresentação."),
        bullet("Use WAV 24-bit ou FLAC para edição; evite recomprimir repetidamente em formatos com perdas."),
        bullet("Confirme espaço em disco: seis WAVs podem ocupar várias vezes o tamanho da entrada."),
        bullet("A primeira execução pode baixar modelos; use rede confiável e não interrompa o processo."),
        bullet("GPU acelera o trabalho, mas pode esgotar memória. CPU é mais lenta e geralmente mais previsível."),
        bullet("Respeite direitos autorais, consentimento e privacidade do material processado."),
        h("5.1 Tratamento de erros do Demucs", level=2),
        table(
            ["Mensagem ou sintoma", "Ação útil"],
            [
                ["demucs não reconhecido", "Confirme que o CLI está instalado no PATH e reabra o PowerShell."],
                ["Modelo não baixa", "Confirme internet, espaço, proxy e permissões. Tente novamente sem apagar arquivos válidos."],
                ["CUDA out of memory", "Use -d cpu ou --segment 7. Feche aplicações que ocupam a GPU."],
                ["Processamento muito lento", "Use htdemucs padrão, reduza shifts, processe um trecho ou use hardware mais adequado."],
                ["Formato não abre", "Valide com ffprobe e converta para WAV ou FLAC com FFmpeg."],
                ["Stem com vazamento", "Teste outro modelo, use fonte de melhor qualidade e trate o resultado como estimativa."],
                ["Som distorcido ou clipping", "Teste --clip-mode clamp ou reduza o volume da entrada antes da separação."],
                ["Arquivo incompleto", "Não use a saída; confirme espaço, energia e erro final antes de repetir."],
                ["Sem espaço em disco", "Interrompa com segurança, libere espaço e use FLAC quando apropriado."],
            ],
            [3000, 6000],
        ),
        h("6. Fluxos completos"),
        h("6.1 Áudio completo até quatro stems", level=2),
        code(
            'yt-dlp --no-playlist -x --audio-format flac -o "musica.%(ext)s" "COLE_A_URL_AQUI"\n'
            'demucs -n htdemucs --flac -o ".\\stems" ".\\musica.flac"'
        ),
        h("6.2 Capítulo até seis stems", level=2),
        code(
            'yt-dlp --download-sections "*NOME EXATO DO CAPÍTULO" --force-keyframes-at-cuts -x --audio-format wav -o "capitulo.%(ext)s" "COLE_A_URL_AQUI"\n'
            'demucs -n htdemucs_6s --int24 -o ".\\stems-capitulo" ".\\capitulo.wav"'
        ),
        h("6.3 Intervalo até vocais e acompanhamento", level=2),
        code(
            'yt-dlp --download-sections "*00:05:10-00:08:25" --force-keyframes-at-cuts -x --audio-format wav -o "trecho.%(ext)s" "COLE_A_URL_AQUI"\n'
            'demucs --two-stems vocals --flac -o ".\\stems-trecho" ".\\trecho.wav"'
        ),
        callout(
            "Antes de encadear:",
            "confirme que o primeiro arquivo existe, abre normalmente e tem duração esperada. Não continue um pipeline "
            "quando a etapa anterior terminou com erro.",
            kind="critical",
        ),
        h("7. Checklist antes e depois"),
        table(
            ["Antes", "Depois"],
            [
                ["Confirmar autorização e finalidade", "Abrir e escutar os arquivos gerados"],
                ["Validar URL ou arquivo de entrada", "Verificar duração, formato e tamanho"],
                ["Escolher pasta existente e gravável", "Preservar original e logs úteis"],
                ["Conferir espaço, rede e energia", "Remover temporários somente após validar"],
                ["Testar versões e comandos", "Documentar comando, modelo e opções usados"],
            ],
            [4500, 4500],
        ),
        h("8. Referências oficiais"),
        bullet("yt-dlp: https://github.com/yt-dlp/yt-dlp"),
        bullet("FFmpeg: https://ffmpeg.org/documentation.html"),
        bullet("Demucs: https://github.com/facebookresearch/demucs"),
        bullet("Fork de manutenção do Demucs: https://github.com/adefossez/demucs"),
        bullet("Moises: https://moises.ai/"),
        callout(
            "Última orientação:",
            "comece com um arquivo curto, valide o resultado e só então processe materiais longos. A ferramenta mais "
            "adequada é a que atende ao objetivo com qualidade, segurança e esforço aceitáveis.",
            kind="tip",
        ),
    ]

    section = (
        '<w:sectPr><w:footerReference w:type="default" r:id="rId9"/>'
        '<w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1134" w:right="1134" w:bottom="1134" '
        'w:left="1134" w:header="568" w:footer="568" w:gutter="0"/></w:sectPr>'
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f"<w:body>{''.join(body)}{section}</w:body></w:document>"
    )


FOOTER = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:p><w:pPr><w:jc w:val="center"/></w:pPr><w:r><w:rPr><w:color w:val="7F8C8D"/><w:sz w:val="18"/></w:rPr><w:t>AudioLab Editor — Manual Prático de CLI  •  </w:t></w:r><w:fldSimple w:instr="PAGE"><w:r><w:rPr><w:color w:val="7F8C8D"/><w:sz w:val="18"/></w:rPr><w:t>1</w:t></w:r></w:fldSimple></w:p></w:ftr>"""


def main() -> None:
    logo = ASSETS["logo"]
    if not logo.exists():
        raise FileNotFoundError(logo)

    relationships = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/logo.png"/>
  <Relationship Id="rId9" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/>
</Relationships>"""

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    core = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dc:title>AudioLab Editor — Manual Prático de yt-dlp e Demucs</dc:title><dc:subject>Uso responsável de CLI para captura e separação de stems</dc:subject><dc:creator>AudioLab Editor</dc:creator><cp:keywords>AudioLab Editor; yt-dlp; Demucs; FFmpeg; CLI; stems</cp:keywords><dc:description>Comandos diretos, cuidados, erros e fluxos úteis.</dc:description><dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created><dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified></cp:coreProperties>"""
    app = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"><Application>AudioLab Editor</Application><AppVersion>1.0</AppVersion></Properties>"""

    with ZipFile(OUTPUT, "w", ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", CONTENT_TYPES)
        archive.writestr("_rels/.rels", ROOT_RELS)
        archive.writestr("docProps/core.xml", core)
        archive.writestr("docProps/app.xml", app)
        archive.writestr("word/document.xml", build_document())
        archive.writestr("word/styles.xml", STYLES)
        archive.writestr("word/numbering.xml", NUMBERING)
        archive.writestr("word/footer1.xml", FOOTER)
        archive.writestr("word/_rels/document.xml.rels", relationships)
        archive.write(logo, "word/media/logo.png")
    print(OUTPUT)


if __name__ == "__main__":
    main()
