import random
import datetime

# ================= GERAÇÃO =================

def gerarDataHora(i):
    base = datetime.datetime(2026, 3, 30, 22, 8, 0)
    data = datetime.timedelta(seconds=i * random.randint(5, 20))
    return (base + data).strftime('%d/%m/%Y %H:%M:%S')


def gerarIp(i):
    if 20 <= i <= 30:
        return '200.0.111.135'
    r = random.randint(1, 6)
    if r == 1: return '192.168.5.6'
    elif r == 2: return '192.168.5.8'
    elif r == 3: return '192.168.5.9'
    elif r == 4: return '192.168.25.8'
    elif r == 5: return '192.168.45.8'
    else: return '192.168.65.68'


def gerarRecurso(i):
    if i % 7 == 0: return "/admin"
    elif i % 5 == 0: return "/login"
    elif i % 11 == 0: return "/config"
    else: return "/home"


def gerarMetodo(i):
    if i % 2 == 0: return "GET"
    else: return "POST"


def gerarStatus(i, recurso):
    if recurso == "/admin" and i % 2 == 0: return 403
    if recurso == "/login" and i % 3 == 0: return 403
    if i % 15 == 0: return 500
    if i % 12 == 0: return 404
    return 200


def gerarTempo(i):
    if 20 <= i <= 25:
        return 500 + (i * 50)
    return 100 + (i % 5) * 100


def gerarAgente(i):
    if i % 12 == 0: return "Bot"
    elif i % 9 == 0: return "Crawler"
    elif i % 7 == 0: return "Spider"
    else: return "Chrome"


def gerarArquivo(nome_arq, qtd):
    with open(nome_arq, 'w', encoding='utf-8') as arq:
        for i in range(qtd):
            data = gerarDataHora(i)
            ip = gerarIp(i)
            recurso = gerarRecurso(i)
            metodo = gerarMetodo(i)
            status = gerarStatus(i, recurso)
            tempo = gerarTempo(i)
            agente = gerarAgente(i)

            linha = f'[{data}] {ip} - {metodo} - {status} - {recurso} - {tempo}ms - 512B - HTTP/1.1 - {agente} - /home'
            arq.write(linha + '\n')

    print("Logs gerados com sucesso!")


# ================= ANÁLISE =================

