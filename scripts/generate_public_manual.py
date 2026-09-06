"""Generate the public AudioLab Editor user manual as a dependency-free DOCX."""

from __future__ import annotations

import struct
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "AudioLabEditor_Manual_Publico_Atualizado.docx"
ASSETS = {
    "logo": ROOT / "src/presentation/assets/logo.png",
    "main": ROOT / "docs/screenshots/main_window.png",
    "capture": ROOT / "docs/screenshots/tab_capture.png",
    "trim": ROOT / "docs/screenshots/tab_trim.png",
    "video": ROOT / "docs/screenshots/tab_video.png",
    "stems": ROOT / "docs/screenshots/tab_stems.png",
}


def png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()[:24]
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"Imagem PNG inválida: {path}")
    return struct.unpack(">II", data[16:24])


def run(text: str, *, bold: bool = False, italic: bool = False, color: str | None = None) -> str:
    props = []
    if bold:
        props.append("<w:b/>")
    if italic:
        props.append("<w:i/>")
    if color:
        props.append(f'<w:color w:val="{color}"/>')
    rpr = f"<w:rPr>{''.join(props)}</w:rPr>" if props else ""
    return f'<w:r>{rpr}<w:t xml:space="preserve">{escape(text)}</w:t></w:r>'


def p(
    text: str = "",
    *,
    style: str | None = None,
    bold: bool = False,
    italic: bool = False,
    color: str | None = None,
    bullet: bool = False,
    keep_next: bool = False,
    center: bool = False,
) -> str:
    props = []
    if style:
        props.append(f'<w:pStyle w:val="{style}"/>')
    if bullet:
        props.append('<w:numPr><w:ilvl w:val="0"/><w:numId w:val="1"/></w:numPr>')
    if keep_next:
        props.append("<w:keepNext/>")
    if center:
        props.append('<w:jc w:val="center"/>')
    ppr = f"<w:pPr>{''.join(props)}</w:pPr>" if props else ""
    return f"<w:p>{ppr}{run(text, bold=bold, italic=italic, color=color)}</w:p>"


def h(text: str, level: int = 1) -> str:
    return p(text, style=f"Heading{level}", keep_next=True)


def bullet(text: str) -> str:
    return p(text, bullet=True)


def step(number: int, title: str, body: str) -> list[str]:
    return [p(f"PASSO {number} — {title}", style="Step", keep_next=True), p(body)]


def callout(title: str, body: str, *, kind: str = "info") -> str:
    colors = {
        "info": ("DCEAF7", "17365D"),
        "tip": ("E2F0D9", "375623"),
        "warning": ("FFF2CC", "7F6000"),
        "critical": ("FCE4D6", "9C0006"),
    }
    fill, text_color = colors[kind]
    content = run(title + " ", bold=True, color=text_color) + run(body, color=text_color)
    return (
        '<w:tbl><w:tblPr><w:tblW w:w="0" w:type="auto"/><w:tblCellMar>'
        '<w:top w:w="140" w:type="dxa"/><w:left w:w="180" w:type="dxa"/>'
        '<w:bottom w:w="140" w:type="dxa"/><w:right w:w="180" w:type="dxa"/>'
        '</w:tblCellMar></w:tblPr><w:tr><w:tc><w:tcPr><w:shd w:fill="'
        + fill
        + '"/><w:tcW w:w="9000" w:type="dxa"/></w:tcPr><w:p>'
        + content
        + "</w:p></w:tc></w:tr></w:tbl>"
        + p()
    )


