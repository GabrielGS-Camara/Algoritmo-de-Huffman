import heapq
import os
import tkinter as tk
from tkinter import filedialog

class CodificacaoHuffman:
    def __init__(self, caminho):
        self.caminho = caminho
        self.heap = []
        self.codigos = {}
        self.mapeamento_reverso = {}

    class NoHeap:
        def __init__(self, caractere, frequencia):
            self.caractere = caractere
            self.frequencia = frequencia
            self.esquerda = None
            self.direita = None

        def __lt__(self, outro):
            return self.frequencia < outro.frequencia

    def criar_dicionario_frequencias(self, texto):
        return {char: texto.count(char) for char in set(texto)}

    def criar_heap(self, frequencia):
        for chave, freq in frequencia.items():
            heapq.heappush(self.heap, self.NoHeap(chave, freq))

    def combinar_nos(self):
        while len(self.heap) > 1:
            no1 = heapq.heappop(self.heap)
            no2 = heapq.heappop(self.heap)
            combinado = self.NoHeap(None, no1.frequencia + no2.frequencia)
            combinado.esquerda = no1
            combinado.direita = no2
            heapq.heappush(self.heap, combinado)

    def gerar_codigos(self):
        raiz = heapq.heappop(self.heap)
        self._gerar_codigos_aux(raiz, "")

    def _gerar_codigos_aux(self, raiz, codigo_atual):
        if raiz is None:
            return
        if raiz.caractere is not None:
            self.codigos[raiz.caractere] = codigo_atual
            self.mapeamento_reverso[codigo_atual] = raiz.caractere
            return
        self._gerar_codigos_aux(raiz.esquerda, codigo_atual + "0")
        self._gerar_codigos_aux(raiz.direita, codigo_atual + "1")

    def obter_texto_codificado(self, texto):
        return "".join(self.codigos[caractere] for caractere in texto)

    def adicionar_padding(self, texto_codificado):
        padding_extra = 8 - len(texto_codificado) % 8
        texto_codificado += "0" * padding_extra
        info_padding = "{0:08b}".format(padding_extra)
        return info_padding + texto_codificado

    def obter_bytes(self, texto_codificado_preenchido):
        array_bytes = bytearray()
        for i in range(0, len(texto_codificado_preenchido), 8):
            byte = texto_codificado_preenchido[i:i+8]
            array_bytes.append(int(byte, 2))
        return array_bytes

    def compactar(self):
        nome_arquivo, _ = os.path.splitext(self.caminho)
        caminho_saida = nome_arquivo + ".bin"

        with open(self.caminho, 'r') as arquivo, open(caminho_saida, 'wb') as saida:
            texto = arquivo.read().rstrip()
            frequencias = self.criar_dicionario_frequencias(texto)
            self.criar_heap(frequencias)
            self.combinar_nos()
            self.gerar_codigos()
            texto_codificado = self.obter_texto_codificado(texto)
            texto_preenchido = self.adicionar_padding(texto_codificado)
            bytes_codificados = self.obter_bytes(texto_preenchido)
            saida.write(bytes(bytes_codificados))

        print("Compactação concluída:", caminho_saida)
        return caminho_saida

    def remover_padding(self, texto_codificado_preenchido):
        info_padding = texto_codificado_preenchido[:8]
        padding_extra = int(info_padding, 2)
        return texto_codificado_preenchido[8:-padding_extra]

    def decodificar_texto(self, texto_codificado):
        codigo_atual, texto_decodificado = "", ""
        for bit in texto_codificado:
            codigo_atual += bit
            if codigo_atual in self.mapeamento_reverso:
                texto_decodificado += self.mapeamento_reverso[codigo_atual]
                codigo_atual = ""
        return texto_decodificado

    def descompactar(self, caminho_entrada):
        nome_arquivo, _ = os.path.splitext(caminho_entrada)
        caminho_saida = nome_arquivo + "_descompactado.txt"

        with open(caminho_entrada, 'rb') as arquivo, open(caminho_saida, 'w') as saida:
            bits = "".join(bin(byte)[2:].rjust(8, '0') for byte in arquivo.read())
            texto_codificado = self.remover_padding(bits)
            texto_decodificado = self.decodificar_texto(texto_codificado)
            saida.write(texto_decodificado)

        print("Descompactação concluída:", caminho_saida)
        return caminho_saida

def select_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])

    if file_path:
        print(f"Arquivo selecionado: {file_path}")
        huffman = CodificacaoHuffman(file_path)

        caminho_compactado = huffman.compactar()
        print("Arquivo compactado:", caminho_compactado)

        caminho_descompactado = huffman.descompactar(caminho_compactado)
        print("Arquivo descompactado:", caminho_descompactado)

def main():
    print("Selecione um arquivo .txt para compressão e descompressão")
    select_file()

if __name__ == "__main__":
    main()