def analisarLog(nome_arq):
    with open(nome_arq, 'r', encoding='utf-8') as arq:

        total = sucesso = erros = erros500 = 0
        somaTempo = maior = 0
        menor = 999999

        rapidos = normais = lentos = 0
        st200 = st403 = st404 = st500 = 0

        ultimo_ip = ""
        cont_ip = bots = 0
        ultimo_bot = ""

        ultimo_tempo = cont_degrad = degrad = 0
        cont500 = falha = 0

        rec_home = rec_login = rec_admin = rec_config = 0

        ip1 = "192.168.5.6"; ip1_count = ip1_err = 0
        ip2 = "192.168.5.8"; ip2_count = ip2_err = 0
        ip3 = "192.168.5.9"; ip3_count = ip3_err = 0

        for linha in arq:
            if linha == "\n":
                continue

            total += 1

            # IP
            i = 0
            while linha[i] != ']':
                i += 1
            i += 2
            ip = ""
            while linha[i] != ' ':
                ip += linha[i]
                i += 1

            # STATUS
            tracos = 0
            i = 0
            while tracos < 2:
                if linha[i] == '-': tracos += 1
                i += 1
            i += 1
            status_str = ""
            while linha[i] != ' ':
                status_str += linha[i]
                i += 1
            status = int(status_str)

            # RECURSO
            tracos = 0
            i = 0
            while tracos < 3:
                if linha[i] == '-': tracos += 1
                i += 1
            i += 1
            recurso = ""
            while linha[i] != ' ':
                recurso += linha[i]
                i += 1

            # TEMPO
            while linha[i] != '-':
                i += 1
            i += 2
            tempo_str = ""
            while linha[i] != 'm':
                tempo_str += linha[i]
                i += 1
            tempo = int(tempo_str)

            # CONTAGENS
            somaTempo += tempo
            if tempo > maior: maior = tempo
            if tempo < menor: menor = tempo

            if tempo < 200: rapidos += 1
            elif tempo < 800: normais += 1
            else: lentos += 1

            if status == 200:
                sucesso += 1; st200 += 1
            else:
                erros += 1
                if status == 403: st403 += 1
                elif status == 404: st404 += 1
                elif status == 500:
                    st500 += 1; erros500 += 1

            # RECURSOS
            if recurso == "/home": rec_home += 1
            elif recurso == "/login": rec_login += 1
            elif recurso == "/admin": rec_admin += 1
            elif recurso == "/config": rec_config += 1

            # IPs
            if ip == ip1:
                ip1_count += 1
                if status != 200: ip1_err += 1
            elif ip == ip2:
                ip2_count += 1
                if status != 200: ip2_err += 1
            elif ip == ip3:
                ip3_count += 1
                if status != 200: ip3_err += 1

            # BOT
            if ip == ultimo_ip:
                cont_ip += 1
                if cont_ip == 5:
                    bots += 1
                    ultimo_bot = ip
            else:
                cont_ip = 1
            ultimo_ip = ip

            # DEGRADAÇÃO
            if tempo > ultimo_tempo:
                cont_degrad += 1
                if cont_degrad == 3:
                    degrad += 1
            else:
                cont_degrad = 0
            ultimo_tempo = tempo

            # FALHA CRÍTICA
            if status == 500:
                cont500 += 1
                if cont500 == 3:
                    falha += 1
            else:
                cont500 = 0

        # RESULTADOS
        disponibilidade = (sucesso / total) * 100
        media = somaTempo / total

        # RECURSO MAIS ACESSADO
        mais_rec = "/home"
        maior_rec = rec_home

        if rec_login > maior_rec:
            maior_rec = rec_login; mais_rec = "/login"
        if rec_admin > maior_rec:
            maior_rec = rec_admin; mais_rec = "/admin"
        if rec_config > maior_rec:
            mais_rec = "/config"

        # IP MAIS ATIVO
        ip_ativo = ip1; maior_ip = ip1_count
        if ip2_count > maior_ip:
            maior_ip = ip2_count; ip_ativo = ip2
        if ip3_count > maior_ip:
            ip_ativo = ip3

        # IP MAIS ERROS
        ip_erro = ip1; maior_erro = ip1_err
        if ip2_err > maior_erro:
            maior_erro = ip2_err; ip_erro = ip2
        if ip3_err > maior_erro:
            ip_erro = ip3

        # ESTADO
        if falha > 0 or disponibilidade < 70:
            estado = "CRÍTICO"
        elif disponibilidade < 85 or lentos > total * 0.3:
            estado = "INSTÁVEL"
        elif disponibilidade < 95 or bots > 0:
            estado = "ATENÇÃO"
        else:
            estado = "SAUDÁVEL"

        print("\n===== RELATÓRIO FINAL =====")
        print("Total:", total)
        print("Sucesso:", sucesso)
        print("Erros:", erros)
        print("Erros críticos:", erros500)
        print("Disponibilidade:", round(disponibilidade,2))
        print("Tempo médio:", round(media,2))
        print("Maior:", maior, "| Menor:", menor)
        print("Rápidos:", rapidos, "Normais:", normais, "Lentos:", lentos)
        print("Status 200:", st200, "403:", st403, "404:", st404, "500:", st500)
        print("Recurso mais acessado:", mais_rec)
        print("IP mais ativo:", ip_ativo)
        print("IP com mais erros:", ip_erro)
        print("Bots:", bots, "| Último:", ultimo_bot)
        print("Degradação:", degrad)
        print("Falha crítica:", falha)
        print("Estado:", estado)


# ================= MENU =================

def menu():
    nome_arq = 'log.txt'
    while True:
        print("\n1-GerAR  2-ANALISAR  3-AMBOS  4-SAIR")
        op = input("Opção: ")

        if op == "1":
            try:
                qtd = int(input("Qtd: "))
                gerarArquivo(nome_arq, qtd)
            except:
                print("Erro")

        elif op == "2":
            analisarLog(nome_arq)

        elif op == "3":
            try:
                qtd = int(input("Qtd: "))
                gerarArquivo(nome_arq, qtd)
                analisarLog(nome_arq)
            except:
                print("Erro")

        elif op == "4":
            break

        else:
            print("Inválido")


if __name__ == "__main__":
    menu()    