def table(headers: list[str], rows: list[list[str]], widths: list[int] | None = None) -> str:
    widths = widths or [9000 // len(headers)] * len(headers)

    def cell(text: str, width: int, header: bool = False) -> str:
        shade = '<w:shd w:fill="17365D"/>' if header else ""
        color = "FFFFFF" if header else None
        return (
            f'<w:tc><w:tcPr><w:tcW w:w="{width}" w:type="dxa"/>{shade}</w:tcPr>'
            f'<w:p>{run(text, bold=header, color=color)}</w:p></w:tc>'
        )

    grid = "".join(f'<w:gridCol w:w="{width}"/>' for width in widths)
    trs = ["<w:tr>" + "".join(cell(x, widths[i], True) for i, x in enumerate(headers)) + "</w:tr>"]
    for row in rows:
        trs.append("<w:tr>" + "".join(cell(x, widths[i]) for i, x in enumerate(row)) + "</w:tr>")
    return (
        '<w:tbl><w:tblPr><w:tblStyle w:val="TableGrid"/><w:tblW w:w="9000" w:type="dxa"/>'
        '<w:tblCellMar><w:top w:w="100" w:type="dxa"/><w:left w:w="120" w:type="dxa"/>'
        '<w:bottom w:w="100" w:type="dxa"/><w:right w:w="120" w:type="dxa"/></w:tblCellMar>'
        f'</w:tblPr><w:tblGrid>{grid}</w:tblGrid>{"".join(trs)}</w:tbl>' + p()
    )


def image(key: str, rel_id: str, *, width_inches: float, caption: str | None = None) -> str:
    px_w, px_h = png_size(ASSETS[key])
    cx = int(width_inches * 914400)
    cy = int(cx * px_h / px_w)
    drawing = f"""<w:p><w:pPr><w:jc w:val="center"/></w:pPr><w:r><w:drawing>
<wp:inline xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" distT="0" distB="0" distL="0" distR="0">
<wp:extent cx="{cx}" cy="{cy}"/><wp:effectExtent l="0" t="0" r="0" b="0"/><wp:docPr id="{rel_id[3:]}" name="{escape(key)}"/>
<wp:cNvGraphicFramePr><a:graphicFrameLocks xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" noChangeAspect="1"/></wp:cNvGraphicFramePr>
<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:nvPicPr><pic:cNvPr id="0" name="{escape(key)}.png"/><pic:cNvPicPr/></pic:nvPicPr>
<pic:blipFill><a:blip xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" r:embed="{rel_id}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>
<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic>
</a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>"""
    if caption:
        drawing += p(caption, style="Caption", center=True, italic=True, color="5B6573")
    return drawing


def page_break() -> str:
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


def build_document() -> str:
    body: list[str] = [
        p("MANUAL PÚBLICO", style="Title"),
        p("AudioLab Editor", style="ProductTitle"),
        p("Capture, prepare e separe áudio e vídeo em um único fluxo", style="Subtitle"),
        image("logo", "rId3", width_inches=1.7),
        p("Guia de uso para pessoas — sem terminal, sem Python e sem comandos técnicos", style="CoverNote", center=True),
        p("Edição pública • Junho de 2026", center=True, italic=True, color="5B6573"),
        page_break(),
        h("Bem-vindo ao AudioLab Editor"),
        p(
            "O AudioLab Editor reúne ferramentas reconhecidas de mídia e inteligência artificial em uma interface "
            "única. Você escolhe o que deseja fazer; o aplicativo cuida dos mecanismos técnicos necessários."
        ),
        callout(
            "Para quem é este manual:",
            "criadores de conteúdo, educadores, músicos, estudantes e qualquer pessoa que queira trabalhar com "
            "áudio e vídeo sem aprender comandos de terminal.",
            kind="tip",
        ),
        h("O que você aprenderá"),
        table(
            ["Etapa", "O que você fará", "Tecnologia usada internamente"],
            [
                ["1. Capturar", "Analisar uma URL e baixar vídeo ou áudio", "yt-dlp"],
                ["2. Preparar", "Consultar, cortar, converter, extrair ou compactar mídia", "ffprobe e FFmpeg"],
                ["3. Separar", "Criar vocais, bateria, baixo e outros stems", "Demucs + PyTorch"],
                ["4. Combinar", "Usar as etapas em fluxos completos", "Integração do AudioLab Editor"],
            ],
            [1300, 4300, 3400],
        ),
        h("Antes de começar"),
        bullet("Use somente materiais que você tenha autorização para baixar e processar."),
        bullet("Confirme que há espaço livre na pasta escolhida; vídeos e stems podem ocupar bastante espaço."),
        bullet("Mantenha conexão com a internet durante downloads e na primeira preparação de recursos de IA."),
        bullet("Para melhor desempenho, feche aplicações pesadas durante separações longas."),
        bullet("Escolha um nome de projeto para manter os resultados organizados."),
        image("main", "rId4", width_inches=6.25, caption="Tela principal do AudioLab Editor"),
        page_break(),
        h("1. Captura de mídia — yt-dlp"),
        p(
            "A aba Captura de Mídia usa o yt-dlp internamente para obter informações e baixar materiais de serviços "
            "compatíveis. Você não precisa instalar nem executar o yt-dlp separadamente."
        ),
        h("1.1 Entenda os controles", level=2),
        table(
            ["Controle", "Para que serve"],
            [
                ["URL", "Endereço do material que será analisado e capturado."],
                ["Analisar", "Mostra título, duração, canal e endereço antes do download."],
                ["Pasta de saída", "Local principal onde o projeto será criado."],
                ["Nome do projeto", "Agrupa os arquivos relacionados. Em branco, usa ALE."],
                ["Modo", "Vídeo original, vídeo comprimido ou somente áudio."],
                ["Qualidade", "Controla o equilíbrio entre qualidade e tamanho no vídeo comprimido."],
                ["Formato e bitrate", "Aparecem no modo Somente áudio."],
                ["Iniciar", "Executa a captura e acompanha o progresso."],
            ],
            [2500, 6500],
        ),
        image("capture", "rId5", width_inches=6.25, caption="Aba Captura de Mídia"),
        h("1.2 Baixar um vídeo completo", level=2),
        *step(1, "Cole a URL", "Copie o endereço do material e cole no campo URL."),
        *step(2, "Analise antes de baixar", "Clique em Analisar e confira título, duração e canal. Se os dados não correspondem ao esperado, não prossiga."),
        *step(3, "Escolha onde salvar", "Selecione a pasta de saída e informe um nome curto para o projeto."),
        *step(4, "Selecione o modo", "Use Vídeo original para preservar a mídia ou Vídeo comprimido para reduzir o tamanho."),
        *step(5, "Inicie e acompanhe", "Clique em Iniciar. Não feche o aplicativo enquanto a barra e o histórico indicarem processamento."),
        *step(6, "Abra o resultado", "Ao concluir, use Abrir pasta de destino para localizar o arquivo."),
        h("1.3 Baixar somente o áudio", level=2),
        p("Repita a análise da URL e altere o modo para Somente áudio. Depois:"),
        bullet("Escolha MP3 para ampla compatibilidade."),
        bullet("Escolha WAV ou FLAC para preservar melhor a qualidade antes de editar ou separar stems."),
        bullet("Em MP3, 192 kbps oferece bom equilíbrio; 320 kbps prioriza qualidade e aumenta o arquivo."),
        bullet("Clique em Iniciar e aguarde o pós-processamento."),
        h("1.4 Baixar um capítulo específico", level=2),
        callout(
            "Limitação confirmada na versão atual:",
            "o AudioLab Editor ainda não exibe a lista de capítulos nem permite selecionar um intervalo de capítulo "
            "antes do download. Uma URL com marca de tempo também não garante que somente aquele trecho será baixado.",
            kind="critical",
        ),
        p(
            "Até que o seletor de capítulos seja implementado, use o fluxo seguro: baixe o material autorizado, "
            "identifique o início e o fim do capítulo e gere o trecho nas abas Editor de Vídeo ou Editor de Áudio."
        ),
        p("Fluxo provisório:", keep_next=True),
        bullet("Baixe o vídeo ou o áudio completo."),
        bullet("Anote o início e o fim do capítulo mostrado no provedor."),
        bullet("Abra o arquivo no editor correspondente."),
        bullet("Informe os tempos e exporte somente o trecho desejado."),
        callout(
            "Orientação para o vídeo público:",
            "não grave uma seleção de capítulo como recurso nativo antes de ela existir na interface. No vídeo atual, "
            "demonstre o recorte após o download e identifique-o como fluxo provisório.",
            kind="warning",
        ),
        h("1.5 Se algo não funcionar", level=2),
        table(
            ["Situação", "O que fazer"],
            [
                ["URL inválida", "Copie novamente o endereço completo, começando por http:// ou https://."],
                ["Não foi possível analisar", "Confirme internet, disponibilidade pública do material e compatibilidade do serviço."],
                ["Download interrompido", "Mantenha o aplicativo aberto, verifique a conexão e tente novamente."],
                ["Conteúdo privado ou regional", "Use apenas acesso legítimo. O aplicativo não contorna restrições."],
                ["Arquivo muito grande", "Use Vídeo comprimido ou Somente áudio e verifique o espaço livre."],
            ],
            [3000, 6000],
        ),
        page_break(),
        h("2. Preparação de mídia — ffprobe e FFmpeg"),
        p(
            "FFprobe identifica características da mídia, como duração, faixas, codecs e resolução. FFmpeg executa "
            "as transformações: corte, conversão, extração de áudio e compactação. No AudioLab Editor, ambos trabalham "
            "nos bastidores; não há necessidade de abrir um terminal."
        ),
        callout(
            "Diferença simples:",
            "ffprobe observa e descreve o arquivo; FFmpeg cria uma nova versão do arquivo.",
            kind="info",
        ),
        h("2.1 Editor de áudio", level=2),
        p("Use esta aba para cortar áudio, mudar o formato ou extrair o som de um vídeo."),
        image("trim", "rId6", width_inches=6.25, caption="Aba Editor de Áudio"),
        h("Cortar e converter áudio", level=3),
        *step(1, "Selecione o arquivo", "Clique em Procurar e escolha um arquivo de áudio ou vídeo compatível."),
        *step(2, "Escolha destino e projeto", "Defina onde o resultado será salvo e mantenha o mesmo projeto usado na captura."),
        *step(3, "Escolha formato e qualidade", "MP3 é prático; WAV e FLAC são indicados para edição e stems; M4A/AAC equilibram qualidade e tamanho."),
        *step(4, "Informe o trecho", "No Editor de Áudio, prefira informar os tempos em segundos: por exemplo, início 75 e fim 105 para obter um trecho de 30 segundos."),
        *step(5, "Exporte", "Clique em Exportar corte, aguarde a conclusão e abra a pasta pelo botão exibido."),
        h("Extrair áudio de um vídeo", level=3),
        p(
            "Selecione o vídeo, escolha o formato de áudio e clique em Extrair áudio. Para separar stems depois, "
            "prefira WAV ou FLAC quando o espaço em disco permitir."
        ),
        h("2.2 Editor de vídeo", level=2),
        p("Use esta aba para recortar um intervalo e gerar um novo vídeo."),
        image("video", "rId7", width_inches=6.25, caption="Aba Editor de Vídeo"),
        *step(1, "Selecione o vídeo", "Clique em Procurar e escolha o arquivo capturado."),
        *step(2, "Informe início e fim", "Use HH:MM:SS. Exemplo: 00:05:10 até 00:08:25."),
        *step(3, "Defina formato", "MP4 oferece maior compatibilidade. MKV é flexível; AVI é voltado a fluxos legados."),
        *step(4, "Defina qualidade", "Alta preserva mais detalhes; Balanceada reduz tamanho; Compacta prioriza economia de espaço."),
        *step(5, "Renderize", "Clique em Renderizar e aguarde. Vídeos longos podem exigir vários minutos."),
        h("2.3 Qual formato escolher?", level=2),
        table(
            ["Objetivo", "Escolha sugerida", "Motivo"],
            [
                ["Compartilhar áudio", "MP3", "Ampla compatibilidade e tamanho moderado."],
                ["Editar ou criar stems", "WAV ou FLAC", "Menor perda acumulada durante o processamento."],
                ["Compartilhar vídeo", "MP4", "Compatível com navegadores, celulares e redes."],
                ["Preservar qualidade", "Original, WAV ou FLAC", "Evita compactações adicionais quando possível."],
                ["Economizar espaço", "MP3 ou vídeo Compacto", "Reduz o tamanho com perda controlada."],
            ],
            [2800, 2200, 4000],
        ),
        h("2.4 Solução de problemas", level=2),
        table(
            ["Situação", "Como agir"],
            [
                ["Arquivo não abre", "Teste outro arquivo e confirme que o original não está incompleto ou corrompido."],
                ["Tempo inválido", "No áudio, use segundos; no vídeo, use HH:MM:SS e mantenha o fim maior que o início."],
                ["Processamento demorado", "Escolha qualidade Balanceada, feche aplicações pesadas e aguarde."],
                ["Sem som", "Confirme que o arquivo original possui faixa de áudio."],
                ["Sem espaço", "Escolha outra pasta ou libere espaço antes de tentar novamente."],
            ],
            [3000, 6000],
        ),
        page_break(),
        h("3. Criação de stems — Demucs"),
        p(
            "Stems são faixas separadas de uma música. O AudioLab Editor usa inteligência artificial para estimar "
            "vocais e instrumentos a partir de uma gravação pronta. O resultado é útil para estudo, remix, karaokê, "
            "acessibilidade, análise e produção — sempre respeitando direitos de uso."
        ),
        image("stems", "rId8", width_inches=6.25, caption="Aba Separador de Stems"),
        h("3.1 Modos disponíveis", level=2),
        table(
            ["Modo", "Arquivos esperados", "Indicado para"],
            [
                ["Apenas vocais", "vocals e no_vocals", "Karaokê, estudo vocal e base instrumental."],
                ["4 stems", "vocals, drums, bass e other", "Remix e análise musical geral."],
                ["6 stems", "4 stems + guitar e piano", "Estudo mais detalhado de arranjo."],
            ],
            [2300, 3300, 3400],
        ),
        callout(
            "Importante:",
            "a separação é uma estimativa. Vazamentos entre faixas, reverberação e artefatos podem ocorrer, "
            "principalmente em gravações ao vivo, compactadas ou com muitos instrumentos sobrepostos.",
            kind="warning",
        ),
        h("3.2 Separar um arquivo", level=2),
        *step(1, "Abra a aba Stems", "Aguarde a verificação dos recursos de IA. O botão ficará disponível quando o ambiente estiver pronto."),
        *step(2, "Escolha a origem", "Clique em Procurar e selecione um arquivo. WAV ou FLAC tende a preservar melhor o material de entrada."),
        *step(3, "Escolha a pasta e o projeto", "Use a mesma pasta e o mesmo nome das etapas anteriores para facilitar a rastreabilidade."),
        *step(4, "Selecione o modo", "Comece por Apenas vocais para rapidez, 4 stems para uso geral ou 6 stems para maior detalhamento."),
        *step(5, "Escolha o formato", "WAV prioriza qualidade; FLAC reduz espaço sem perda; MP3 320 kbps facilita compartilhamento."),
        *step(6, "Inicie", "Clique em Iniciar separação. Não feche o aplicativo e evite suspender o computador."),
        *step(7, "Confira o resultado", "Use Abrir pasta de destino e ouça cada faixa separadamente antes de utilizá-la."),
        h("3.3 Separação em lote", level=2),
        p(
            "O botão Procurar permite selecionar vários arquivos. Todos receberão o mesmo modo e formato. Antes de "
            "iniciar, confira a lista, o espaço livre e a pasta de destino. O histórico mostra quantos itens foram "
            "concluídos e quais falharam."
        ),
        h("3.4 Tempo e qualidade", level=2),
        bullet("Arquivos longos e o modo de 6 stems exigem mais memória, processamento e espaço."),
        bullet("A primeira execução pode ser mais lenta por causa da preparação dos modelos."),
        bullet("Evite converter repetidamente entre formatos com perda, como MP3."),
        bullet("Use fones de ouvido para conferir vazamentos e artefatos em cada stem."),
        bullet("Se o resultado não estiver adequado, teste uma fonte de melhor qualidade antes de repetir."),
        h("3.5 Solução de problemas", level=2),
        table(
            ["Situação", "Como agir"],
            [
                ["Recursos de IA indisponíveis", "Reinstale a versão oficial do aplicativo ou reporte o erro; o público não deve executar comandos Python."],
                ["FFmpeg não encontrado", "Reinstale o aplicativo oficial. A distribuição pública deve fornecer os componentes necessários."],
                ["Pouco espaço", "Libere ao menos alguns gigabytes ou use FLAC/MP3 e uma pasta em outro disco."],
                ["Processamento muito lento", "Comece por Apenas vocais ou 4 stems e feche aplicações pesadas."],
                ["Resultado com vazamentos", "Use uma fonte melhor e reconheça que a separação por IA não é perfeita."],
            ],
            [3100, 5900],
        ),
        page_break(),
        h("4. Fluxos combinados por afinidade"),
        h("Fluxo A — Material online para stems", level=2),
        p("Use quando você deseja estudar ou separar o áudio de um material autorizado disponível por URL."),
        table(
            ["Ordem", "Aba", "Ação", "Resultado"],
            [
                ["1", "Captura", "Analisar e baixar em Somente áudio, preferencialmente FLAC/WAV", "Arquivo de áudio"],
                ["2", "Editor de Áudio", "Remover trechos desnecessários", "Trecho preparado"],
                ["3", "Stems", "Selecionar 2, 4 ou 6 stems", "Faixas separadas"],
            ],
            [900, 1800, 4100, 2200],
        ),
        h("Fluxo B — Capítulo de vídeo para stems", level=2),
        p("Use o fluxo provisório enquanto o seletor nativo de capítulos não estiver disponível:"),
        table(
            ["Ordem", "Aba", "Ação", "Resultado"],
            [
                ["1", "Captura", "Baixar o vídeo autorizado completo", "Vídeo original"],
                ["2", "Editor de Vídeo", "Recortar pelos tempos do capítulo", "Vídeo do capítulo"],
                ["3", "Editor de Áudio", "Extrair WAV ou FLAC", "Áudio do capítulo"],
                ["4", "Stems", "Separar o modo desejado", "Faixas do capítulo"],
            ],
            [900, 1800, 4100, 2200],
        ),
        h("Fluxo C — Arquivo local para edição", level=2),
        p("Se o material já está no computador, comece diretamente no Editor de Áudio, Editor de Vídeo ou Stems."),
        callout(
            "Regra prática:",
            "capture primeiro, prepare apenas o trecho necessário e execute IA por último. Isso reduz tempo, espaço "
            "e processamento sem perder a rastreabilidade do projeto.",
            kind="tip",
        ),
        page_break(),
        h("5. Roteiro para a série de vídeos"),
        p(
            "Grave primeiro os componentes individualmente. Depois, publique vídeos curtos que combinem recursos "
            "por afinidade. Use sempre material próprio, licenciado ou de demonstração."
        ),
        h("Vídeo 1 — Captura com yt-dlp", level=2),
        bullet("Apresente o problema: obter vídeo ou áudio sem usar comandos."),
        bullet("Cole uma URL, clique em Analisar e confira os metadados."),
        bullet("Demonstre Vídeo original, Vídeo comprimido e Somente áudio."),
        bullet("Mostre o projeto criado e o botão Abrir pasta de destino."),
        bullet("Para capítulos, demonstre o recorte provisório e informe claramente a limitação atual."),
        h("Vídeo 2 — ffprobe e FFmpeg", level=2),
        bullet("Explique que ffprobe lê informações e FFmpeg transforma a mídia nos bastidores."),
        bullet("Demonstre um corte de áudio com tempos em segundos."),
        bullet("Extraia áudio de um vídeo em WAV ou FLAC."),
        bullet("Demonstre um corte de vídeo usando HH:MM:SS."),
        bullet("Compare rapidamente Alta, Balanceada e Compacta."),
        h("Vídeo 3 — Separador de stems", level=2),
        bullet("Explique o que é um stem e mostre o arquivo de entrada."),
        bullet("Compare Apenas vocais, 4 stems e 6 stems."),
        bullet("Mostre WAV, FLAC e MP3 320 kbps."),
        bullet("Acompanhe progresso, pasta de saída e audição das faixas."),
        bullet("Explique limites da IA sem prometer isolamento perfeito."),
        h("Vídeo 4 — Fluxo integrado", level=2),
        bullet("Capture um material autorizado."),
        bullet("Recorte o trecho realmente necessário."),
        bullet("Extraia ou converta o áudio."),
        bullet("Crie os stems e apresente o resultado final."),
        h("Checklist de gravação", level=2),
        bullet("☐ Ocultar caminhos, nomes ou dados pessoais antes de gravar."),
        bullet("☐ Usar uma pasta de demonstração vazia e um nome de projeto curto."),
        bullet("☐ Confirmar internet, espaço livre e áudio do computador."),
        bullet("☐ Mostrar a interface inteira antes de aproximar cada controle."),
        bullet("☐ Explicar o resultado esperado antes de clicar em Iniciar."),
        bullet("☐ Aguardar a conclusão real e abrir o arquivo gerado."),
        bullet("☐ Não cortar mensagens de erro importantes; explique como corrigi-las."),
        bullet("☐ Não apresentar o seletor de capítulos como pronto antes da implementação."),
        page_break(),
        h("6. Glossário rápido"),
        table(
            ["Termo", "Significado em linguagem simples"],
            [
                ["Bitrate", "Quantidade de dados usada por segundo; em geral, maior significa melhor áudio e arquivo maior."],
                ["Codec", "Método usado para codificar e reproduzir áudio ou vídeo."],
                ["FFmpeg", "Motor que corta, converte, extrai e compacta mídia."],
                ["ffprobe", "Leitor técnico que identifica as características de um arquivo de mídia."],
                ["Stem", "Uma parte isolada da música, como vocal, bateria ou baixo."],
                ["Renderizar", "Criar um novo arquivo de vídeo com as escolhas realizadas."],
                ["FLAC", "Áudio compactado sem perda de qualidade."],
                ["WAV", "Áudio de alta qualidade e tamanho geralmente maior."],
                ["yt-dlp", "Mecanismo usado para analisar e capturar mídia de serviços compatíveis."],
            ],
            [2200, 6800],
        ),
        h("7. Mensagem final"),
        p(
            "O AudioLab Editor foi criado para transformar ferramentas técnicas poderosas em tarefas compreensíveis. "
            "O usuário não precisa dominar FFmpeg, yt-dlp ou Demucs: precisa apenas entender seu objetivo, escolher "
            "as opções adequadas e acompanhar o resultado."
        ),
        callout(
            "Em uma frase:",
            "capture o material, prepare somente o trecho necessário e aplique inteligência artificial ao final.",
            kind="info",
        ),
        p("AudioLab Editor • Capture, edite e separe áudio e vídeo com IA", center=True, italic=True, color="5B6573"),
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


CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Default Extension="png" ContentType="image/png"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>
  <Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>"""

ROOT_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>"""

STYLES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/><w:sz w:val="21"/><w:lang w:val="pt-BR"/></w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:spacing w:after="130" w:line="264" w:lineRule="auto"/><w:jc w:val="both"/></w:pPr></w:pPrDefault></w:docDefaults>
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/></w:style>
  <w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:before="360" w:after="80"/><w:jc w:val="center"/></w:pPr><w:rPr><w:rFonts w:ascii="Aptos Display" w:hAnsi="Aptos Display"/><w:b/><w:color w:val="3D6D8E"/><w:sz w:val="28"/><w:smallCaps/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="ProductTitle"><w:name w:val="Product Title"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:after="100"/><w:jc w:val="center"/></w:pPr><w:rPr><w:rFonts w:ascii="Aptos Display" w:hAnsi="Aptos Display"/><w:b/><w:color w:val="17365D"/><w:sz w:val="50"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Subtitle"><w:name w:val="Subtitle"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:after="220"/><w:jc w:val="center"/></w:pPr><w:rPr><w:color w:val="3D6D8E"/><w:sz w:val="25"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="CoverNote"><w:name w:val="Cover Note"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:before="160" w:after="120"/><w:jc w:val="center"/></w:pPr><w:rPr><w:b/><w:color w:val="17365D"/><w:sz w:val="22"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:pPr><w:keepNext/><w:spacing w:before="300" w:after="110"/><w:outlineLvl w:val="0"/></w:pPr><w:rPr><w:rFonts w:ascii="Aptos Display" w:hAnsi="Aptos Display"/><w:b/><w:color w:val="17365D"/><w:sz w:val="29"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:basedOn w:val="Normal"/><w:pPr><w:keepNext/><w:spacing w:before="230" w:after="80"/><w:outlineLvl w:val="1"/></w:pPr><w:rPr><w:b/><w:color w:val="3D6D8E"/><w:sz w:val="24"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading3"><w:name w:val="heading 3"/><w:basedOn w:val="Normal"/><w:pPr><w:keepNext/><w:spacing w:before="170" w:after="60"/><w:outlineLvl w:val="2"/></w:pPr><w:rPr><w:b/><w:color w:val="4472C4"/><w:sz w:val="22"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Step"><w:name w:val="Step"/><w:basedOn w:val="Normal"/><w:pPr><w:keepNext/><w:spacing w:before="130" w:after="40"/><w:ind w:left="240"/></w:pPr><w:rPr><w:b/><w:color w:val="17365D"/><w:sz w:val="21"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Caption"><w:name w:val="Caption"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:after="160"/><w:jc w:val="center"/></w:pPr><w:rPr><w:i/><w:color w:val="5B6573"/><w:sz w:val="18"/></w:rPr></w:style>
  <w:style w:type="table" w:styleId="TableGrid"><w:name w:val="Table Grid"/><w:tblPr><w:tblBorders><w:top w:val="single" w:sz="4" w:color="B4C6E7"/><w:left w:val="single" w:sz="4" w:color="B4C6E7"/><w:bottom w:val="single" w:sz="4" w:color="B4C6E7"/><w:right w:val="single" w:sz="4" w:color="B4C6E7"/><w:insideH w:val="single" w:sz="4" w:color="D9E2F3"/><w:insideV w:val="single" w:sz="4" w:color="D9E2F3"/></w:tblBorders></w:tblPr></w:style>
</w:styles>"""

NUMBERING = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:numbering xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:abstractNum w:abstractNumId="0"><w:multiLevelType w:val="singleLevel"/><w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="bullet"/><w:lvlText w:val="•"/><w:lvlJc w:val="left"/><w:pPr><w:tabs><w:tab w:val="num" w:pos="600"/></w:tabs><w:ind w:left="600" w:hanging="300"/></w:pPr><w:rPr><w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/></w:rPr></w:lvl></w:abstractNum>
  <w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num>
</w:numbering>"""

FOOTER = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:p><w:pPr><w:jc w:val="center"/></w:pPr><w:r><w:rPr><w:color w:val="7F8C8D"/><w:sz w:val="18"/></w:rPr><w:t>AudioLab Editor — Manual Público  •  </w:t></w:r><w:fldSimple w:instr="PAGE"><w:r><w:rPr><w:color w:val="7F8C8D"/><w:sz w:val="18"/></w:rPr><w:t>1</w:t></w:r></w:fldSimple></w:p></w:ftr>"""


def main() -> None:
    missing = [str(path) for path in ASSETS.values() if not path.exists()]
    if missing:
        raise FileNotFoundError("Assets ausentes: " + ", ".join(missing))

    image_rels = []
    for index, key in enumerate(ASSETS, start=3):
        image_rels.append(
            f'<Relationship Id="rId{index}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/{key}.png"/>'
        )
    doc_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>'
        + "".join(image_rels)
        + '<Relationship Id="rId9" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/>'
        '</Relationships>'
    )

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    core = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dc:title>AudioLab Editor — Manual Público Atualizado</dc:title><dc:subject>Guia humano de captura, preparação e separação de stems</dc:subject><dc:creator>AudioLab Editor</dc:creator><cp:keywords>AudioLab Editor; yt-dlp; FFmpeg; ffprobe; Demucs; stems</cp:keywords><dc:description>Manual público sem instruções Python ou Linux.</dc:description><dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created><dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified></cp:coreProperties>"""
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
        archive.writestr("word/_rels/document.xml.rels", doc_rels)
        for key, path in ASSETS.items():
            archive.write(path, f"word/media/{key}.png")
    print(OUTPUT)


if __name__ == "__main__":
    main()
