"""Revise the PowerShell manual with direct, path-independent CLI examples."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from tempfile import NamedTemporaryFile
from xml.etree import ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
MANUAL = ROOT / "AudioLabEditor_Manual_PowerShell_WinGet.docx"
DOCUMENT_XML = "word/document.xml"
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W = f"{{{W_NS}}}"
ET.register_namespace("w", W_NS)


def paragraph_text(paragraph: ET.Element) -> str:
    return "".join(node.text or "" for node in paragraph.iter(f"{W}t"))


def set_paragraph_text(paragraph: ET.Element, text: str) -> None:
    paragraph_properties = paragraph.find(f"{W}pPr")
    run_properties = paragraph.find(f"{W}r/{W}rPr")
    for child in list(paragraph):
        if child is not paragraph_properties:
            paragraph.remove(child)
    run = ET.SubElement(paragraph, f"{W}r")
    if run_properties is not None:
        run.append(deepcopy(run_properties))
    text_node = ET.SubElement(run, f"{W}t")
    if text.startswith(" ") or text.endswith(" "):
        text_node.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    text_node.text = text


def clone_with_text(template: ET.Element, text: str) -> ET.Element:
    paragraph = deepcopy(template)
    set_paragraph_text(paragraph, text)
    return paragraph


def write_document(document: ET.Element) -> None:
    xml_bytes = ET.tostring(document, encoding="utf-8", xml_declaration=True)
    with NamedTemporaryFile(dir=MANUAL.parent, suffix=".docx", delete=False) as temp_file:
        temp_path = Path(temp_file.name)
    try:
        with ZipFile(MANUAL, "r") as source, ZipFile(temp_path, "w", ZIP_DEFLATED) as target:
            for entry in source.infolist():
                data = xml_bytes if entry.filename == DOCUMENT_XML else source.read(entry.filename)
                target.writestr(entry, data)
        temp_path.replace(MANUAL)
    finally:
        temp_path.unlink(missing_ok=True)


def main() -> None:
    if not MANUAL.exists():
        raise FileNotFoundError(MANUAL)

    with ZipFile(MANUAL, "r") as source:
        document = ET.fromstring(source.read(DOCUMENT_XML))
        # Release the original DOCX before replacing it on Windows.
        source.close()
        body = document.find(f"{W}body")
        if body is None:
            raise RuntimeError("Documento sem corpo XML")

        paragraphs = list(document.iter(f"{W}p"))
        by_text = {paragraph_text(item): item for item in paragraphs}
        parent_map = {child: parent for parent in document.iter() for child in parent}
        marker = "RLLabs é apenas a pasta usada na demonstração; não é requisito nem caminho padrão."
        if marker in by_text:
            for paragraph in list(document.iter(f"{W}p")):
                text = paragraph_text(paragraph)
                if text == '$Url = "COLE_A_URL_AQUI"':
                    parent_map[paragraph].remove(paragraph)
                elif text == '$Capitulo = "NOME EXATO DO CAPÍTULO"':
                    set_paragraph_text(paragraph, "Baixar capítulo pelo título, informando o nome diretamente")
            write_document(document)
            print(MANUAL)
            return

        command_template = by_text["winget --version"]
        normal_template = by_text["Guia técnico dos componentes que dão base ao AudioLab Editor. Use-o para demonstrações individuais, diagnóstico e compreensão do fluxo que a interface gráfica simplifica."]
        label_template = by_text["Analisar e listar formatos"]

        def remove(text: str) -> None:
            for paragraph in list(document.iter(f"{W}p")):
                if paragraph_text(paragraph) == text:
                    parent_map[paragraph].remove(paragraph)

        def replace(old: str, new: str) -> None:
            matches = [item for item in document.iter(f"{W}p") if paragraph_text(item) == old]
            if not matches:
                raise KeyError(f"Parágrafo não encontrado: {old}")
            for paragraph in matches:
                set_paragraph_text(paragraph, new)

        def insert_before(anchor_text: str, items: list[tuple[ET.Element, str]]) -> None:
            anchor = by_text[anchor_text]
            parent = parent_map[anchor]
            index = list(parent).index(anchor)
            for offset, (template, text) in enumerate(items):
                parent.insert(index + offset, clone_with_text(template, text))

        for text in (
            '$Projeto = Join-Path $HOME "Videos\\AudioLabCLI"',
            "New-Item -ItemType Directory -Path $Projeto -Force | Out-Null",
            "Set-Location $Projeto",
            '$Url = "COLE_A_URL_AQUI"',
        ):
            remove(text)

        insert_before(
            "Analisar e listar formatos",
            [
                (normal_template, marker),
                (
                    normal_template,
                    "Nos comandos abaixo, troque C:\\Users\\SeuUsuario\\Desktop\\RLLabs pela pasta que você preferir. Se já estiver na pasta desejada, use somente os comandos da ferramenta.",
                ),
                (label_template, "Três formas de escolher onde trabalhar"),
                (command_template, 'Set-Location "C:\\Users\\SeuUsuario\\Desktop\\RLLabs"'),
                (command_template, 'Set-Location "$HOME\\Downloads"'),
                (command_template, 'yt-dlp -P "D:\\Midia" "COLE_A_URL_AQUI"'),
            ],
        )

        replacements = {
            'yt-dlp --print "Título: %(title)s" --print "Duração: %(duration_string)s" --print "Canal: %(uploader)s" $Url':
                'yt-dlp --print "Título: %(title)s" --print "Duração: %(duration_string)s" --print "Canal: %(uploader)s" "COLE_A_URL_AQUI"',
            "yt-dlp --list-formats $Url": 'yt-dlp --list-formats "COLE_A_URL_AQUI"',
            'yt-dlp --no-playlist -f "bv*+ba/b" --merge-output-format mp4 -o "%(title).180s.%(ext)s" $Url':
                'yt-dlp --no-playlist -f "bv*+ba/b" --merge-output-format mp4 -o "%(title).180s.%(ext)s" "COLE_A_URL_AQUI"',
            'yt-dlp --no-playlist -x --audio-format mp3 --audio-quality 0 -o "%(title).180s.%(ext)s" $Url':
                'yt-dlp --no-playlist -x --audio-format mp3 --audio-quality 0 -o "%(title).180s.%(ext)s" "COLE_A_URL_AQUI"',
            '$Info = yt-dlp --dump-single-json --skip-download $Url | ConvertFrom-Json':
                'yt-dlp --dump-single-json --skip-download "COLE_A_URL_AQUI" | ConvertFrom-Json | Select-Object -ExpandProperty chapters | Format-Table start_time,end_time,title -AutoSize',
            '$Capitulo = "NOME EXATO DO CAPÍTULO"': "Baixar capítulo pelo título, informando o nome diretamente",
            '  -o "%(title).120s - %(section_title).100s.%(ext)s" $Url':
                '  -o "%(title).120s - %(section_title).100s.%(ext)s" "COLE_A_URL_AQUI"',
            '  -o "%(title).120s - trecho.%(ext)s" $Url':
                '  -o "%(title).120s - trecho.%(ext)s" "COLE_A_URL_AQUI"',
            '$Entrada = "C:\\Midia\\video.mp4"': 'Test-Path -LiteralPath "C:\\Midia\\video.mp4"',
            "Test-Path -LiteralPath $Entrada": 'ffprobe -hide_banner "C:\\Midia\\video.mp4"',
            "ffprobe -hide_banner $Entrada": 'ffprobe -v error -show_format -show_streams -of json "C:\\Midia\\video.mp4" | ConvertFrom-Json | Select-Object -ExpandProperty format',
            '$Probe = ffprobe -v error -show_format -show_streams -of json $Entrada | ConvertFrom-Json':
                'ffprobe -v error -show_streams -of json "C:\\Midia\\video.mp4" | ConvertFrom-Json | Select-Object -ExpandProperty streams | Format-Table index,codec_type,codec_name,width,height,sample_rate,channels -AutoSize',
            '$Probe = ffprobe -v error -show_chapters -of json $Entrada | ConvertFrom-Json':
                'ffprobe -v error -show_chapters -of json "C:\\Midia\\video.mp4" | ConvertFrom-Json | Select-Object -ExpandProperty chapters | Format-Table start_time,end_time,tags -AutoSize',
            "WinGet instala Python; Demucs fica em ambiente virtual isolado.":
                "WinGet instala Python; os comandos abaixo criam apenas um ambiente virtual .venv na pasta atual. Nenhum nome de projeto ou variável é necessário.",
            '$Base = Join-Path $HOME "AudioLabCLI"': "py -3.11 -m venv .venv",
            '$Venv = Join-Path $Base ".venv"': ".\\.venv\\Scripts\\python.exe -m pip install --upgrade pip",
            "New-Item -ItemType Directory -Path $Base -Force | Out-Null": ".\\.venv\\Scripts\\python.exe -m pip install demucs",
            "py -3.11 -m venv $Venv": "Separar stems na pasta atual ou em qualquer destino explícito",
            '$Entrada = "C:\\Midia\\musica.wav"': '.\\.venv\\Scripts\\python.exe -m demucs -n htdemucs --two-stems vocals -o ".\\stems" "C:\\Midia\\musica.wav"',
            '$Stems = "C:\\Midia\\stems"': '.\\.venv\\Scripts\\python.exe -m demucs -n htdemucs -o "D:\\Resultados\\stems" "C:\\Midia\\musica.wav"',
            "Primeira execução: o modelo pode ser baixado. Garanta internet, energia e espaço.":
                "Primeira execução: o modelo pode ser baixado. Garanta internet, energia e espaço. Os caminhos C:\\Midia e D:\\Resultados são exemplos; use pastas existentes no seu computador.",
            "Demucs sem torch": "Demucs ou torch ausente",
            "Instale demucs com o mesmo $Python.": "Execute .\\.venv\\Scripts\\python.exe -m pip install demucs na pasta que contém o .venv.",
        }
        for old, new in replacements.items():
            replace(old, new)

        for text in (
            "$Info.chapters | Select-Object start_time,end_time,title | Format-Table -AutoSize",
            "$Probe.format | Select-Object filename,format_name,duration,size,bit_rate",
            "$Probe.streams | Select-Object index,codec_type,codec_name,width,height,sample_rate,channels",
            "$Probe.chapters | Select-Object start_time,end_time,tags | Format-Table -AutoSize",
            '$Python = Join-Path $Venv "Scripts\\python.exe"',
            "& $Python -m pip install --upgrade pip",
            "& $Python -m pip install demucs",
            "Não ative o ambiente: & $Python usa diretamente o runtime isolado sem mudar ExecutionPolicy.",
            "& $Python -m demucs -n htdemucs --two-stems vocals -o $Stems $Entrada",
            "& $Python -m demucs -n htdemucs -o $Stems $Entrada",
            "& $Python -m demucs -n htdemucs_6s -o $Stems $Entrada",
            "& $Python -m demucs -n htdemucs --flac -o $Stems $Entrada",
            "& $Python -m demucs -n htdemucs --mp3 --mp3-bitrate 320 -o $Stems $Entrada",
            "& $Python -m demucs -n htdemucs --device cpu -o $Stems $Entrada",
        ):
            remove(text)

        insert_before(
            "Formatos e CPU",
            [
                (command_template, '.\\.venv\\Scripts\\python.exe -m demucs -n htdemucs_6s -o ".\\stems" ".\\musica.wav"'),
            ],
        )
        insert_before(
            "Primeira execução: o modelo pode ser baixado. Garanta internet, energia e espaço.",
            [
                (command_template, '.\\.venv\\Scripts\\python.exe -m demucs -n htdemucs --flac -o ".\\stems" ".\\musica.wav"'),
                (command_template, '.\\.venv\\Scripts\\python.exe -m demucs -n htdemucs --mp3 --mp3-bitrate 320 -o ".\\stems" ".\\musica.wav"'),
                (command_template, '.\\.venv\\Scripts\\python.exe -m demucs -n htdemucs --device cpu -o ".\\stems" ".\\musica.wav"'),
            ],
        )

        pipeline_start = by_text['$ErrorActionPreference = "Stop"']
        section_8 = by_text["8. Roteiro de vídeos"]
        ordered_paragraphs = list(document.iter(f"{W}p"))
        start_index = ordered_paragraphs.index(pipeline_start)
        end_index = ordered_paragraphs.index(section_8)
        for item in ordered_paragraphs[start_index:end_index]:
            parent = parent_map.get(item)
            if parent is not None and item in list(parent):
                parent.remove(item)
        insert_before(
            "8. Roteiro de vídeos",
            [
                (normal_template, "Exemplo direto na pasta de demonstração. Substitua o primeiro caminho por qualquer pasta existente e ajuste o nome do capítulo e a URL."),
                (command_template, 'Set-Location "C:\\Users\\SeuUsuario\\Desktop\\RLLabs"'),
                (command_template, 'yt-dlp --download-sections "*NOME EXATO DO CAPÍTULO" --force-keyframes-at-cuts -f "bv*+ba/b" --merge-output-format mp4 -o "video.%(ext)s" "COLE_A_URL_AQUI"'),
                (command_template, 'ffmpeg -y -i ".\\video.mp4" -vn -c:a pcm_s24le -ar 48000 ".\\audio.wav"'),
                (command_template, '.\\.venv\\Scripts\\python.exe -m demucs -n htdemucs -o ".\\stems" ".\\audio.wav"'),
                (normal_template, "Alternativa: execute os mesmos três comandos dentro de Downloads, D:\\Midia ou outra pasta; apenas os caminhos de entrada e saída mudam."),
            ],
        )

        # Fix the two remaining chapter commands after removing their temporary variable.
        for paragraph in document.iter(f"{W}p"):
            text = paragraph_text(paragraph)
            if text == 'yt-dlp --download-sections "*$Capitulo" --force-keyframes-at-cuts `':
                set_paragraph_text(paragraph, 'yt-dlp --download-sections "*NOME EXATO DO CAPÍTULO" --force-keyframes-at-cuts `')

        write_document(document)

    print(MANUAL)


if __name__ == "__main__":
    main()
